# Change log

All notable changes to this project will be documented in this file.

## [0.3.1] UNRELEASED
### Added
- `duplicate_list` function to duplicate elements in a list.
- `loads`, `save`, `read` functions for CSV, JSON and PICKLE.
- JSONL file format support.
- `str_to_type` and `parse_to` functions to convert any argparse argument to builtin value.
- `requires_packages` decorator to avoid calling a function that requires an optional dependency.

### Modified
- `deprecated_function` decorator can be used without parenthesis.

### Fixed
- `disk_cache_decorator` typing.
- `priority` argument in `register` method of `_FunctionRegistry` class.

## [0.3.0] 2025-06-29
### Added
- `check_args_type` decorator.

### Modified
- `as_builtin` now converts `collections.Counter` instances.

### Fixed
- `as_builtin` now converts correctly `Mapping` instances.
- `register_checksum_fn` now accepts `priority` arg.

## [0.2.0] 2025-06-25
### Added
- Python 3.8 support.
- `T_BuiltinNumber` and `T_BuiltinScalar` are covariant by default.
- `SupportsLen` protocol.
- `randstr` now support a range of sizes.
- `as_builtin` function to convert object to built-in equivalent recursively.

### Modified
- `disk_cache_decorator` now supports custom saving backend fns.

## [0.1.0] 2025-06-21
### Added
- Initial modules from `pyoutil` module contained in [torchoutil](https://github.com/Labbeti/torchoutil) project.
