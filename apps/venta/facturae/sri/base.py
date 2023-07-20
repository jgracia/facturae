from lxml import etree
from os import path

BASE_DIR = path.dirname(__file__)


def parse_xml(name):
    return etree.parse(path.join(BASE_DIR, name)).getroot()


def compare(name, result):
    # Parse the expected file.
    xml = parse_xml(name)

    # Stringify the root, <Envelope/> nodes of the two documents.
    expected_text = etree.tostring(xml, pretty_print=False)
    result_text = etree.tostring(result, pretty_print=False)
    # Compare the results.
    if expected_text != result_text:
        print(expected_text)
        print(result_text)
    assert expected_text == result_text
