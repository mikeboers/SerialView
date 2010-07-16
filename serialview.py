# encoding: utf8

import cPickle as pickle
import collections
import threading
import ast


__all__ = 'SerialView'


def _is_reprable(key):
    """Determine if the value will repr to a valid literal.
    
    We could also be checking for lists, dicts, sets, etc. in here, but I want
    to keep it only to things which are already valid keys in a mapping.
    
    """
    
    t = type(key)
    return t in (int, str, unicode) or (t is tuple and all(
        _is_reprable(x) for x in key))


class SerialView(collections.MutableMapping):
    """Serializing wrapper around a mapping.

    Values are limited to pickleable types, and mutations to stored objects
    are not reflected in the database.

    Keys may consist of strings, unicode, ints, and tuples (of these typed).
    We are using repr to serialize the key and we are assuming that it is
    deterministic.

    Because of the repr-ing, this does not have all of the same lookup
    behaviours of a normal dict. Ints and longs of the same value are not
    considered equal, nor are strings and unicode objects.

    We know this will not be deterministic across the 32/64bit platform
    boundary when using integers > 2**32. There may be other cases that we are
    not aware of.

    """
    
    def __init__(self, mapping):
        self._mapping = mapping
    
    # Overide these in child classes to change the serializing behaviour. The
    # _dump_key MUST be deterministic across any environments that you will
    # use the same mapping on.
    @staticmethod
    def _dump_key(key):
        if not _is_reprable(key):
            raise ValueError('cannot deterministically serialize key %r' % key)
        return repr(key)
    _load_key = staticmethod(lambda x: ast.literal_eval(x))
    _dump_value = staticmethod(lambda x: buffer(pickle.dumps(x, protocol=-1)))
    _load_value = staticmethod(lambda x: pickle.loads(str(x)))
    
    def __setitem__(self, key, value):
        self._mapping[self._dump_key(key)] = self._dump_value(value)

    def __getitem__(self, key):
        try:
            return self._load_value(self._mapping[self._dump_key(key)])
        except KeyError:
            raise KeyError(key)
    
    def __delitem__(self, key):
        try:
            del self._mapping[self._dump_key(key)]
        except KeyError:
            raise KeyError(key)
    
    def __iter__(self):
        for key in self._mapping:
            yield self._load_key(key)
    
    def __len__(self):
        return len(self._mapping)




def test_thread_safe():
    
    import os
    from threading import Thread
    import random
    import time
    
    path = ':memory:'
    store = RawLiteMap(path)
    
    def target():
        for i in xrange(100):
            items = [(os.urandom(5), os.urandom(10)) for j in xrange(5)]
            for k, v in items:
                store[k] = v
            for k, v in items:
                assert store[k] == v
    
    threads = [Thread(target=target) for i in xrange(5)]
    for x in threads:
        x.start()
    for x in threads:
        x.join()

    
    
if __name__ == '__main__':
    
    from time import clock as time
    # import bsddb
    import os
    
    store = LiteMap(':memory:')
    store.clear()
    
    start_time = time()
    
    store['key'] = 'whatever'
    assert store['key'] == 'whatever'
    assert 'key' in store
    assert 'not' not in store
    store[('tuple', 1)] = 'tuple_1'
    assert store[('tuple', 1)] == 'tuple_1'
    for i in range(100):
        key = os.urandom(5)
        value = os.urandom(10)
        store[key] = value
        assert store[key] == value, '%r != %r' % (repr(store[key]), value)
    
    store['a'] = 1
    assert store.setdefault('a', 2) == 1
    assert store['a'] == 1
    assert store.setdefault('b', 1) == 1
    assert store['b'] == 1
    
    print 'test duration:', time() - start_time
