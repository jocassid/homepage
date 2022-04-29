#!/usr/bin/env python3

from argparse import ArgumentParser
from os import system
from os.path import exists
from pathlib import Path
from stat import ST_MTIME
from sys import exit, stderr

from jinja2 import Environment, select_autoescape, FileSystemLoader

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def parse_contents(contents):
    for item in contents:
        item_type = item.get('type')
        if not item_type:
            print("Item missing type", file=stderr)
            continue
        yield item


def mod_time(path):
    return path.stat()[ST_MTIME]


def render_html(input_file, output_dir):

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
                        contents=parse_contents(
                            page.get('contents', [])
                        ),
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


def main(args):

    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        print(f"{output_dir} doesn't exist", file=stderr)
        exit(1)

    homepage_dir = Path(__file__).parent

    render_html(args.input_file, output_dir)
    generate_css(homepage_dir, output_dir)


if __name__ == '__main__':
    arg_parser = ArgumentParser(description='Build home page')
    arg_parser.add_argument(
        'input_file',
    )
    arg_parser.add_argument(
        'output_dir',
    )
    main(arg_parser.parse_args())
