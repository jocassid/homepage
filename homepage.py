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
from typing import Generator

from jinja2 import \
    Environment, \
    FileSystemLoader, \
    select_autoescape

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def parse_contents(page: dict) -> Generator[dict, None, None]:
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


def mod_time(path):
    return path.stat()[ST_MTIME]


def copy_required_files(requires, output_dir):
    for required in requires:
        pieces = [p.strip() for p in required.split('->')]
        if len(pieces) > 2:
            print(f"Invalid required path {required}", file=stderr)
            continue
        if len(pieces) == 2:
            output_dir = output_dir / pieces[1]
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
        for globbed in glob(expanduser(pieces[0])):
            copy2(globbed, output_dir)


def process_input_file(input_file, output_dir):

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

        for page in data.get('pages', []):
            template = page.get('template')
            template = env.get_template(template)

            file_name = page.get('file')
            if not file_name:
                continue

            output_file = output_dir / file_name
            with open(str(output_file), 'w') as out_file:
                out_file.write(
                    template.render(
                        contents=parse_contents(page),
                    )
                )
    return True


def generate_css(homepage_dir, output_dir):
    source_file = homepage_dir / 'style.scss'
    dest_file = output_dir / 'style.css'

    if not source_file.exists():
        print(f"{source_file} not found", file=stderr)
        return

    if dest_file.exists() and mod_time(dest_file) >= mod_time(source_file):
        # destination exist and is newer than source
        return True

    sass_path = homepage_dir / 'node_modules/sass/sass.js'
    command = f"node {sass_path} {source_file} {dest_file}"
    return system(command) == 0


def copy_homepage_js(homepage_dir, output_dir):
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

    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        print(f"{output_dir} doesn't exist", file=stderr)
        exit(1)

    homepage_dir = Path(__file__).parent

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
