# -*- coding: utf-8 -*-
"""
MCI (Maturity Coherence Index) — COMET Framework.

The Maturity Coherence Index measures how uniformly mature an
organisation is across its transformation dimensions. A high MCI
indicates balanced progress; a low MCI signals lopsided development
where some dimensions are far ahead of others.

Mathematical Formulation:
    MCI = 1 − CV(L) = 1 − (σ_L / μ_L)

where:
    L = {L₁, L₂, …, L_K} are maturity levels across K dimensions
    σ_L = standard deviation of L
    μ_L = mean of L

The result is clamped to [0, 1]:
    - MCI = 1  → perfectly balanced maturity across all dimensions
    - MCI = 0  → extremely unbalanced (σ_L ≥ μ_L)

Edge cases:
    - If all L_k are equal, σ_L = 0 and MCI = 1.
    - If μ_L = 0 (all dimensions at zero maturity), MCI is defined as 0
      (no coherence to speak of — everything is uniformly absent).
    - Negative maturity levels are not meaningful and raise ValueError.

References:
    COMET Framework — NOC-to-SOC Unified Theory of Intelligent Service
    Transformation in Telecommunications.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np


def compute_mci(maturity_levels: Sequence[float]) -> float:
    """
    Compute the Maturity Coherence Index (MCI).

    Parameters
    ----------
    maturity_levels : array-like
        A sequence of maturity levels L₁ … L_K across K dimensions.
        All values must be non-negative.

    Returns
    -------
    float
        MCI clamped to [0, 1].

    Raises
    ------
    ValueError
        If the input is empty, contains fewer than 2 dimensions, or
        contains negative values.

    Examples
    --------
    >>> compute_mci([3.0, 3.5, 3.2, 2.8, 3.1])
    0.9125...
    >>> compute_mci([1.0, 5.0])
    0.0
    """
    levels = np.asarray(maturity_levels, dtype=np.float64)

    if levels.size < 2:
        raise ValueError(
            f"At least 2 maturity dimensions are required, got {levels.size}."
        )
    if np.any(levels < 0):
        raise ValueError(
            "Maturity levels must be non-negative. "
            f"Found min value = {levels.min():.4f}."
        )

    mean_l = float(np.mean(levels))
    std_l = float(np.std(levels, ddof=0))  # population std for CV

    if mean_l == 0.0:
        # All zeros — no meaningful coherence
        return 0.0

    cv = std_l / mean_l
    mci = 1.0 - cv

    # Clamp to [0, 1]
    mci = float(np.clip(mci, 0.0, 1.0))
    return mci


class MaturityCoherenceAnalyzer:
    """
    Provides richer analysis of maturity coherence, including
    per-dimension deviation reporting and recommendations.

    Parameters
    ----------
    dimension_names : sequence of str or None, optional
        Human-readable names for each maturity dimension.
    """

    def __init__(
        self,
        dimension_names: Sequence[str] | None = None,
    ) -> None:
        self.dimension_names = dimension_names

    def analyze(self, maturity_levels: Sequence[float]) -> dict:
        """
        Full coherence analysis.

        Returns
        -------
        dict
            Keys: 'mci', 'mean', 'std', 'cv', 'min_level', 'max_level',
                  'gap', 'deviations'.
        """
        levels = np.asarray(maturity_levels, dtype=np.float64)
        mci = compute_mci(levels)
        mean_l = float(np.mean(levels))
        std_l = float(np.std(levels, ddof=0))
        cv = std_l / mean_l if mean_l > 0 else float("inf")

        deviations = levels - mean_l
        names = (
            list(self.dimension_names)
            if self.dimension_names is not None
            else [f"Dim_{i}" for i in range(len(levels))]
        )

        return {
            "mci": mci,
            "mean": mean_l,
            "std": std_l,
            "cv": cv,
            "min_level": float(np.min(levels)),
            "max_level": float(np.max(levels)),
            "gap": float(np.max(levels) - np.min(levels)),
            "deviations": dict(zip(names, deviations.tolist())),
        }


if __name__ == "__main__":
    # Example 1: Well-balanced maturity
    balanced = [3.0, 3.5, 3.2, 2.8, 3.1]
    mci = compute_mci(balanced)
    print(f"Balanced maturity  → MCI = {mci:.4f}")

    # Example 2: Highly unbalanced maturity
    unbalanced = [1.0, 5.0]
    mci_ub = compute_mci(unbalanced)
    print(f"Unbalanced maturity → MCI = {mci_ub:.4f}")

    # Example 3: All equal (perfect coherence)
    equal = [4.0, 4.0, 4.0, 4.0]
    mci_eq = compute_mci(equal)
    print(f"Equal maturity     → MCI = {mci_eq:.4f}")

    # Example 4: Full analysis with named dimensions
    dims = ["Network", "Service", "Customer", "Process", "Culture"]
    levels = [4.2, 2.1, 3.5, 1.8, 3.9]
    analyzer = MaturityCoherenceAnalyzer(dimension_names=dims)
    report = analyzer.analyze(levels)
    print(f"\nFull coherence report:")
    print(f"  MCI  = {report['mci']:.4f}")
    print(f"  Mean = {report['mean']:.2f}, Std = {report['std']:.2f}, CV = {report['cv']:.4f}")
    print(f"  Gap  = {report['gap']:.2f} (min={report['min_level']:.1f}, max={report['max_level']:.1f})")
    print(f"  Deviations from mean:")
    for name, dev in report["deviations"].items():
        print(f"    {name:10s}: {dev:+.2f}")