#!/usr/bin/env python

import csv
import os
from csv import DictReader, DictWriter
from io import IOBase, TextIOBase
from os import PathLike
from pathlib import Path
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    TypeVar,
    Union,
    get_args,
    overload,
)

from pythonwrench.cast import as_builtin
from pythonwrench.collections import dict_list_to_list_dict, list_dict_to_dict_list
from pythonwrench.functools import function_alias
from pythonwrench.serialization._core import (
    OnExists,
    _dump_base,
    _dumps_base,
    _load_base,
    _loads_base,
    _save_base,
)
from pythonwrench.typing import isinstance_generic

T = TypeVar("T")

Orient = Literal["list", "dict"]

__all__ = [
    "Orient",
    "dump_csv",
    "dumps_csv",
    "load_csv",
    "loads_csv",
    "read_csv",
    "save_csv",
]

# -- Dump / Save / Serialize content to CSV --


def dump_csv(
    data: Union[Iterable[Mapping[str, Any]], Mapping[str, Iterable[Any]], Iterable],
    target: Union[str, Path, PathLike, TextIOBase, None] = None,
    /,
    *,
    on_exists: Optional[OnExists] = None,
    overwrite: Optional[bool] = None,
    make_parents: bool = True,
    to_builtins: bool = False,
    header: Union[bool, Literal["auto"]] = "auto",
    align_content: bool = False,
    replace_newline_by: Optional[str] = "\\n",
    **csv_writer_kwds,
) -> str:
    r"""Dump content to CSV format into string and/or file.

    Args:
        data: Data to serialize. Can be a list of dicts, dicts of lists or list of lists.
        target: File path or buffer to write serialized data.
        on_exists: Define how target file should be treated if already exists. defaults to "overwrite".
        overwrite: (DEPRECATED: use on_exists instead) If True, overwrite target filepath. defaults to None.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        header: Indicates if CSV must have header. If "auto", an header is added when a dict of list or list of dicts is passed. defaults to "auto".
        align_content: If True, center content at the middle of each row for better visualization. defaults to False.
        replace_newline_by: Replace newline character to avoid newline in CSV content. defaults to "\\n".
        \*\*csv_writer_kwds: Others optional arguments passed to CSV writer object.

    Returns:
        Dumped content as string.
    """
    return _dump_base(
        _serialize_csv,
        "text",
        data,
        target,
        on_exists=on_exists,
        overwrite=overwrite,
        make_parents=make_parents,
        to_builtins=to_builtins,
        header=header,
        align_content=align_content,
        replace_newline_by=replace_newline_by,
        **csv_writer_kwds,
    )


def dumps_csv(
    data: Union[Iterable[Mapping[str, Any]], Mapping[str, Iterable[Any]], Iterable],
    /,
    *,
    to_builtins: bool = False,
    header: Union[bool, Literal["auto"]] = "auto",
    align_content: bool = False,
    replace_newline_by: Optional[str] = "\\n",
    **csv_writer_kwds,
) -> str:
    r"""Dump content to CSV format into string.

    Args:
        data: Data to serialize. Can be a list of dicts, dicts of lists or list of lists.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        header: Indicates if CSV must have header. If "auto", an header is added when a dict of list or list of dicts is passed. defaults to "auto".
        align_content: If True, center content at the middle of each row for better visualization. defaults to False.
        replace_newline_by: Replace newline character to avoid newline in CSV content. defaults to "\\n".
        \*\*csv_writer_kwds: Others optional arguments passed to CSV writer object.

    Returns:
        Dumped content as string.
    """
    return _dumps_base(
        _serialize_csv,
        "text",
        data,
        to_builtins=to_builtins,
        header=header,
        align_content=align_content,
        replace_newline_by=replace_newline_by,
        **csv_writer_kwds,
    )


def save_csv(
    data: Union[Iterable[Mapping[str, Any]], Mapping[str, Iterable[Any]], Iterable],
    target: Union[str, Path, PathLike, TextIOBase],
    /,
    *,
    on_exists: Optional[OnExists] = None,
    overwrite: Optional[bool] = None,
    make_parents: bool = True,
    to_builtins: bool = False,
    header: Union[bool, Literal["auto"]] = "auto",
    align_content: bool = False,
    replace_newline_by: Optional[str] = "\\n",
    **csv_writer_kwds,
) -> None:
    r"""Save content to CSV format into a file or buffer.

    Args:
        data: Data to serialize. Can be a list of dicts, dicts of lists or list of lists.
        target: File path or buffer to write serialized data.
        on_exists: Define how target file should be treated if already exists. defaults to "overwrite".
        overwrite: (DEPRECATED: use on_exists instead) If True, overwrite target filepath. defaults to None.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        header: Indicates if CSV must have header. If "auto", an header is added when a dict of list or list of dicts is passed. defaults to "auto".
        align_content: If True, center content at the middle of each row for better visualization. defaults to False.
        replace_newline_by: Replace newline character to avoid newline in CSV content. defaults to "\\n".
        \*\*csv_writer_kwds: Others optional arguments passed to CSV writer object.
    """
    return _save_base(
        _serialize_csv,
        "text",
        data,
        target,
        overwrite=overwrite,
        on_exists=on_exists,
        make_parents=make_parents,
        to_builtins=to_builtins,
        header=header,
        align_content=align_content,
        replace_newline_by=replace_newline_by,
        **csv_writer_kwds,
    )


# -- Load / Read / Parse CSV content --


@overload
def load_csv(
    file: Union[str, Path, TextIOBase],
    /,
    *,
    orient: Literal["list"] = "list",
    header: bool = True,
    comment_start: Optional[str] = None,
    strip_content: bool = False,
    # CSV reader kwargs
    delimiter: Optional[str] = None,
    **csv_reader_kwds,
) -> List[Dict[str, Any]]:
    """Load csv."""


@overload
def load_csv(
    file: Union[str, Path, TextIOBase],
    /,
    *,
    orient: Literal["dict"],
    header: bool = True,
    comment_start: Optional[str] = None,
    strip_content: bool = False,
    # CSV reader kwargs
    delimiter: Optional[str] = None,
    **csv_reader_kwds,
) -> Dict[str, List[Any]]:
    """Load csv."""


def load_csv(
    source: Union[str, Path, TextIOBase],
    /,
    *,
    orient: Orient = "list",
    header: bool = True,
    comment_start: Optional[str] = None,
    strip_content: bool = False,
    # CSV reader kwargs
    delimiter: Optional[str] = ",",
    **csv_reader_kwds,
) -> Union[List[Dict[str, Any]], Dict[str, List[Any]]]:
    r"""Load content from csv filepath.

    Args:
        orient: Orientation of the output value. Can be "list" or "dict". defaults to "list".
        header: Specify if CSV has header column. defaults to True.
        comment_start: If this string is not None and a line starts with this string, the line will be ignored. defaults to None.
        delimiter: Value delimiter. defaults to ",".
        \*\*csv_reader_kwds: Other optional csv arguments.

    Returns:
        The loaded values as dict of lists, list of dicts or list of lists.
    """
    if delimiter is None and isinstance(source, (str, Path, os.PathLike)):
        source = Path(source)
        delimiter = "\t" if source.suffix == ".tsv" else ","

    return _load_base(
        _parse_csv,
        "text",
        source,
        orient=orient,
        header=header,
        comment_start=comment_start,
        strip_content=strip_content,
        delimiter=delimiter,
        **csv_reader_kwds,
    )


@overload
def loads_csv(
    content: str,
    /,
    *,
    orient: Literal["list"] = "list",
    header: bool = True,
    comment_start: Optional[str] = None,
    strip_content: bool = False,
    # CSV reader kwargs
    delimiter: Optional[str] = ",",
    **csv_reader_kwds,
) -> List[Dict[str, Any]]: ...


@overload
def loads_csv(
    content: str,
    /,
    *,
    orient: Literal["dict"],
    header: bool = True,
    comment_start: Optional[str] = None,
    strip_content: bool = False,
    # CSV reader kwargs
    delimiter: Optional[str] = ",",
    **csv_reader_kwds,
) -> Dict[str, List[Any]]: ...


def loads_csv(
    content: str,
    /,
    *,
    orient: Orient = "list",
    header: bool = True,
    comment_start: Optional[str] = None,
    strip_content: bool = False,
    # CSV reader kwargs
    delimiter: Optional[str] = ",",
    **csv_reader_kwds,
) -> Union[List[Dict[str, Any]], Dict[str, List[Any]]]:
    """Load a CSV file from string content."""
    return _loads_base(
        _parse_csv,
        "text",
        content,
        orient=orient,
        header=header,
        comment_start=comment_start,
        strip_content=strip_content,
        delimiter=delimiter,
        **csv_reader_kwds,
    )


@function_alias(load_csv)
def read_csv(*args, **kwargs): ...


def _serialize_csv(
    data: Union[Iterable[Mapping[str, Any]], Mapping[str, Iterable[Any]], Iterable],
    buffer: IOBase,
    *,
    to_builtins: bool = False,
    header: Union[bool, Literal["auto"]] = "auto",
    align_content: bool = False,
    replace_newline_by: Optional[str] = "\\n",
    **csv_writer_kwds,
) -> None:
    """Perform the serialize csv operation."""
    if to_builtins:
        data = as_builtin(data)

    is_mapping_iterable = isinstance_generic(data, Mapping[str, Iterable])
    if is_mapping_iterable:
        is_iterable_mapping = False
    else:
        is_iterable_mapping = isinstance_generic(data, Iterable[Mapping[str, Any]])

    if header == "auto":
        header = is_mapping_iterable or is_iterable_mapping

    if is_mapping_iterable:
        data_lst = dict_list_to_list_dict(data, "same")
    elif is_iterable_mapping:
        data_lst = [dict(data_i.items()) for data_i in data]
    elif isinstance(data, str):
        msg = f"Invalid argument type {type(data)}."
        raise TypeError(msg)
    elif not header and isinstance_generic(data, Iterable[str]):
        data_lst = [{"0": data_i} for data_i in data]
    elif not header and isinstance_generic(data, Iterable[Iterable]):
        data_lst = [dict(zip(map(str, range(len(data_i))), data)) for data_i in data]
    elif not header and isinstance(data, Iterable):
        data_lst = [{"0": data_i} for data_i in data]
    else:
        msg = f"Invalid argument type {type(data)} with {header=}."
        raise TypeError(msg)
    del data

    if header:
        writer_cls = DictWriter
    else:
        writer_cls = csv.writer

    if len(data_lst) == 0:
        fieldnames = []
    else:
        fieldnames = [str(k) for k in data_lst[0]]

    if align_content:
        old_fieldnames = fieldnames
        data_lst = _stringify(data_lst)
        fieldnames = _stringify(fieldnames)
        max_num_chars = {
            k: max(max(len(data_i[k]) for data_i in data_lst), len(k)) + 1
            for k in fieldnames
        }

        fieldnames = [f"{{:^{max_num_chars[k]}s}}".format(k) for k in fieldnames]
        old_to_new_fieldnames = dict(zip(old_fieldnames, fieldnames))

        data_lst = [
            {
                old_to_new_fieldnames[k]: f"{{:^{max_num_chars[k]}s}}".format(v)
                for k, v in data_i.items()
            }
            for data_i in data_lst
        ]

    if replace_newline_by is not None:

        def _replace_newline(s):
            """Perform the replace newline operation."""
            if not isinstance(s, str):
                return s
            else:
                return s.replace("\n", replace_newline_by)

        data_lst = [
            {_replace_newline(k): _replace_newline(v) for k, v in data_i.items()}
            for data_i in data_lst
        ]

    if header:
        csv_writer_kwds["fieldnames"] = fieldnames

    writer = writer_cls(buffer, **csv_writer_kwds)
    if isinstance(writer, DictWriter):
        writer.writeheader()
        writer.writerows(data_lst)
    else:
        data_lst = [tuple(data_i.values()) for data_i in data_lst]
        writer.writerows(data_lst)


def _stringify(x: Any) -> Any:
    """Perform the stringify operation."""
    if isinstance(x, str):
        return x
    elif isinstance(x, dict):
        return {_stringify(k): _stringify(v) for k, v in x.items()}  # type: ignore
    elif isinstance(x, (list, tuple, set, frozenset)):
        return type(x)(_stringify(xi) for xi in x)
    else:
        return str(x)


def _parse_csv(
    file: TextIOBase,
    /,
    *,
    orient: Orient = "list",
    header: bool = True,
    comment_start: Optional[str] = None,
    strip_content: bool = False,
    # CSV reader kwargs
    delimiter: Optional[str] = ",",
    **csv_reader_kwds,
) -> Union[List[Dict[str, Any]], Dict[str, List[Any]]]:
    if delimiter is None:
        msg = f"Invalid argument {delimiter=}. (expected not None when {type(file)=})"
        raise ValueError(msg)

    if header:
        reader_cls = DictReader
    else:
        reader_cls = csv.reader

    reader = reader_cls(file, delimiter=delimiter, **csv_reader_kwds)
    raw_data_lst = list(reader)

    data_lst: List[Dict[str, Any]]
    if header:
        data_lst = raw_data_lst  # type: ignore
    else:
        data_lst = [
            {str(j): data_ij for j, data_ij in enumerate(data_i)}
            for data_i in raw_data_lst
        ]
    del raw_data_lst

    if comment_start is not None:
        data_lst = [
            line
            for line in data_lst
            if not next(iter(line.values())).startswith(comment_start)
        ]

    if strip_content:
        data_lst = [
            {k.strip(): v.strip() for k, v in data_i.items()} for data_i in data_lst
        ]

    if orient == "dict":
        result = list_dict_to_dict_list(data_lst, key_mode="same")  # type: ignore
    elif orient == "list":
        result = data_lst
    else:
        msg = f"Invalid argument {orient=}. (expected one of {get_args(Orient)})"
        raise ValueError(msg)

    return result  # type: ignore
