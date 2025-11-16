
pythonwrench's documentation
========================================

Set of tools for Python that could be in the standard library.

See the API doc here:

.. toctree::
   :maxdepth: 1
   :name: maintoc

   modules

Useful links:

- `GitHub repository <https://github.com/Labbeti/pythonwrench>`_
- `Pypi repository <https://pypi.org/project/pythonwrench/>`_

Key features
============================

Collections
----------------------------

Provides functions to facilitate iterables processing, like `unzip` or `flatten` :

.. :caption: Load an item.

.. code-block:: python

    import pythonwrench as pw

    list_of_tuples = [(1, "a"), (2, "b"), (3, "c"), (4, "d")]
    pw.unzip(list_of_tuples)
    [1, 2, 3, 4], ["a", "b", "c", "d"]
    pw.flatten(list_of_tuples)
    [1, "a", 2, "b", 3, "c", 4, "d"]

or mathematical functions like `prod` or `argmax` :

.. :caption: Load an item.

.. code-block:: python

    import pythonwrench as pw

    values = [3, 1, 6, 4]
    pw.prod(values)  # 72
    pw.argmax(values)  # 2
    pw.is_sorted(values)  # False

Easely converts common python structures like list of dicts to dict of lists :

.. :caption: Load an item.

.. code-block:: python

    import pythonwrench as pw

    list_of_dicts = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    pw.list_dict_to_dict_list(list_of_dicts)  # {"a": [1, 3], "b": [2, 4]}

or dict of dicts :

.. :caption: Load an item.

.. code-block:: python

    import pythonwrench as pw

    dict_of_dicts = {"a": {"x": 1, "y": 2}, "b": {"x": 3, "y": 4}}
    pw.flat_dict_of_dict(dict_of_dicts)  # {"a.x": 1, "a.y": 2, "b.x": 3, "b.y": 4}


Typing
----------------------------

Check generic types with ìsinstance_generic` :

.. :caption: Load an item.

.. code-block:: python

    import pythonwrench as pw

    # Behaves like builtin isinstance() :
    pw.isinstance_generic({"a": 1, "b": 2}, dict)  # True
    # But works with generic types !
    pw.isinstance_generic({"a": 1, "b": 2}, dict[str, int])  # True
    pw.isinstance_generic({"a": 1, "b": 2}, dict[str, str])  # False

... or check specific methods with protocols classes beginning with `Supports`

.. :caption: Load an item.

.. code-block:: python

    import pythonwrench as pw

    isinstance({"a": 1, "b": 2}, pw.SupportsIterLen)  # True
    isinstance({"a": 1, "b": 2}, pw.SupportsGetitemLen)  # True

Finally, you can also force argument type checking with `check_args_types` function :

.. :caption: Load an item.

.. code-block:: python

    import pythonwrench as pw

    @pw.check_args_types
    def f(a: int, b: str) -> str:
        return a * b

    f(1, "a")  # pass check
    f(1, 2)  # raises TypeError from decorator


Disk caching (memoize)
----------------------------

.. :caption: Load an item.

.. code-block:: python

    import pythonwrench as pw

    @pw.disk_cache_decorator
    def heavy_processing():
        # Lot of stuff here
        ...

    data1 = heavy_processing()  # first call function is called and the result is stored on disk
    data2 = heavy_processing()  # second call result is loaded from disk directly


Semantic versionning parsing
----------------------------

.. :caption: Load an item.

.. code-block:: python

    import pythonwrench as pw
    version = pw.Version("1.12.2")
    version.to_tuple()  # (1, 12, 2)
    version = pw.Version("0.5.1-beta+linux")
    version.to_tuple()  # (0, 5, 1, "beta", "linux")

    Version("1.3.1") < Version("1.4.0")  # True


Serialization
----------------------------

.. :caption: Load an item.

.. code-block:: python

    import pythonwrench as pw

    list_of_dicts = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    pw.dump_csv(list_of_dicts, "data.csv")
    pw.dump_json(list_of_dicts, "data.json")
    pw.load_json("data.json") == list_of_dicts  # True


Contact
============================

Maintainer:
- [Étienne Labbé](https://labbeti.github.io/) "Labbeti": labbeti.pub@gmail.com
