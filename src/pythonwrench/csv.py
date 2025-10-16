#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import io
from csv import DictReader, DictWriter
from io import TextIOBase
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

from pythonwrench._core import _setup_output_fpath
from pythonwrench.cast import as_builtin
from pythonwrench.collections import dict_list_to_list_dict, list_dict_to_dict_list
from pythonwrench.functools import function_alias
from pythonwrench.typing import isinstance_generic

T = TypeVar("T")

Orient = Literal["list", "dict"]


# -- Dump / Save / Serialize content to CSV --


def dump_csv(
    data: Union[Iterable[Mapping[str, Any]], Mapping[str, Iterable[Any]], Iterable],
    file: Union[str, Path, PathLike, TextIOBase, None] = None,
    /,
    *,
    overwrite: bool = True,
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
        file: File path or buffer to write serialized data.
        overwrite: If True, overwrite target filepath. defaults to True.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        header: Indicates if CSV must have header. If "auto", an header is added when a dict of list or list of dicts is passed. defaults to "auto".
        align_content: If True, center content at the middle of each row for better visualization. defaults to False.
        replace_newline_by: Replace newline character to avoid newline in CSV content. defaults to "\\n".
        \*\*csv_writer_kwds: Others optional arguments passed to CSV writer object.

    Returns:
        Dumped content as string.
    """
    content = dumps_csv(
        data,
        to_builtins=to_builtins,
        header=header,
        align_content=align_content,
        replace_newline_by=replace_newline_by,
        **csv_writer_kwds,
    )

    if isinstance(file, (str, Path, PathLike)):
        file = _setup_output_fpath(file, overwrite, make_parents)
        with open(file, "w") as opened_file:
            opened_file.write(content)
    elif isinstance(file, TextIOBase):
        file.write(content)
    elif file is None:
        pass
    else:
        msg = f"Invalid argument type {type(file)}. (expected one of str, Path, TextIOBase, None)"
        raise TypeError(msg)

    return content


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
        overwrite: If True, overwrite target filepath. defaults to True.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        header: Indicates if CSV must have header. If "auto", an header is added when a dict of list or list of dicts is passed. defaults to "auto".
        align_content: If True, center content at the middle of each row for better visualization. defaults to False.
        replace_newline_by: Replace newline character to avoid newline in CSV content. defaults to "\\n".
        \*\*csv_writer_kwds: Others optional arguments passed to CSV writer object.

    Returns:
        Dumped content as string.
    """
    with io.StringIO() as buffer:
        _serialize_csv(
            data,
            buffer,
            to_builtins=to_builtins,
            header=header,
            align_content=align_content,
            replace_newline_by=replace_newline_by,
            **csv_writer_kwds,
        )
        content = buffer.getvalue()
    return content


def save_csv(
    data: Union[Iterable[Mapping[str, Any]], Mapping[str, Iterable[Any]], Iterable],
    file: Union[str, Path, PathLike, TextIOBase],
    /,
    *,
    overwrite: bool = True,
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
        overwrite: If True, overwrite target filepath. defaults to True.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        header: Indicates if CSV must have header. If "auto", an header is added when a dict of list or list of dicts is passed. defaults to "auto".
        align_content: If True, center content at the middle of each row for better visualization. defaults to False.
        replace_newline_by: Replace newline character to avoid newline in CSV content. defaults to "\\n".
        \*\*csv_writer_kwds: Others optional arguments passed to CSV writer object.
    """
    if isinstance(file, (str, Path, PathLike)):
        file = _setup_output_fpath(file, overwrite=overwrite, make_parents=make_parents)
        file = open(file, "w")
        close = True
    elif isinstance(file, TextIOBase):
        close = False
    else:
        msg = f"Invalid argument type {type(file)}. (expected one of str, Path, PathLike, TextIOBase)"
        raise TypeError(msg)

    _serialize_csv(
        data,
        file,
        to_builtins=to_builtins,
        header=header,
        align_content=align_content,
        replace_newline_by=replace_newline_by,
        **csv_writer_kwds,
    )

    if close:
        file.close()


def _serialize_csv(
    data: Union[Iterable[Mapping[str, Any]], Mapping[str, Iterable[Any]], Iterable],
    buffer: TextIOBase,
    *,
    to_builtins: bool = False,
    header: Union[bool, Literal["auto"]] = "auto",
    align_content: bool = False,
    replace_newline_by: Optional[str] = "\\n",
    **csv_writer_kwds,
) -> None:
    if to_builtins:
        data = as_builtin(data)

    if header == "auto":
        header = isinstance_generic(
            data, (Mapping[str, Iterable], Iterable[Mapping[str, Any]])
        )

    if isinstance_generic(data, Mapping[str, Iterable]):
        data_lst = dict_list_to_list_dict(data, "same")  # type: ignore
    elif isinstance_generic(data, Iterable[Mapping[str, Any]]):
        data_lst = [dict(data_i.items()) for data_i in data]
    elif not header and isinstance_generic(data, Iterable[str]):
        data_lst = [{"0": data_i} for data_i in data]
    elif not header and isinstance_generic(data, Iterable[Iterable]):
        data_lst = [dict(zip(map(str, range(len(data_i))), data)) for data_i in data]
    elif not header and isinstance_generic(data, Iterable):
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
        fieldnames = [str(k) for k in data_lst[0].keys()]

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
    if isinstance(x, str):
        return x
    elif isinstance(x, dict):
        return {_stringify(k): _stringify(v) for k, v in x.items()}  # type: ignore
    elif isinstance(x, (list, tuple, set, frozenset)):
        return type(x)(_stringify(xi) for xi in x)
    else:
        return str(x)


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
) -> List[Dict[str, Any]]: ...


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
) -> Dict[str, List[Any]]: ...


def load_csv(
    file: Union[str, Path, TextIOBase],
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
    if isinstance(file, (str, Path, PathLike)):
        file = Path(file)
        if delimiter is None:
            delimiter = "\t" if file.suffix == ".tsv" else ","

        file = file.open("r")
        close = True
    else:
        close = False

    data = _parse_csv(
        file,
        orient=orient,
        header=header,
        comment_start=comment_start,
        strip_content=strip_content,
        delimiter=delimiter,
        **csv_reader_kwds,
    )
    if close:
        file.close()
    return data


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
    with io.StringIO(content) as buffer:
        return _parse_csv(
            buffer,
            orient=orient,
            header=header,
            comment_start=comment_start,
            strip_content=strip_content,
            delimiter=delimiter,
            **csv_reader_kwds,
        )


@function_alias(load_csv)
def read_csv(*args, **kwargs): ...


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
