**SerialView** is a Python mapping view which serializes all key-value pairs before storing them in the given mapping object. The general use case is to use this class to wrap around a `bsddb.DB` or a `LiteMap` object (which only take string keys/values).

The provided `SerialView` classes uses `repr` for the keys and `pickle` for the values. One can easily change the serialization method by extending the class and overriding the `_(load|dump)_(key|value)` methods.

Example:

    import bsddb
    from serialview import SerialView
    db = bsddb.hashopen('path_to_db')
    view = SerialView(db)
    view['key'] = ('complex value', 1, 2, (3, 4))
    print view['key']
    # ('complex value', 1, 2, (3, 4))
