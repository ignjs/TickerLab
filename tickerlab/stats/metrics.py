from __future__ import annotations

import math

import numpy as np
from sklearn.metrics import brier_score_loss, roc_auc_score


def _safe_auc(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    uniq = np.unique(y_true)
    if len(uniq) < 2:
        return float("nan")
    return float(roc_auc_score(y_true, y_prob))


def compute_signal_metrics(y_true: np.ndarray, y_prob: np.ndarray, returns: np.ndarray, threshold: float = 0.5) -> dict[str, float]:
    y_pred = (y_prob >= threshold).astype(int)
    hit_rate = float((y_pred == y_true).mean())
    mean_fr = float(np.nanmean(returns))
    median_fr = float(np.nanmedian(returns))

    signal_returns = returns[y_pred == 1]
    gains = signal_returns[signal_returns > 0].sum() if signal_returns.size else 0.0
    losses = -signal_returns[signal_returns < 0].sum() if signal_returns.size else 0.0
    profit_factor = float(gains / losses) if losses > 0 else float("inf")
    sharpe = float(np.nanmean(signal_returns) / (np.nanstd(signal_returns) + 1e-8) * math.sqrt(252)) if signal_returns.size else 0.0

    equity = np.cumprod(1 + np.nan_to_num(signal_returns, nan=0.0)) if signal_returns.size else np.array([1.0])
    peak = np.maximum.accumulate(equity)
    drawdown = (equity / peak) - 1
    max_dd = float(drawdown.min()) if drawdown.size else 0.0

    sorted_idx = np.argsort(-y_prob)
    k = max(1, int(0.1 * len(y_prob)))
    top_k = y_true[sorted_idx[:k]]
    precision_k = float(np.mean(top_k)) if top_k.size else 0.0

    return {
        "hit_rate": hit_rate,
        "mean_forward_return": mean_fr,
        "median_forward_return": median_fr,
        "profit_factor": profit_factor,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "auc": _safe_auc(y_true, y_prob),
        "brier_score": float(brier_score_loss(y_true, y_prob)),
        "precision_at_k": precision_k,
    }


def stability_score(values: list[float]) -> float:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return float("nan")
    m = np.nanmean(arr)
    s = np.nanstd(arr)
    if abs(m) < 1e-9:
        return 0.0
    return float(max(0.0, 1.0 - (s / abs(m))))
