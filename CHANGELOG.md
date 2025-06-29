# Change log

All notable changes to this project will be documented in this file.

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
