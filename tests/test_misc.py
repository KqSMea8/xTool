#coding: utf-8

from __future__ import unicode_literals

import os
from datetime import timedelta
import subprocess

import pytest

from xTool import misc


def test_get_encodings():
    items = misc.get_encodings()
    items = list(items)
    assert 'utf8' in items


def test_exceptionToString():
    try:
        1/0
    except Exception:
        value = misc.exceptionToString()
        assert "ZeroDivisionError" in value


def test_ustr():
    value = "你好"
    value2 = misc.ustr(value)
    assert value == value2
    value3 = misc.ustr(value.encode('utf8'))
    assert value == value3
    value4 = misc.ustr('abc')
    assert 'abc' == value4


def test_get_cur_info():
    actual = misc.get_cur_info()
    value = ('test_get_cur_info', 35)
    assert value[0] == actual[0]


def test_runCommand():
    misc.runCommand("echo 1")


def test_getRunCommandResult():
    actual = misc.getRunCommandResult("echo 1")
    expect = (0, b'1\r\n', b'')
    assert actual == expect


def test_dumpGarbage():
    misc.dumpGarbage()


def test_listData():
    rows = [{
        'key': 'abc',
        'value': 'def',
    }]
    key = 'key'
    value = 'value'
    actual = misc.listData(rows, key, value)
    expect = {u'abc': u'def'}
    assert expect == actual


def test_ustr2unicode():
    value = "%u67E5%u8BE2%u5DE5%u4F1A%u4FE1%u606F%u63A5%u53E3"
    actual = misc.ustr2unicode(value, sep='%')
    expect = "查询工会信息接口"
    assert actual == expect
    value = "\\u67E5\\u8BE2\\u5DE5\\u4F1A\\u4FE1\\u606F\\u63A5\\u53E3"
    actual = misc.ustr2unicode(value, sep='\\')
    expect = "查询工会信息接口"
    assert actual == expect


def test_format_time():
    a = timedelta(minutes=10)
    seconds = a.total_seconds()
    actual = misc.format_time(seconds)
    expect = "0:10:00"
    assert actual == expect


def test_isMemoryAvailable():
    actual = misc.isMemoryAvailable(limit=1)
    assert actual is False
    actual = misc.isMemoryAvailable(limit=100)
    assert actual is True


def test_isDiskAvailable():
    actual = misc.isDiskAvailable(".", limit=1)
    assert actual is False
    actual = misc.isDiskAvailable(".", limit=100)
    assert actual is True


def test_formatRow():
    row = " a  b \t c "
    actual = misc.formatRow(row)
    expect = ['a', 'b', 'c']
    assert actual == expect
    row = ""
    actual = misc.formatRow(row)
    assert actual == []


def test_getColCount():
    row = " a  b \t c "
    actual = misc.getColCount(row)
    assert actual == 3
    row = ""
    actual = misc.getColCount(row)
    assert actual == 0


def test_getFileRowColCount():
    dirname = os.path.dirname(__name__)
    filePath = os.path.abspath(os.path.join(dirname, "tests/data/a.txt"))
    (row, col) = misc.getFileRowColCount(filePath)
    assert row == 2
    assert col == 3


def test_getFileRow():
    dirname = os.path.dirname(__name__)
    filePath = os.path.abspath(os.path.join(dirname, "tests/data/a.txt"))
    row = misc.getFileRow(filePath)
    assert row == 2


def test_grouper():
    n = 3
    iterable = 'abcdefg'
    actual = misc.grouper(n, iterable, padvalue=None)
    expect = [('a', 'b', 'c'), ('d', 'e', 'f'), ('g', None, None)]
    assert list(actual) == expect
    actual = misc.grouper(n, iterable, padvalue='x')
    expect = [('a', 'b', 'c'), ('d', 'e', 'f'), ('g', 'x', 'x')]
    assert list(actual) == expect


def test_chunks():
    n = 3
    iterable = 'abcdefg'
    actual = misc.chunks(iterable, n)
    assert list(actual) == [u'abc', u'def', u'g']


def test_get_random_string():
    actual = misc.get_random_string(length=12)
    assert len(actual) == 12
    actual = misc.get_random_string(length=0)
    assert actual == ''


def test_strict_bool():
    with pytest.raises(ValueError):
        misc.strict_bool(True)
    with pytest.raises(ValueError):
        misc.strict_bool(False)
    with pytest.raises(ValueError):
        misc.strict_bool(None)
    with pytest.raises(ValueError):
        misc.strict_bool("None")
    assert misc.strict_bool("True") is True
    assert misc.strict_bool("False") is False
    with pytest.raises(ValueError):
        misc.strict_bool("true") is True
    with pytest.raises(ValueError):
        misc.strict_bool("false") is True


def test_less_strict_bool():
    with pytest.raises(ValueError):
        misc.less_strict_bool('abc')
    with pytest.raises(ValueError):
        misc.less_strict_bool("true") is True
    with pytest.raises(ValueError):
        misc.less_strict_bool("false") is True
    with pytest.raises(ValueError):
        misc.less_strict_bool("None")
    assert misc.less_strict_bool("True") is True
    assert misc.less_strict_bool("False") is False
    assert misc.less_strict_bool(True) is True
    assert misc.less_strict_bool(False) is False
    assert misc.less_strict_bool(None) is False


def test_properties():
    class Foo():
         def __init__(self):
             self.var = 1
         @property
         def prop(self):
             return self.var + 1
         def meth(self):
             return self.var + 2
    foo = Foo()
    actual = misc.properties( foo )
    expect = { 'var':1, 'prop':2, 'meth':foo.meth }
    assert expect == expect


def test_get_first_duplicate():
    expectValue = 2
    actualValue = misc.get_first_duplicate([1,2,2,3])
    assert expectValue == actualValue


def test_many_to_one():
    expectValue = {'a': 1, 'b': 1, 'c': 2, 'd': 2}
    actualValue = misc.many_to_one({'ab': 1, ('c', 'd'): 2})
    assert expectValue == actualValue
