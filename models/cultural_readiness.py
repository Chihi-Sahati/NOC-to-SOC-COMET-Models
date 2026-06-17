# -*- coding: utf-8 -*-
"""
CRC (Cultural Readiness Coefficient) — COMET Framework.

The Cultural Readiness Coefficient quantifies an organisation's
preparedness for NOC-to-SOC transformation along four cultural
dimensions. Each dimension is scored on a normalised scale (typically
[0, 1] or [0, 100]) and combined via a weighted sum.

Mathematical Formulation:
    CRC = w₁·MS + w₂·CN + w₃·ET + w₄·ES

where:
    MS = Mindset Shift score
         Measures the extent to which the workforce has adopted a
         service-centric, proactive mindset over the traditional
         reactive, infrastructure-centric mindset.
    CN = Collaboration Norms score
         Captures cross-functional collaboration quality — e.g. between
         network ops, IT, and business units.
    ET = Experimentation Tolerance score
         Reflects the organisation's willingness to experiment, fail
         fast, and iterate (DevOps / SRE culture).
    ES = Executive Sponsorship score
         Gauges visible, sustained executive support for the
         transformation programme.
    w₁ … w₄ = dimension weights summing to 1.

All dimension scores should be on the same scale (recommended: [0, 1]).
The resulting CRC inherits that scale.

References:
    COMET Framework — NOC-to-SOC Unified Theory of Intelligent Service
    Transformation in Telecommunications.
"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np


def compute_crc(
    ms: float,
    cn: float,
    et: float,
    es: float,
    weights: Optional[Sequence[float]] = None,
) -> float:
    """
    Compute the Cultural Readiness Coefficient (CRC).

    Parameters
    ----------
    ms : float
        Mindset Shift score.
    cn : float
        Collaboration Norms score.
    et : float
        Experimentation Tolerance score.
    es : float
        Executive Sponsorship score.
    weights : array-like of 4 floats or None, optional
        Weights [w₁, w₂, w₃, w₄] summing to 1.
        If None, equal weights (0.25 each) are used.

    Returns
    -------
    float
        The CRC value on the same scale as the input scores.

    Raises
    ------
    ValueError
        If any score is negative, if weights do not have length 4, or
        if weights do not sum to 1 (within tolerance).

    Examples
    --------
    >>> compute_crc(0.7, 0.5, 0.6, 0.8)
    0.65
    >>> compute_crc(70, 50, 60, 80, weights=[0.3, 0.2, 0.2, 0.3])
    66.0
    """
    scores = np.array([ms, cn, et, es], dtype=np.float64)

    if np.any(scores < 0):
        raise ValueError(
            "All cultural dimension scores must be non-negative. "
            f"Got MS={ms}, CN={cn}, ET={et}, ES={es}."
        )

    if weights is None:
        w = np.array([0.25, 0.25, 0.25, 0.25], dtype=np.float64)
    else:
        w = np.asarray(weights, dtype=np.float64)
        if w.shape != (4,):
            raise ValueError(
                f"weights must have exactly 4 elements, got {w.size}."
            )
        if abs(w.sum() - 1.0) > 1e-6:
            raise ValueError(
                f"weights must sum to 1.0, got {w.sum():.6f}."
            )

    crc = float(np.dot(w, scores))
    return crc


class CulturalReadinessModel:
    """
    Reusable model for CRC computation with named dimensions and
    diagnostic output.

    Parameters
    ----------
    weights : array-like of 4 floats or None
        Dimension weights summing to 1. Default is equal weights.
    dimension_names : array-like of 4 str or None
        Custom names for the four dimensions. Defaults to
        ["Mindset Shift", "Collaboration Norms",
         "Experimentation Tolerance", "Executive Sponsorship"].
    """

    DIMENSION_DEFAULTS = [
        "Mindset Shift",
        "Collaboration Norms",
        "Experimentation Tolerance",
        "Executive Sponsorship",
    ]

    def __init__(
        self,
        weights: Optional[Sequence[float]] = None,
        dimension_names: Optional[Sequence[str]] = None,
    ) -> None:
        self.weights = np.asarray(
            weights if weights is not None else [0.25, 0.25, 0.25, 0.25],
            dtype=np.float64,
        )
        self.dimension_names = (
            list(dimension_names)
            if dimension_names is not None
            else list(self.DIMENSION_DEFAULTS)
        )

    def compute(
        self,
        ms: float,
        cn: float,
        et: float,
        es: float,
    ) -> float:
        """Compute CRC using stored weights."""
        return compute_crc(ms, cn, et, es, weights=self.weights)

    def diagnose(
        self,
        ms: float,
        cn: float,
        et: float,
        es: float,
    ) -> dict:
        """
        Compute CRC and return per-dimension contribution analysis.

        Returns
        -------
        dict
            Keys: 'crc', 'total_weighted', 'dimension_contributions',
                  'weakest_dimension', 'strongest_dimension'.
        """
        scores = np.array([ms, cn, et, es], dtype=np.float64)
        crc = float(np.dot(self.weights, scores))
        contributions = self.weights * scores

        weakest_idx = int(np.argmin(scores))
        strongest_idx = int(np.argmax(scores))

        return {
            "crc": crc,
            "dimension_contributions": dict(
                zip(self.dimension_names, contributions.tolist())
            ),
            "weakest_dimension": self.dimension_names[weakest_idx],
            "strongest_dimension": self.dimension_names[strongest_idx],
        }


if __name__ == "__main__":
    # Example 1: Equal weights
    crc1 = compute_crc(ms=0.7, cn=0.5, et=0.6, es=0.8)
    print(f"CRC (equal weights)     = {crc1:.4f}")

    # Example 2: Custom weights (executive sponsorship weighted more)
    crc2 = compute_crc(
        ms=0.7, cn=0.5, et=0.6, es=0.8,
        weights=[0.3, 0.2, 0.2, 0.3],
    )
    print(f"CRC (custom weights)    = {crc2:.4f}")

    # Example 3: Full diagnostic with the class
    model = CulturalReadinessModel(weights=[0.3, 0.2, 0.2, 0.3])
    report = model.diagnose(0.7, 0.5, 0.6, 0.8)
    print(f"\nCultural Readiness Diagnostic:")
    print(f"  CRC = {report['crc']:.4f}")
    print(f"  Weakest  : {report['weakest_dimension']}")
    print(f"  Strongest: {report['strongest_dimension']}")
    print(f"  Contributions:")
    for dim, contrib in report["dimension_contributions"].items():
        print(f"    {dim:30s}: {contrib:.4f}")