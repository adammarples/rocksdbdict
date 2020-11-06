import pickle
import functools

from pathlib import Path

import rocksdb


def default_opts():
    opts = rocksdb.Options()
    opts.create_if_missing = True
    opts.table_factory = rocksdb.BlockBasedTableFactory(
        filter_policy=rocksdb.BloomFilterPolicy(10),
        block_cache=rocksdb.LRUCache(2 * (1024 ** 3)),
        block_cache_compressed=rocksdb.LRUCache(500 * (1024 ** 2)))
    return opts


class RocksdbDict:
    
    def __init__(
            self,
            filepath,
            opts=None,
            read_only=False,
            encoder=functools.partial(pickle.dumps, protocol=pickle.HIGHEST_PROTOCOL),
            decoder=pickle.loads,
            **kwargs
    ):
        opts = opts or default_opts()
        try:
            filepath = filepath.as_posix()
        except AttributeError:
            pass
        self.filepath = Path(filepath)
        self.db = rocksdb.DB(filepath, opts, read_only=read_only, **kwargs)
        self.encoder = encoder
        self.decoder = decoder

    def __setitem__(self, key, value):
        byteskey, bytesvalue = self.encoder(key), self.encoder(value)
        self.db.put(byteskey, bytesvalue)

    def __getitem__(self, key):
        byteskey = self.encoder(key)
        bytesvalue = self.db.get(byteskey)
        if bytesvalue is None:
            raise KeyError(f'{key} not in {self}')
        value = self.decoder(bytesvalue)
        return value

    def get(self, *args):
        nargs = len(args)
        if nargs == 1:
            key, default = *args, None
        elif nargs == 2:
            key, default = args
        else:
            raise ValueError(f'too many args to get (expected 1 or 2, got {nargs})')
        try:
            return self[key]
        except KeyError:
            return default

    def _keys_iterator(self):
        it = self.db.iterkeys()
        it.seek_to_first()
        yield from it

    def items(self):
        for byteskey in self._keys_iterator():
            bytesvalue = self.db.get(byteskey)
            key, value = self.decoder(byteskey), self.decoder(bytesvalue)
            yield key, value

    def keys(self):
        for byteskey in self._keys_iterator():
            key = self.decoder(byteskey)
            yield key

    def values(self):
        for byteskey in self._keys_iterator():
            bytesvalue = self.db.get(byteskey)
            value = self.decoder(bytesvalue)
            yield value

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __repr__(self):
        return f'RocksdbDict<{self.filepath}>'
