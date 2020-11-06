#### Installation
```
pip install rocksdbdict
```

Has a dependency on [rocksdb](https://github.com/facebook/rocksdb)

#### Features

Inspired by and [sqlitedict](https://pypi.org/project/sqlitedict/) and [shelve](https://docs.python.org/3/library/shelve.html) to be a replacement for sqlitedict using a faster backing database in rocksdb, which will also allow concurrent reads if read_only is set to True.

```python
# constructor
db = RocksdbDict('/path/to/db')
```

```python
# set and get items like a dict
>>> db[1] = 2
>>> db[1]
2

>>> db['a'] = 'b'
>>> db['a']
'b'

>>> db[100]
Traceback (most recent call last):
  File "<input>", line 1, in <module>
KeyError: 100

# contains
>>> 1 in db
True

# default keys
>>> db.get(100, 9999)
9999

# keys is an iterator
>>> list(db.keys())
[1, 'a']

# values is an iterator
>>> list(db.values())
[2, 'b']

# items is an iterator
>>> for k, v in db.items():
>>>     print(k, v)
1 2
a b
```

#### Encoding

Rocksdb takes bytes as keys and values so python objects are encoded as bytes, the default being to use pickle with the highest protocol, but custom encoders/decoders can be passed to the constructor

```python
db = RocksdbDict('/path/to/db', encoder=pickle.loads, decoder=pickle.dumps)

class A:
    b = 4

db['a'] = A()

>>> db['a'].b
4
```

#### Options

Default options are provided, but all kwargs are passed directly through to the rocksdb.DB() constructor

```python
import rocksdb

def default_opts():
    opts = rocksdb.Options()
    opts.create_if_missing = True
    opts.table_factory = rocksdb.BlockBasedTableFactory(
        filter_policy=rocksdb.BloomFilterPolicy(10),
        block_cache=rocksdb.LRUCache(2 * (1024 ** 3)),
        block_cache_compressed=rocksdb.LRUCache(500 * (1024 ** 2)))
    return opts
```

Options can be passed as a kwarg instead

```python
import rocksdb

opts = rocksdb.Options()
db = RocksdbDict('/path/to/db', opts=opts)
```

If read_only is set to True, multiple concurrent reads can be performed
```python
db = RocksdbDict('/path/to/db', read_only=True)
db[1] = 2

with ThreadPoolExecutor(max_workers=10) as executor:
   futures = executor.map(readonly_db.get, [1, 1, 1])

>>> list(futures)
[2, 2, 2]
```




