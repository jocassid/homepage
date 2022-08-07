
from homepage import parse_contents


def test_parse_contents():

    assert [] == list(parse_contents({}))

    contents_in = [
        {'label': 'C'},
        {'label': 'A'},
        {'label': 'B'},
    ]
    page = {'contents': contents_in}
    assert contents_in == list(parse_contents(page))

    page = {
        'contents': contents_in,
        'content_sort': ['c', 'b'],
    }
    expected_out = [
        {'label': 'C'},
        {'label': 'B'},
        {'label': 'A'},
    ]
    assert expected_out == list(parse_contents(page))

