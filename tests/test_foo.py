from types import SimpleNamespace

import pytest


def test_foo():
    assert True


def test_sorting1():
    foo = [
        SimpleNamespace(timestamp=1, preprocessed=True),
        SimpleNamespace(timestamp=2, preprocessed=True),
        SimpleNamespace(timestamp=3, preprocessed=False)
    ]

    foo.sort(key=lambda f: (f.preprocessed, f.timestamp))

    assert not foo[0].preprocessed

def test_sorting2():
    foo = [
        SimpleNamespace(timestamp=3, preprocessed=False),
        SimpleNamespace(timestamp=1, preprocessed=False),
        SimpleNamespace(timestamp=2, preprocessed=True),
    ]

    foo.sort(key=lambda f: (f.preprocessed, f.timestamp))

    assert not foo[0].preprocessed and foo[0].timestamp == 1
