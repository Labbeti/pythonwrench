# pythonwrench

<center>

<a href="https://www.python.org/">
    <img alt="Python" src="https://img.shields.io/badge/-Python 3.8+-blue?style=for-the-badge&logo=python&logoColor=white">
</a>
<a href="https://github.com/Labbeti/pythonwrench/actions">
    <img alt="Build" src="https://img.shields.io/github/actions/workflow/status/Labbeti/pythonwrench/test.yaml?branch=main&style=for-the-badge&logo=github">
</a>
<a href='https://pythonwrench.readthedocs.io/en/stable/?badge=stable'>
    <img src='https://readthedocs.org/projects/pythonwrench/badge/?version=stable&style=for-the-badge' alt='Documentation Status' />
</a>

Set of tools for Python that could be in the standard library.

</center>


## Installation

With pip:
```bash
pip install pythonwrench
```

With uv:
```bash
uv add pythonwrench
```

This library has been tested on all Python versions **3.8 - 3.13**, requires only `typing_extensions>=4.10.0`, and runs on **Linux, Mac and Windows** systems.

## Examples

### Collections

Provides functions to facilitate iterables processing, like `unzip` :

```python
>>> import pythonwrench as pw
>>>
>>> list_of_tuples = [(1, "a"), (2, "b"), (3, "c"), (4, "d")]
>>> pw.unzip(list_of_tuples)
... [1, 2, 3, 4], ["a", "b", "c", "d"]
>>> pw.flatten(list_of_tuples)
... [1, "a", 2, "b", 3, "c", 4, "d"]
```

... or mathematical functions like `prod` or `argmax` :

```python
>>> import pythonwrench as pw
>>>
>>> values = [3, 1, 6, 4]
>>> pw.prod(values)
... 72
>>> pw.argmax(values)
... 2
>>> pw.is_sorted(values)
... False
```

Easely converts common python structures like list of dicts to dict of lists :

```python
>>> import pythonwrench as pw
>>>
>>> list_of_dicts = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
>>> pw.list_dict_to_dict_list(list_of_dicts)
... {"a": [1, 3], "b": [2, 4]}
```

... or dict of dicts :
```python
>>> import pythonwrench as pw
>>>
>>> dict_of_dicts = {"a": {"x": 1, "y": 2}, "b": {"x": 3, "y": 4}}
>>> pw.flat_dict_of_dict(dict_of_dicts)
... {"a.x": 1, "a.y": 2, "b.x": 3, "b.y": 4}
```

### Typing

```python
>>> import pythonwrench as pw
>>>
>>> # Behaves like builtin isinstance() :
>>> pw.isinstance_generic({"a": 1, "b": 2}, dict)
... True
>>> # But works with generic types !
>>> pw.isinstance_generic({"a": 1, "b": 2}, dict[str, int])
... True
>>> pw.isinstance_generic({"a": 1, "b": 2}, dict[str, str])
... False
```

```python
>>> import pythonwrench as pw
>>>
>>> # Combines Iterable and Sized !
>>> isinstance({"a": 1, "b": 2}, pw.SupportsGetitemLen)
... True
>>> isinstance({"a": 1, "b": 2}, pw.SupportsIterLen)
... True
```

### Disk caching (memoize)

```python
>>> import pythonwrench as pw
>>>
>>> @pw.disk_cache_decorator
>>> def heavy_processing():
>>>     # Lot of stuff here
>>>     ...
>>>
>>> data1 = heavy_processing()  # first call function is called and the result is stored on disk
>>> data2 = heavy_processing()  # second call result is loaded from disk directly
```

### Semantic versionning parsing

```python
>>> import pythonwrench as pw
>>> version = pw.Version("1.12.2")
>>> version.to_tuple()
... (1, 12, 2)
>>> version = pw.Version("0.5.1-beta+linux")
>>> version.to_tuple()
... (0, 5, 1, "beta", "linux")
```

### Serialization

```python
>>> import pythonwrench as pw
>>>
>>> list_of_dicts = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
>>> pw.dump_csv(list_of_dicts, "data.csv")
>>> pw.dump_json(list_of_dicts, "data.json")
>>> pw.load_json("data.json") == list_of_dicts
... True
```

## Contact
Maintainer:
- [Étienne Labbé](https://labbeti.github.io/) "Labbeti": labbeti.pub@gmail.com
