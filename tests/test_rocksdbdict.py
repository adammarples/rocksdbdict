import tempfile
import shutil

from pathlib import Path

import pytest

from rocksdbdict import RocksdbDict


PATH = tempfile.gettempdir() / Path('rocksdbdict/test')


@pytest.fixture
def db():
    tempdir = tempfile.gettempdir() / Path('rocksdbdict/test')
    tempdir.mkdir(parents=True)
    _db = RocksdbDict(tempdir, read_only=False)
    for x, y in ((1, None), ('3', '4')):
        _db[x] = y
    yield _db
    shutil.rmtree(tempdir)


def test_keys(db):
    assert list(db.keys()) == [1, '3']


def test_values(db):
    assert list(db.values()) == [None, '4']


def test_items(db):
    assert list(db.items()) == [(1, None), ('3', '4')]


def test_contains(db):
    assert 1 in db
    assert 2 not in db


if __name__ == '__main__':
    pytest.main()