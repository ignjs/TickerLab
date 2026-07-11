from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class IngestConfig(BaseModel):
    source: Literal["csv", "synthetic"] = "synthetic"
    input_path: str | None = None
    adjusted: bool = True


class PatternConfig(BaseModel):
    pivot_window: int = 3
    top_tolerance: float = 0.01


class ValidationConfig(BaseModel):
    mode: Literal["rolling", "expanding"] = "rolling"
    n_splits: int = 5
    train_size: int = 200
    test_size: int = 50
    purge: int = 0


class AppConfig(BaseModel):
    symbol: str = "AAPL"
    timeframe: str = "1d"
    cache_dir: Path = Path("data")
    horizons: list[int] = Field(default_factory=lambda: [1, 3, 5, 10, 20, 60])
    ingest: IngestConfig = Field(default_factory=IngestConfig)
    patterns: PatternConfig = Field(default_factory=PatternConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)


def load_config(path: str | None) -> AppConfig:
    if not path:
        return AppConfig()
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return AppConfig.model_validate(raw)
