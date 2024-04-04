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
from typing import Any, Dict, Iterable, Iterator, List, Tuple

from jinja2 import \
    Environment, \
    FileSystemLoader, \
    select_autoescape

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class ValidationError(ValueError):
    pass


class Validator:

    def validate(self, data):
        self.validate_version(data)

    @staticmethod
    def validate_version(data):
        version = data.get('version')
        if version is None:
            return
        try:
            version = int(version)
        except (TypeError, ValueError):
            raise ValidationError('version should be an integer')
        if version < 1:
            raise ValidationError("version should be greater than zero")


def parse_contents(
        page: dict,
        page_switcher_links: Dict[str, Dict[str, str]],
) -> Iterator[dict]:

    contents = page.get('contents', [])
    content_sort = page.get('content_sort', [])
    if not content_sort:
        for item in contents:
            yield add_page_switcher_links(
                item,
                page_switcher_links,
            )
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
        yield add_page_switcher_links(item, page_switcher_links)

    for item in contents_by_label.values():
        yield add_page_switcher_links(item, page_switcher_links)


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


def add_page_switcher_links(
        content_item: dict,
        page_switcher_links: Dict[str, Dict[str, str]],
):
    item_type = content_item.get('type', '')
    if item_type != 'page switcher':
        return content_item
    content_item['links'] = page_switcher_links
    return content_item


def process_input_file(input_file: str, output_dir: Path):

    env = Environment(
        loader=FileSystemLoader(
            Path(__file__).parent / 'templates'
        ),
        autoescape=select_autoescape(['html', 'xml'])
    )

    if not exists(input_file):
        print(f"{input_file} doesn't exist", file=stderr)
        return False

    data = None
    with open(input_file, 'rb') as input_file:
        data = load(input_file, Loader=Loader)
        # print(f"data is {data}")

    if not data:
        return False

    validator = Validator()
    validator.validate(data)

    copy_required_files(data.get('requires', []), output_dir)

    site_data_type = List[Tuple[str, str, Any]]

    site_data: site_data_type = []
    for page in data.get('pages', []):
        filename = page.get('file')
        if not filename:
            continue
        title = page.get('title')
        if not title:
            continue
        site_data.append(
            (filename, title, page),
        )

    page_switcher_links = OrderedDict()
    for filename, title, _ in site_data:
        page_switcher_links[title] = {
            'label': title,
            'href': filename,
        }

    for filename, title, page in site_data:
        template = page.get('template')
        template = env.get_template(template)

        output_file = output_dir / filename
        with open(str(output_file), 'w') as out_file:
            out_file.write(
                template.render(
                    title=title,
                    contents=parse_contents(
                        page,
                        page_switcher_links,
                    ),
                )
            )
    return True


def generate_css(homepage_dir, output_dir):
    source_file = homepage_dir / 'style.css'
    dest_file = output_dir / 'style.css'

    if not source_file.exists():
        print(f"{source_file} not found", file=stderr)
        return

    if dest_file.exists() and mod_time(dest_file) >= mod_time(source_file):
        # destination exist and is newer than source
        return True

    copy2(source_file, dest_file)

    return True


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
    generate_css(homepage_dir, output_dir)
    copy_homepage_js(homepage_dir, output_dir)


if __name__ == '__main__':
    arg_parser = ArgumentParser(description='Build home page')
    arg_parser.add_argument(
        'input_file',
    )
    arg_parser.add_argument(
        'output_dir',
    )
    main(arg_parser.parse_args())
