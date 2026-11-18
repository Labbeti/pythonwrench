#!/usr/bin/env python

import os
import tempfile
import unittest
from pathlib import Path
from unittest import TestCase

from pythonwrench.csv import dump_csv, dumps_csv, loads_csv, read_csv, save_csv
from pythonwrench.json import read_json, save_json
from pythonwrench.jsonl import dumps_jsonl, loads_jsonl
from pythonwrench.pickle import (
    dump_pickle,
    dumps_pickle,
    loads_pickle,
    read_pickle,
    save_pickle,
)


class TestCSV(TestCase):
    def test_examples_1(self) -> None:
        examples = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        expected_with_header = "a,b\r\n1,2\r\n3,4\r\n"
        assert dumps_csv(examples) == expected_with_header

        expected_without_header = "1,2\r\n3,4\r\n"
        assert dumps_csv(examples, header=False) == expected_without_header

        expected_from_dumped = [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
        assert loads_csv(expected_with_header) == expected_from_dumped

    def test_examples_2(self) -> None:
        examples = [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
        tmp_dpath = Path(tempfile.gettempdir())

        tmp_fpath = tmp_dpath.joinpath("subdir", "test.csv")
        save_csv(examples, tmp_fpath, on_exists="overwrite", make_parents=True)
        result = read_csv(tmp_fpath, orient="list")

        assert examples == result
        os.remove(tmp_fpath)

    def test_examples_3(self) -> None:
        tmp_dpath = Path(tempfile.gettempdir())
        tmp_fpath = tmp_dpath / "subdir" / "test_csv_3.csv"

        data = {"a": [1, 2]}
        lineterminator = "\n"
        expected = f"a{lineterminator}1{lineterminator}2{lineterminator}"

        content = dump_csv(data, tmp_fpath, lineterminator=lineterminator)
        assert content == expected

    def test_examples_4(self) -> None:
        lineterminator = "\r\n"
        dumped = f"a{lineterminator}1{lineterminator}2{lineterminator}"
        expected = {"a": ["1", "2"]}

        data = loads_csv(dumped, lineterminator=lineterminator, orient="dict")
        assert data == expected


class TestJSON(TestCase):
    def test_example_1(self) -> None:
        tmp_fpath = Path(tempfile.gettempdir()).joinpath("test.json")
        data = {"x": [1, 2], "y": "abc", "z": None}
        save_json(data, tmp_fpath)
        result = read_json(tmp_fpath)
        assert data == result
        os.remove(tmp_fpath)


class TestJSONL(TestCase):
    def test_example_1(self) -> None:
        data = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
        content = dumps_jsonl(data)
        assert loads_jsonl(content) == data


class TestPickle(TestCase):
    def test_example_1(self) -> None:
        data = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
        dumped = dumps_pickle(data)
        result = loads_pickle(dumped)
        assert data == result

        tmpdir = Path(tempfile.gettempdir())
        tmpdir.mkdir(parents=True, exist_ok=True)
        fpath = tmpdir / "test.pickle"

        save_pickle(data, fpath)
        result = read_pickle(fpath)
        fpath.unlink()

        assert data == result

    def test_example_2(self) -> None:
        tmpdir = Path(tempfile.gettempdir())
        tmpdir.mkdir(parents=True, exist_ok=True)
        fpath = tmpdir / "test.pickle"

        data = [{"a": 10, "b": 20}, {"c": 30, "d": 40}]
        dumped = dump_pickle(data, fpath)
        assert dumped == fpath.read_bytes()
        fpath.unlink()


if __name__ == "__main__":
    unittest.main()
