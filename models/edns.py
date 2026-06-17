# -*- coding: utf-8 -*-
"""
EDNS (Expected Demand Not Served) — Equation 1 of the COMET Framework.

EDNS measures the gap between service demand and delivered service quality,
capturing the cumulative unmet demand over a given evaluation period. This
is a foundational metric in the NOC-to-SOC transformation, quantifying how
well the current service delivery apparatus meets aggregate demand.

Mathematical Formulation:
    EDNS = ∫₀ᵀ [D(t) − S(t)] · w(t) dt

where:
    D(t) = aggregate service demand function at time t
    S(t) = aggregate service delivery function at time t
    w(t) = weighting function (customer impact weight, typically 1.0)
    T   = evaluation period (upper bound of integration)

Only positive gaps (demand exceeding supply) are counted; negative gaps
(surplus capacity) do not reduce the EDNS value.

References:
    COMET Framework — NOC-to-SOC Unified Theory of Intelligent Service
    Transformation in Telecommunications.
"""

from __future__ import annotations

import numpy as np
from scipy import integrate
from typing import Callable, Optional


def compute_edns(
    demand_func: Callable[[np.ndarray], np.ndarray],
    supply_func: Callable[[np.ndarray], np.ndarray],
    t_start: float = 0.0,
    t_end: float = 12.0,
    weight_func: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    n_points: int = 1000,
) -> float:
    """
    Compute Expected Demand Not Served (EDNS) via numerical integration.

    Parameters
    ----------
    demand_func : callable
        Function D(t) returning aggregate service demand at each time step.
        Must accept and return a numpy array.
    supply_func : callable
        Function S(t) returning aggregate service delivery at each time step.
        Must accept and return a numpy array.
    t_start : float, optional
        Start time of the evaluation period. Default is 0.
    t_end : float, optional
        End time of the evaluation period. Default is 12.
    weight_func : callable or None, optional
        Weighting function w(t) for customer impact. If None, a uniform
        weight of 1.0 is applied across all time points.
    n_points : int, optional
        Number of quadrature points for numerical integration. Default is 1000.

    Returns
    -------
    float
        The EDNS value — cumulative unserved demand over [t_start, t_end].

    Raises
    ------
    ValueError
        If t_end <= t_start, if n_points < 2, or if the integrand arrays
        have inconsistent shapes.
    TypeError
        If demand_func or supply_func are not callable.

    Examples
    --------
    >>> demand = lambda t: 100 + 10 * t + 5 * np.sin(2 * np.pi * t / 12)
    >>> supply = lambda t: 80 + 8 * t + 2 * np.cos(2 * np.pi * t / 12)
    >>> edns = compute_edns(demand, supply, t_end=24)
    """
    # --- Input validation ---
    if not callable(demand_func):
        raise TypeError("demand_func must be a callable accepting a numpy array.")
    if not callable(supply_func):
        raise TypeError("supply_func must be a callable accepting a numpy array.")
    if t_end <= t_start:
        raise ValueError(f"t_end ({t_end}) must be greater than t_start ({t_start}).")
    if n_points < 2:
        raise ValueError(f"n_points must be at least 2, got {n_points}.")

    # --- Build time grid ---
    t = np.linspace(t_start, t_end, n_points)

    # --- Evaluate functions ---
    d = np.asarray(demand_func(t), dtype=np.float64)
    s = np.asarray(supply_func(t), dtype=np.float64)

    if d.shape != t.shape or s.shape != t.shape:
        raise ValueError(
            "demand_func and supply_func must return arrays of the same shape "
            f"as the input time array. Got d.shape={d.shape}, s.shape={s.shape}, "
            f"t.shape={t.shape}."
        )

    # --- Weight function ---
    if weight_func is not None:
        if not callable(weight_func):
            raise TypeError("weight_func must be a callable or None.")
        w = np.asarray(weight_func(t), dtype=np.float64)
        if w.shape != t.shape:
            raise ValueError(
                f"weight_func must return array of shape {t.shape}, "
                f"got {w.shape}."
            )
    else:
        w = np.ones_like(t)

    # --- Compute gap (only positive, i.e. unserved demand) ---
    gap = (d - s) * w
    gap = np.maximum(gap, 0.0)

    # --- Numerical integration using Simpson's rule ---
    result = integrate.simpson(y=gap, x=t)

    return float(result)


if __name__ == "__main__":
    # Example: 24-hour evaluation period with sinusoidal demand/supply
    demand = lambda t: 100 + 10 * t + 5 * np.sin(2 * np.pi * t / 12)
    supply = lambda t: 80 + 8 * t + 2 * np.cos(2 * np.pi * t / 12)

    edns = compute_edns(demand, supply, t_start=0.0, t_end=24.0)
    print(f"EDNS over 24-hour period = {edns:.2f}")

    # Example with a non-uniform weight (peak hours matter more)
    def peak_weight(t: np.ndarray) -> np.ndarray:
        """Higher weight during business hours (8–18)."""
        w = np.ones_like(t)
        w[(t >= 8) & (t <= 18)] = 1.5
        return w

    edns_weighted = compute_edns(demand, supply, t_start=0.0, t_end=24.0,
                                  weight_func=peak_weight)
    print(f"EDNS (peak-weighted)    = {edns_weighted:.2f}")

    # Example: perfect supply (EDNS should be 0)
    edns_zero = compute_edns(demand, demand, t_start=0.0, t_end=24.0)
    print(f"EDNS (perfect supply)   = {edns_zero:.2f}")