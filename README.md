# pythonwrench

<center>

<a href="https://www.python.org/">
    <img alt="Python" src="https://img.shields.io/badge/-Python 3.9+-blue?style=for-the-badge&logo=python&logoColor=white">
</a>

<!--
TODO: ruff badge ?
<a href="https://black.readthedocs.io/en/stable/">
    <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-black.svg?style=for-the-badge&labelColor=gray">
</a> -->
<a href="https://github.com/Labbeti/pythonwrench/actions">
    <img alt="Build" src="https://img.shields.io/github/actions/workflow/status/Labbeti/pythonwrench/test.yaml?branch=main&style=for-the-badge&logo=github">
</a>
<!--
TODO: readthedocs doc ?
<a href='https://pythonwrench.readthedocs.io/en/stable/?badge=stable'>
    <img src='https://readthedocs.org/projects/pythonwrench/badge/?version=stable&style=for-the-badge' alt='Documentation Status' />
</a> -->

Set of tools for Python that could be in the standard library.

</center>


## Installation
```bash
pip install pythonwrench
```

This library works on all Python versions **>=3.9**, requires only `typing_extensions`, and runs on **Linux, Mac and Windows** systems.

## Examples

### Collections

Easely converts common structures like list of dicts or dict of lists :

```python
>>> import pythonwrench as pw
>>> list_of_dicts = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
>>> pw.list_dict_to_dict_list(list_of_dicts)
... {"a": [1, 3], "b": [2, 4]}
```

### Typing

```python
>>> import pythonwrench as pw
>>> # Behaves like builtin isinstance() :
>>> pw.isinstance_generic({"a": 1, "b": 2}, dict)
... True
>>> # But works with generic types !
>>> pw.isinstance_generic({"a": 1, "b": 2}, dict[str, int])
... True
>>> pw.isinstance_generic({"a": 1, "b": 2}, dict[str, str])
... False
```

## Contact
Maintainer:
- [Étienne Labbé](https://labbeti.github.io/) "Labbeti": labbeti.pub@gmail.com
