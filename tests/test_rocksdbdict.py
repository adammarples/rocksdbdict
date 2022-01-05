import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
import rocksdb

from rocksdbdict import RocksdbDict


@pytest.fixture
def db():
    tempdir = tempfile.gettempdir() / Path("rocksdbdict/test")
    tempdir.mkdir(parents=True)
    _db = RocksdbDict(tempdir)
    for x, y in ((1, 2), ("3", "4")):
        _db[x] = y
    yield _db
    shutil.rmtree(tempdir)


@pytest.fixture
def readonly_db():
    tempdir = tempfile.gettempdir() / Path("rocksdbdict/test")
    tempdir.mkdir(parents=True)
    _db = RocksdbDict(tempdir)
    for x, y in ((1, 2), ("3", "4")):
        _db[x] = y
    _readonly_db = RocksdbDict(tempdir, read_only=True)
    yield _readonly_db
    shutil.rmtree(tempdir)


def test_keys(db):
    assert list(db.keys()) == [1, "3"]


def test_values(db):
    assert list(db.values()) == [2, "4"]


def test_items(db):
    assert list(db.items()) == [(1, 2), ("3", "4")]


def test_contains(db):
    assert 1 in db
    assert 100 not in db


def test_default_keys(db):
    result = db.get(1)
    assert result == 2
    result = db.get(1, "default")
    assert result == 2
    result = db.get(100, "default")
    assert result == "default"


def test_raises_key_error(db):
    with pytest.raises(KeyError):
        db[100]


def test_readonly_db_raises_on_write(readonly_db):
    with pytest.raises(rocksdb.errors.NotSupported):
        readonly_db["key"] = "value"


def test_readonly_db_concurrent_access(readonly_db):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = executor.map(readonly_db.get, [1] * 10)
    assert list(futures) == [2] * 10


def test_len(db):
    assert len(db) == 2


def test_delete(db):
    del db[1]
    assert 1 not in db


def test_iter(db):
    assert tuple(iter(db)) == ((1, 2), ("3", "4"))


if __name__ == "__main__":
    pytest.main()
