from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Literal

import numpy as np
import polars as pl


@dataclass
class Fold:
    train_idx: np.ndarray
    test_idx: np.ndarray


Mode = Literal["rolling", "expanding"]


def walk_forward_indices(
    n_rows: int,
    mode: Mode = "rolling",
    train_size: int = 200,
    test_size: int = 50,
    n_splits: int = 5,
    purge: int = 0,
) -> Iterator[Fold]:
    start = train_size
    splits = 0
    while start + test_size <= n_rows and splits < n_splits:
        test_start = start + purge
        test_end = min(test_start + test_size, n_rows)
        if test_start >= test_end:
            break

        if mode == "rolling":
            train_start = max(0, start - train_size)
        else:
            train_start = 0
        train_end = start

        yield Fold(
            train_idx=np.arange(train_start, train_end, dtype=int),
            test_idx=np.arange(test_start, test_end, dtype=int),
        )
        start += test_size
        splits += 1


def split_frame(df: pl.DataFrame, **kwargs) -> list[tuple[pl.DataFrame, pl.DataFrame]]:
    out = []
    for fold in walk_forward_indices(df.height, **kwargs):
        out.append((df[fold.train_idx], df[fold.test_idx]))
    return out
