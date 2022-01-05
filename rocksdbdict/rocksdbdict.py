import functools
import pickle
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, Iterable, Mapping, Union

import rocksdb


def default_opts():
    opts = rocksdb.Options()
    opts.create_if_missing = True
    opts.table_factory = rocksdb.BlockBasedTableFactory(
        filter_policy=rocksdb.BloomFilterPolicy(10),
        block_cache=rocksdb.LRUCache(2 * (1024 ** 3)),
        block_cache_compressed=rocksdb.LRUCache(500 * (1024 ** 2)),
    )
    return opts


class RocksdbDict(MutableMapping):
    db: rocksdb.DB

    def __init__(
        self,
        filepath,
        opts=None,
        encoder=functools.partial(pickle.dumps, protocol=pickle.HIGHEST_PROTOCOL),
        decoder=pickle.loads,
        default_factory=None,
        **kwargs,
    ):
        opts = opts or default_opts()
        try:
            filepath = filepath.as_posix()
        except AttributeError:
            pass
        self.filepath = Path(filepath)
        self.db = rocksdb.DB(filepath, opts, **kwargs)
        self.encoder = encoder
        self.decoder = decoder
        self.default_factory = default_factory

    def update(
        self,
        __m: Union[Mapping[Any, Any], Iterable[Iterable[Any]]] = None,
        **kwargs: Any,
    ):
        """
        D.update([E, ]**F) -> None.  Update D from dict/iterable E and F.
        If E is present and has a .keys() method, then does:  for k in E: D[k] = E[k]
        If E is present and lacks a .keys() method, then does:  for k, v in E: D[k] = v
        In either case, this is followed by: for k in F:  D[k] = F[k]
        """
        batch = rocksdb.WriteBatch()
        if __m:
            try:
                for k in __m.keys():  # type: ignore
                    batch.put(self.encoder(k), self.encoder(__m[k]))  # type: ignore
            except AttributeError:
                for k, v in __m:
                    batch.put(self.encoder(k), self.encoder(v))
        for k, v in kwargs.items():
            batch.put(self.encoder(k), self.encoder(v))
        self.db.write(batch)

    def __setitem__(self, key, value):
        byteskey, bytesvalue = self.encoder(key), self.encoder(value)
        self.db.put(byteskey, bytesvalue)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(f"{key} not in {self}")
        return self.default_factory()

    def __getitem__(self, key):
        byteskey = self.encoder(key)
        bytesvalue = self.db.get(byteskey)
        if bytesvalue is None:
            return self.__missing__(key)

        value = self.decoder(bytesvalue)
        return value

    def get(self, *args):
        nargs = len(args)
        if nargs == 1:
            key, default = *args, None  # type: ignore
        elif nargs == 2:
            key, default = args
        else:
            raise ValueError(f"too many args to get (expected 1 or 2, got {nargs})")
        try:
            return self[key]
        except KeyError:
            return default

    def items(self):
        it = self.db.iteritems()
        it.seek_to_first()
        for byteskey, bytesvalue in it:
            key, value = self.decoder(byteskey), self.decoder(bytesvalue)
            yield key, value

    def keys(self):
        it = self.db.iterkeys()
        it.seek_to_first()
        for byteskey in it:
            key = self.decoder(byteskey)
            yield key

    def values(self):
        it = self.db.itervalues()
        it.seek_to_first()
        for bytesvalue in it:
            value = self.decoder(bytesvalue)
            yield value

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    __iter__ = items

    def __len__(self):
        count = 0
        it = self.db.iterkeys()
        it.seek_to_first()
        for byteskey in it:
            count += 1
        return count

    def __delitem__(self, key):
        byteskey = self.encoder(key)
        self.db.delete(byteskey)

    def __repr__(self):
        return f"RocksdbDict<{self.filepath}>"
