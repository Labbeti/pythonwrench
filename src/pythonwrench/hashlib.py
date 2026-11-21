#!/usr/bin/env python

import hashlib
import logging
from io import BufferedReader, BytesIO
from pathlib import Path
from typing import Literal, Optional, Protocol, Union, get_args, runtime_checkable

from typing_extensions import Buffer

HasherName = Literal["sha256", "md5"]
HashName = HasherName  # alias

DEFAULT_HASHER = "md5"
DEFAULT_CHUNK_SIZE = 256 * 1024**2  # 256 MiB

logger = logging.getLogger(__name__)


@runtime_checkable
class Hasher(Protocol):
    """Hasher protocol class."""

    @property
    def digest_size(self) -> int: ...
    @property
    def block_size(self) -> int: ...
    @property
    def name(self) -> str: ...

    def digest(self) -> bytes:
        """Perform the digest operation."""
        ...

    def update(self, data: Buffer, /) -> None:
        """Perform the update operation."""
        ...


def hash_str(
    x: str,
    hash_type: Union[HasherName, Hasher] = DEFAULT_HASHER,
    chunk_size: Optional[int] = DEFAULT_CHUNK_SIZE,
    *,
    init_bytes: bytes = b"",
) -> str:
    xbytes = x.encode()
    return hash_bytes(xbytes, hash_type, chunk_size, init_bytes=init_bytes)


def hash_bytes(
    x: bytes,
    hash_type: Union[HasherName, Hasher] = DEFAULT_HASHER,
    chunk_size: Optional[int] = DEFAULT_CHUNK_SIZE,
    *,
    init_bytes: bytes = b"",
) -> str:
    buffer = BytesIO(x)
    return hash_bytes_buffer(buffer, hash_type, chunk_size, init_bytes=init_bytes)


def hash_file(
    fpath: Union[str, Path, BufferedReader],
    hash_type: Union[HasherName, Hasher] = DEFAULT_HASHER,
    chunk_size: Optional[int] = DEFAULT_CHUNK_SIZE,
    *,
    init_bytes: bytes = b"",
) -> str:
    """Return the hash value for a file.

    Based on https://github.com/pytorch/audio/blob/v0.13.0/torchaudio/datasets/utils.py#L110

    Args:
        fpath: Path to existing file.
        hash_type: Hash name or custom Hasher algorithm.
        chunk_size: Max chunk size in bytes. defaults to 268435456 (256 MiB).

    Returns:
        Hash value as string.
    """
    if isinstance(fpath, (str, Path)):
        with open(fpath, "rb") as file:
            return hash_bytes_buffer(file, hash_type, chunk_size, init_bytes=init_bytes)
    else:
        return hash_bytes_buffer(fpath, hash_type, chunk_size, init_bytes=init_bytes)


def hash_bytes_buffer(
    buffer: Union[BufferedReader, BytesIO],
    hash_type: Union[HasherName, Hasher] = DEFAULT_HASHER,
    chunk_size: Optional[int] = DEFAULT_CHUNK_SIZE,
    *,
    init_bytes: bytes = b"",
) -> str:
    if isinstance(hash_type, str):
        hasher = _get_hasher(hash_type, init_bytes)
    elif isinstance(hash_type, Hasher):
        hasher = hash_type
    else:
        msg = f"Invalid argument {hash_type=}. (expected one of {get_args(HasherName)} or custom Hasher type)"
        raise TypeError(msg)
    del hash_type

    while True:
        chunk = buffer.read(chunk_size)
        if not chunk:
            break
        hasher.update(chunk)

    hash_bytes = hasher.digest()
    hash_value = hash_bytes.hex()
    return hash_value


def _get_hasher(hasher_name: HasherName, init_bytes: bytes) -> Hasher:
    if hasher_name == "sha256":
        hasher = hashlib.sha256(init_bytes)
    elif hasher_name == "md5":
        hasher = hashlib.md5(init_bytes)
    else:
        msg = (
            f"Invalid argument {hasher_name=}. (expected one of {get_args(HasherName)})"
        )
        raise ValueError(msg)
    return hasher
