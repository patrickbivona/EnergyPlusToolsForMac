import pytest
import os
import eplus


@pytest.fixture
def parser():
    return eplus.IdfParser(eplus.NoddingClassDefinitions())


@pytest.fixture
def objs():
    if os.path.exists('test_file.idf'):
        os.remove('test_file.idf')

    return [
        "Version,8.0".split(','),
        "ScheduleTypeLimits,Fraction,0,1,Continuous,Dimensionless".split(',')
    ]


def test_inline_formatting(parser, objs):

    parser.write_file(objs, 'test_file.idf', eplus.InlineIdfFormatter())

    expected = """Version,8.0;
ScheduleTypeLimits,Fraction,0,1,Continuous,Dimensionless;
"""
    assertIdfFileContentEquals('test_file.idf', expected)


def test_pretty_formatting_without_comments(parser, objs):
    if os.path.exists('test_file.idf'):
        os.remove('test_file.idf')

    expected = """Version,
    8.0;

ScheduleTypeLimits,
    Fraction,
    0,
    1,
    Continuous,
    Dimensionless;

"""
    parser.write_file(objs, 'test_file.idf', eplus.PrettyIdfFormatter(False))
    assertIdfFileContentEquals('test_file.idf', expected)


def assertIdfFileContentEquals(file, expected):
    with open(file, 'r') as f:
        content = f.read()
    assert content == expected
