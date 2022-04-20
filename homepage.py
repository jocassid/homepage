#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
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


def main(args):
    print(args)

    env = Environment(
        loader=FileSystemLoader(
            Path(__file__).parent / 'templates'
        ),
        autoescape=select_autoescape(['html', 'xml'])
    )

    output_dir_path = Path(args.output_dir)
    if not output_dir_path.exists():
        print(f"{args.output_dir} doesn't exist", file=stderr)
        exit(1)

    with open(args.input_file, 'rb') as in_file:
        data = load(in_file, Loader=Loader)
        print(f"data is {data}")

    for page in data.get('pages', []):
        template = page.get('template')
        template = env.get_template(template)

        file_name = page.get('file')
        if not file_name:
            continue

        out_file_path = output_dir_path / file_name
        with open(str(out_file_path), 'w') as out_file:
            out_file.write(
                template.render(
                    contents=parse_contents(
                        page.get('contents', [])
                    ),
                )
            )


if __name__ == '__main__':
    arg_parser = ArgumentParser(description='Build home page')
    arg_parser.add_argument(
        'input_file',
    )
    arg_parser.add_argument(
        'output_dir',
    )
    main(arg_parser.parse_args())
