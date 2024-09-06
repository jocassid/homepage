#!/usr/bin/env python3

from argparse import ArgumentParser
from collections import OrderedDict
from glob import glob
from os import system
from os.path import exists, expanduser
from pathlib import Path
from shutil import copy2
from stat import ST_MTIME
from sys import exit, stderr
from typing import Dict, Iterator, List

from jinja2 import \
    Environment, \
    FileSystemLoader, \
    select_autoescape

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class PageSwitcherDatum:

    def __init__(
            self,
            filename: str,
            title: str,
            is_active: bool = False,
    ) -> None:
        self.filename = filename
        self.title = title
        self.is_active = is_active

    @staticmethod
    def load(page_data: dict):
        filename = page_data.get('file') or ''
        if not filename:
            raise ValueError("Missing file")

        title = page_data.get('title') or ''
        if not title:
            raise ValueError("Missing title")

        return PageSwitcherDatum(filename, title)

    def __enter__(self):
        self.is_active = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.is_active = False


def add_data_to_page_switcher(
        item: dict,
        page_switcher_data: Dict[str, PageSwitcherDatum],
):
    pass


def parse_contents(
        page: dict,
        page_switcher_data: Dict[str, PageSwitcherDatum],
) -> Iterator[dict]:
    contents = page.get('contents', [])
    content_sort = page.get('content_sort', [])
    if not content_sort:
        for item in contents:
            yield item
        return

    contents_by_label = OrderedDict()
    for item in contents:
        label = item.get('label') or item.get('title')
        if not label:
            print(f"Item missing label/title", file=stderr)
            continue
        label = label.lower()
        contents_by_label[label] = item

    for label in content_sort:
        label_lower = label.lower()
        item = contents_by_label.pop(label_lower, None)
        if not item:
            print(f"Content item {label} not found", file=stderr)
            continue
        yield item

    for item in contents_by_label.values():
        yield item


def mod_time(path: Path):
    # I found that some files copied w/ copy2 had modified times that
    # differ by factions of a second.
    return int(path.stat().st_mtime)


def copy_required_files(requires: List[str], output_dir: Path):
    for required in requires:
        pieces = [p.strip() for p in required.split('->')]
        piece_count = len(pieces)
        if piece_count > 2:
            print(f"Invalid required path {required}", file=stderr)
            continue
        # split will return a list of at least 1 piece
        if piece_count == 1:
            temp_output_dir = output_dir
        else:
            temp_output_dir = output_dir / pieces[1]
        if not temp_output_dir.exists():
            temp_output_dir.mkdir(parents=True)
        for globbed in glob(expanduser(pieces[0])):
            src_file = Path(globbed)
            dest_file = temp_output_dir / src_file.name
            if dest_file.exists():
                dest_mtime = mod_time(dest_file)
                src_mtime = mod_time(src_file)
                if dest_mtime >= src_mtime:
                    continue
            print(f"Copying {src_file} -> {dest_file}")
            copy2(src_file, dest_file)


def get_switcher_data(data: dict) -> dict:
    """
    Search through the .yaml file's data and extract a page listing
    :param data: All the data from the .yaml file.
    """
    page_switcher_data = {}
    for page in data.get('pages', []):
        try:
            page_datum = PageSwitcherDatum.load(page)
        except ValueError as error:
            print(f"Unable to load page switcher data {error}", file=stderr)
        else:
            page_switcher_data[page_datum.filename] = page_datum
    return page_switcher_data


def process_input_file(input_file: str, output_dir: Path) -> bool:
    """Process the YAML source file and render a number of HTML files"""

    env = Environment(
        loader=FileSystemLoader(
            Path(__file__).parent / 'templates'
        ),
        autoescape=select_autoescape(['html', 'xml'])
    )

    if not exists(input_file):
        print(f"{input_file} doesn't exist", file=stderr)
        return False

    with open(input_file, 'rb') as input_file:
        data = load(input_file, Loader=Loader)
        # print(f"data is {data}")

        copy_required_files(data.get('requires', []), output_dir)

        page_switcher_data: Dict[str, PageSwitcherDatum] = get_switcher_data(data)

        for page in data.get('pages', []):
            template = page.get('template')
            template = env.get_template(template)

            file_name = page.get('file')
            if not file_name:
                continue

            page['page_switcher_data'] = page_switcher_data

            page_switcher_datum = page_switcher_data[file_name]
            with page_switcher_datum:
                output_file = output_dir / file_name
                with open(str(output_file), 'w') as out_file:
                    out_file.write(
                        template.render(
                            contents=parse_contents(page, page_switcher_data),
                        )
                    )
    return True


def copy_if_newer(source_file: Path, dest_file: Path):
    if not source_file.exists():
        print(f"{source_file} not found", file=stderr)
        return False

    if dest_file.exists() and mod_time(dest_file) >= mod_time(source_file):
        # destination exist and is newer than source
        return True

    copy2(source_file, dest_file)

    return True


def copy_css(homepage_dir, stylesheet, output_dir):
    if stylesheet is None:
        stylesheet = 'default.css'

    if stylesheet.endswith('.css'):
        stylesheet_root = stylesheet[:-4]
    else:
        stylesheet_root = stylesheet
        stylesheet += '.css'

    if stylesheet == 'base.css':
        print(f"Invalid stylesheet choice", file=stderr)

    stylesheets_dir = homepage_dir / 'stylesheets'

    # always copy the non-base spreadsheet in case user specified a style
    # this time around
    copy2(
        stylesheets_dir / stylesheet,
        output_dir / 'style.css',
    )

    copy_if_newer(
        stylesheets_dir / 'base.css',
        output_dir / 'base.css',
    )

    images_src_dir = stylesheets_dir / f"{stylesheet_root}-images"
    if not images_src_dir.exists():
        return

    images_dest_dir = output_dir / 'images'
    if not images_dest_dir.exists():
        images_dest_dir.mkdir()

    for source_file in images_src_dir.iterdir():
        dest_file = images_dest_dir / source_file.name
        copy_if_newer(source_file, dest_file)


def copy_homepage_js(homepage_dir: Path, output_dir: Path):
    filename = 'homepage.js'
    src = homepage_dir / filename
    dst = output_dir / filename

    if not src.exists():
        print(f"{src} doesn't exist", file=stderr)
        exit(2)

    if dst.exists() and src.stat().st_mtime < dst.stat().st_mtime:
        return

    copy2(src, dst)


def main(args):

    output_dir: Path = Path(args.output_dir)
    if not output_dir.exists():
        print(f"{output_dir} doesn't exist", file=stderr)
        exit(1)

    homepage_dir: Path = Path(__file__).parent

    process_input_file(args.input_file, output_dir)
    copy_css(homepage_dir, args.style_sheet, output_dir)
    copy_homepage_js(homepage_dir, output_dir)


if __name__ == '__main__':
    arg_parser = ArgumentParser(description='Build home page')
    arg_parser.add_argument(
        '-s', '--style-sheet',
    )
    arg_parser.add_argument(
        'input_file',
    )
    arg_parser.add_argument(
        'output_dir',
    )
    # args_temp = arg_parser.parse_args()
    # print(args_temp)
    main(arg_parser.parse_args())
