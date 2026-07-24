#!/bin/bash
# -*- coding: utf-8 -*-

docs_dpath=`dirname $0`
cd "$docs_dpath"

if LC_ALL=C.UTF-8 locale >/dev/null 2>&1; then
    locale_name=C.UTF-8
elif LC_ALL=C.utf8 locale >/dev/null 2>&1; then
    locale_name=C.utf8
else
    locale_name=C
fi

export LANG="$locale_name"
export LC_ALL="$locale_name"

rm pythonwrench.*rst 2> /dev/null
uv run sphinx-apidoc -e -M -o . ../src/pythonwrench && uv run make clean && uv run make html

exit $?
