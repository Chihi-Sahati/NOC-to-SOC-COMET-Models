# -*- coding: utf-8 -*-
"""
MTTR(DFI) — MTTR Decay with Data Fabric Investment — COMET Framework.

This module models the exponential decay of Mean Time To Repair (MTTR)
as a function of Data Fabric Investment (DFI). As an operator invests
more in its data fabric — unified data lakes, real-time streaming,
AI/ML pipelines — the time required to diagnose and resolve service
incidents decreases.

Mathematical Formulation:
    MTTR(DFI) = MTTR₀ · exp(−λ · DFI)

where:
    MTTR₀ = baseline MTTR (hours) at zero Data Fabric Investment.
             This reflects the current-state incident resolution time.
    DFI   = Data Fabric Investment index, normalised to [0, 1].
             0 = no investment, 1 = maximum feasible investment.
    λ     = decay rate parameter (1/unit of DFI).
             Higher λ means MTTR drops faster with investment.

Properties:
    - At DFI = 0: MTTR = MTTR₀ (baseline, no improvement).
    - As DFI → 1: MTTR → MTTR₀ · exp(−λ).
    - λ > 0 guarantees monotonic decrease.
    - The half-investment point (MTTR halved) occurs at DFI = ln(2)/λ.

References:
    COMET Framework — NOC-to-SOC Unified Theory of Intelligent Service
    Transformation in Telecommunications.
"""

from __future__ import annotations

from typing import Optional

import numpy as np


def compute_mttr(
    dfi: float | np.ndarray,
    mttr_0: float,
    lam: float,
) -> float | np.ndarray:
    """
    Compute MTTR as a function of Data Fabric Investment.

    Parameters
    ----------
    dfi : float or np.ndarray
        Data Fabric Investment index, typically in [0, 1].
    mttr_0 : float
        Baseline MTTR (hours) at DFI = 0. Must be > 0.
    lam : float
        Decay rate λ. Must be > 0.

    Returns
    -------
    float or np.ndarray
        The predicted MTTR at the given DFI level(s).

    Raises
    ------
    ValueError
        If mttr_0 ≤ 0, lam ≤ 0, or if DFI values are negative.

    Examples
    --------
    >>> compute_mttr(0.5, mttr_0=4.0, lam=2.0)
    1.4715...
    """
    if mttr_0 <= 0:
        raise ValueError(f"mttr_0 must be positive, got {mttr_0}.")
    if lam <= 0:
        raise ValueError(f"lam (decay rate) must be positive, got {lam}.")

    dfi = np.asarray(dfi, dtype=np.float64)
    if np.any(dfi < 0):
        raise ValueError("DFI values must be non-negative.")

    mttr = mttr_0 * np.exp(-lam * dfi)
    if mttr.ndim == 0:
        return float(mttr)
    return mttr


class MTTRDecayModel:
    """
    Object-oriented wrapper for MTTR decay with analysis utilities.

    Parameters
    ----------
    mttr_0 : float
        Baseline MTTR in hours.
    lam : float
        Exponential decay rate.
    """

    def __init__(self, mttr_0: float, lam: float) -> None:
        if mttr_0 <= 0:
            raise ValueError(f"mttr_0 must be positive, got {mttr_0}.")
        if lam <= 0:
            raise ValueError(f"lam must be positive, got {lam}.")
        self.mttr_0 = float(mttr_0)
        self.lam = float(lam)

    def __call__(
        self, dfi: float | np.ndarray
    ) -> float | np.ndarray:
        """Evaluate MTTR at given DFI value(s)."""
        return compute_mttr(dfi, self.mttr_0, self.lam)

    def half_investment_point(self) -> float:
        """
        DFI at which MTTR is halved.

        Returns
        -------
        float
            DFI = ln(2) / λ
        """
        return float(np.log(2.0) / self.lam)

    def improvement_ratio(self, dfi: float) -> float:
        """
        Fractional improvement in MTTR at a given DFI.

        Returns
        -------
        float
            (MTTR₀ − MTTR(DFI)) / MTTR₀ ∈ [0, 1)
        """
        mttr_dfi = compute_mttr(dfi, self.mttr_0, self.lam)
        return float((self.mttr_0 - mttr_dfi) / self.mttr_0)

    def curve(
        self,
        dfi_max: float = 1.0,
        n_points: int = 100,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Generate (DFI, MTTR) arrays for plotting.

        Parameters
        ----------
        dfi_max : float
            Maximum DFI value. Default is 1.0.
        n_points : int
            Number of points. Default is 100.

        Returns
        -------
        dfi_arr : np.ndarray
        mttr_arr : np.ndarray
        """
        dfi_arr = np.linspace(0, dfi_max, n_points)
        mttr_arr = compute_mttr(dfi_arr, self.mttr_0, self.lam)
        return dfi_arr, mttr_arr


if __name__ == "__main__":
    # Example 1: A telco with 4-hour baseline MTTR, λ = 2.0
    model = MTTRDecayModel(mttr_0=4.0, lam=2.0)

    mttr_50 = model(0.5)
    print(f"MTTR at DFI=0.50 = {mttr_50:.4f} hours")

    mttr_100 = model(1.0)
    print(f"MTTR at DFI=1.00 = {mttr_100:.4f} hours")

    # Half-investment point
    half_dfi = model.half_investment_point()
    print(f"\nHalf-investment point: DFI = {half_dfi:.4f}")
    print(f"  (MTTR drops from {model.mttr_0:.1f}h to {model.mttr_0/2:.1f}h)")

    # Improvement ratio
    for dfi in [0.1, 0.25, 0.5, 0.75, 1.0]:
        ratio = model.improvement_ratio(dfi)
        print(f"  DFI={dfi:.2f}  →  {ratio*100:.1f}% MTTR reduction")

    # Curve data
    dfi_arr, mttr_arr = model.curve(dfi_max=1.0, n_points=10)
    print(f"\nCurve sample (first 5 points):")
    for d, m in zip(dfi_arr[:5], mttr_arr[:5]):
        print(f"  DFI={d:.2f}  →  MTTR={m:.4f}h")

    # Compare different decay rates
    print(f"\nComparison of decay rates (MTTR₀=4.0h, DFI=0.5):")
    for lam in [0.5, 1.0, 2.0, 3.0, 5.0]:
        val = compute_mttr(0.5, 4.0, lam)
        print(f"  λ={lam:.1f}  →  MTTR = {val:.4f}h")