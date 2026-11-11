"""Read the original MNIST IDX files, optionally compressed with gzip."""

import gzip
from pathlib import Path
import struct

import numpy as np


def read_idx(path: Path, shape: tuple[int, ...]) -> np.ndarray:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as file:
        header = file.read(4 + 4 * len(shape))
        if len(header) != 4 + 4 * len(shape):
            raise ValueError(f"{path}: truncated IDX header")
        magic, *dimensions = struct.unpack(">" + "I" * (1 + len(shape)), header)
        if magic != 0x0800 + len(shape) or tuple(dimensions) != shape:
            raise ValueError(f"{path}: invalid IDX type or dimensions {dimensions}")
        data = file.read(int(np.prod(shape)) + 1)
    if len(data) != np.prod(shape):
        raise ValueError(f"{path}: incorrect IDX payload size")
    return np.frombuffer(data, dtype=np.uint8).reshape(shape)


def load_split(folder: Path, prefix: str) -> tuple[np.ndarray, np.ndarray]:
    count = {"train": 60_000, "t10k": 10_000}[prefix]
    paths = []
    for suffix in ("images-idx3-ubyte", "labels-idx1-ubyte"):
        stem = f"{prefix}-{suffix}"
        candidates = [folder / name for name in (stem + ".gz", stem, stem.replace("-idx", ".idx"))]
        path = next((path for path in candidates if path.is_file()), None)
        if path is None:
            raise FileNotFoundError(f"Missing IDX file {stem} in {folder}")
        paths.append(path)

    images = read_idx(paths[0], (count, 28, 28)).astype(np.float32) / 255.0
    labels = read_idx(paths[1], (count,))
    if np.any(labels > 9):
        raise ValueError(f"{paths[1]}: labels must be between 0 and 9")
    return images, labels


def one_hot(labels: np.ndarray) -> np.ndarray:
    return np.eye(10, dtype=np.float32)[labels]
