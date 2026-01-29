# Change log

All notable changes to this project will be documented in this file.

## [0.4.7] UNRELEASED
### Modified
- Disk cache functions now detect saving backend when custom load/dump functions are provided.

### Fixed
- `Callable` in `isinstance_generic` check.

## [0.4.6] 2026-01-09
### Added
- `cache_fname_fmt` can now be a custom callable formatter.

## [0.4.5] 2026-01-09
### Fixed
- Documentation build with constraint `sphinx<9.0.0`.

## [0.4.4] 2026-01-09
### Added
- `SizedGenerator` class wrapper.
- `executor_kwds` argument to `ThreadPoolExecutorHelper` class.
- `cache_fname_fmt` argument in `disk_cache` now supports inputs arguments values to name the cache file.

## [0.4.3] 2025-12-13
### Added
- `as_builtin` now supports `datetime.date` instances.
- `check_only_first` argument in `isinstance_generic` function.
- `filter_with_patterns` function.
- `skipfiles`, `include` and `sort` to `tree_iter` function.
- `SupportsGetitem` protocols now has `T_Index` typevar set to `Any` instead of `int` by default.
- `SupportsGetitem2`, `SupportsGetitemLen2` and `SupportsGetitemIterLen2` protocols with generic parameters in reversed order to match `Mapping[key, value]` order.
- `ThreadPoolExecutorHelper` class.
- `SupportsMatmul` typing class.
- `reduce_matmul` function.

## [0.4.2] 2025-10-16
### Fixed
- `get_argnames` and `filter_and_call` functions when argument `fn` contains arguments with default values.

## [0.4.1] 2025-09-11
### Added
- `SupportsGetitem` protocol.
- All `SupportGetitem`-based protocols now accept a second generic to specify idx type.
- `seed` option to `randstr` function.

### Modified
- `checksum_any` computation with `set` and `frozenset` objects no longer require to sort elements.

### Fixed
- Default value for `T_Index` typevar for protocol that specify `__getitem__` method.
- `reload_editable_submodules` when no editable submodule is imported.

## [0.4.0] 2025-07-18
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
- `get_argnames` returns when function contains local variables.

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
