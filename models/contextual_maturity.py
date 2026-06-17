# -*- coding: utf-8 -*-
"""
CMF (Contextual Maturity Factor) — COMET Framework.

The Contextual Maturity Factor captures external and environmental
influences on a telecom operator's readiness for NOC-to-SOC
transformation. Unlike internal metrics (CRC, MCI), CMF reflects
market and regulatory conditions that enable or constrain progress.

Mathematical Formulation:
    CMF = β₁·CI + β₂·RE + β₃·CP + β₄·DG

where:
    CI = Competitive Intensity
         How aggressively competitors are pursuing similar transformations.
         Higher CI means greater urgency to transform.
    RE = Regulatory Enablement
         Degree to which the regulatory environment supports (or
         impedes) data-driven, automated operations.
    CP = Customer Sophistication
         Extent to which customers demand intelligent, self-service
         capabilities (pushing the operator toward SOC).
    DG = Digital Ecosystem Gap
         Current gap between the operator's digital ecosystem maturity
         and best-in-class benchmarks. Higher DG means more room (and
         need) for improvement.
    β₁ … β₄ = contextual weights summing to 1.

All inputs are typically normalised to [0, 1].

References:
    COMET Framework — NOC-to-SOC Unified Theory of Intelligent Service
    Transformation in Telecommunications.
"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np


def compute_cmf(
    ci: float,
    re: float,
    cp: float,
    dg: float,
    betas: Optional[Sequence[float]] = None,
) -> float:
    """
    Compute the Contextual Maturity Factor (CMF).

    Parameters
    ----------
    ci : float
        Competitive Intensity score (normalised, typically [0, 1]).
    re : float
        Regulatory Enablement score.
    cp : float
        Customer Sophistication score.
    dg : float
        Digital Ecosystem Gap score.
    betas : array-like of 4 floats or None, optional
        Contextual weights [β₁, β₂, β₃, β₄] summing to 1.
        If None, equal weights (0.25 each) are used.

    Returns
    -------
    float
        The CMF value on the same scale as the input scores.

    Raises
    ------
    ValueError
        If any score is negative, if betas do not have length 4, or
        if betas do not sum to 1 (within tolerance).

    Examples
    --------
    >>> compute_cmf(0.6, 0.4, 0.7, 0.5)
    0.55
    """
    scores = np.array([ci, re, cp, dg], dtype=np.float64)

    if np.any(scores < 0):
        raise ValueError(
            "All contextual scores must be non-negative. "
            f"Got CI={ci}, RE={re}, CP={cp}, DG={dg}."
        )

    if betas is None:
        b = np.array([0.25, 0.25, 0.25, 0.25], dtype=np.float64)
    else:
        b = np.asarray(betas, dtype=np.float64)
        if b.shape != (4,):
            raise ValueError(
                f"betas must have exactly 4 elements, got {b.size}."
            )
        if abs(b.sum() - 1.0) > 1e-6:
            raise ValueError(
                f"betas must sum to 1.0, got {b.sum():.6f}."
            )

    cmf = float(np.dot(b, scores))
    return cmf


class ContextualMaturityModel:
    """
    Reusable model for CMF computation with scenario analysis.

    Parameters
    ----------
    betas : array-like of 4 floats or None
        Contextual weights. Default is equal weights.
    dimension_names : array-like of 4 str or None
        Custom names. Defaults to the standard four dimensions.
    """

    DIMENSION_DEFAULTS = [
        "Competitive Intensity",
        "Regulatory Enablement",
        "Customer Sophistication",
        "Digital Ecosystem Gap",
    ]

    def __init__(
        self,
        betas: Optional[Sequence[float]] = None,
        dimension_names: Optional[Sequence[str]] = None,
    ) -> None:
        self.betas = np.asarray(
            betas if betas is not None else [0.25, 0.25, 0.25, 0.25],
            dtype=np.float64,
        )
        self.dimension_names = (
            list(dimension_names)
            if dimension_names is not None
            else list(self.DIMENSION_DEFAULTS)
        )

    def compute(
        self,
        ci: float,
        re: float,
        cp: float,
        dg: float,
    ) -> float:
        """Compute CMF using stored betas."""
        return compute_cmf(ci, re, cp, dg, betas=self.betas)

    def scenario_analysis(
        self,
        base_scores: Sequence[float],
        perturbations: list[dict],
    ) -> list[dict]:
        """
        Run scenario analysis by perturbing base scores.

        Parameters
        ----------
        base_scores : array-like of 4 floats
            Baseline [CI, RE, CP, DG].
        perturbations : list of dict
            Each dict has 'name' (str) and 'deltas' (array-like of 4
            floats) — changes to apply to the base scores.

        Returns
        -------
        list of dict
            Each with 'name', 'cmf', 'scores' keys.
        """
        base = np.asarray(base_scores, dtype=np.float64)
        if base.shape != (4,):
            raise ValueError("base_scores must have exactly 4 elements.")

        results = []
        for p in perturbations:
            deltas = np.asarray(p["deltas"], dtype=np.float64)
            scores = base + deltas
            scores = np.clip(scores, 0.0, None)  # no negative scores
            cmf = float(np.dot(self.betas, scores))
            results.append({
                "name": p["name"],
                "cmf": cmf,
                "scores": scores.tolist(),
            })

        # Include baseline
        base_cmf = float(np.dot(self.betas, base))
        results.insert(0, {
            "name": "Baseline",
            "cmf": base_cmf,
            "scores": base.tolist(),
        })
        return results


if __name__ == "__main__":
    # Example 1: Equal weights
    cmf1 = compute_cmf(ci=0.6, re=0.4, cp=0.7, dg=0.5)
    print(f"CMF (equal weights)     = {cmf1:.4f}")

    # Example 2: Custom weights
    cmf2 = compute_cmf(
        ci=0.6, re=0.4, cp=0.7, dg=0.5,
        betas=[0.3, 0.15, 0.35, 0.2],
    )
    print(f"CMF (custom weights)    = {cmf2:.4f}")

    # Example 3: Scenario analysis
    model = ContextualMaturityModel(betas=[0.3, 0.15, 0.35, 0.2])
    scenarios = model.scenario_analysis(
        base_scores=[0.6, 0.4, 0.7, 0.5],
        perturbations=[
            {"name": "Regulation Boost", "deltas": [0.0, 0.3, 0.0, 0.0]},
            {"name": "Competitive Surge", "deltas": [0.2, 0.0, 0.1, 0.0]},
            {"name": "Ecosystem Catch-up", "deltas": [0.0, 0.0, 0.0, -0.3]},
        ],
    )
    print(f"\nScenario Analysis:")
    for s in scenarios:
        print(
            f"  {s['name']:22s}: CMF = {s['cmf']:.4f}  "
            f"(CI={s['scores'][0]:.1f}, RE={s['scores'][1]:.1f}, "
            f"CP={s['scores'][2]:.1f}, DG={s['scores'][3]:.1f})"
        )