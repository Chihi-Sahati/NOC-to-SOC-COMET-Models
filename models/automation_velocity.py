# -*- coding: utf-8 -*-
"""
AV (Automation Velocity) — COMET Framework.

Automation Velocity measures the rate and effectiveness of automated
process execution within a telecom operations environment. It combines
the proportion of automated processes, the speed of execution, the
maturity of the underlying service graph, and a penalty for process
sedimentation (legacy rigidity).

Mathematical Formulation:
    AV = (N_auto / N_total) × (1 / t_avg) × SGMI^β × (1 − ρ)

where:
    N_auto  = number of fully automated processes
    N_total = total number of operational processes
    t_avg   = average cycle time per automated process (hours)
    SGMI    = Service Graph Maturity Index (from service_graph_maturity.py)
    β       = sensitivity exponent amplifying SGMI's contribution
    ρ       = Process Sedimentation Index ∈ [0, 1)
              Measures the degree to which legacy processes resist
              automation (0 = no sedimentation, approaches 1 = fully rigid).

Interpretation:
    - Higher AV indicates faster, more mature, and less encumbered
      automation.
    - ρ acts as a drag factor; at ρ = 1 the velocity drops to zero
      (full legacy lock-in).

References:
    COMET Framework — NOC-to-SOC Unified Theory of Intelligent Service
    Transformation in Telecommunications.
"""

from __future__ import annotations

from typing import Optional

import numpy as np


def compute_automation_velocity(
    n_auto: int,
    n_total: int,
    t_avg: float,
    sgmi: float,
    beta: float = 1.0,
    rho: float = 0.0,
) -> float:
    """
    Compute Automation Velocity (AV).

    Parameters
    ----------
    n_auto : int
        Number of fully automated processes. Must be ≥ 0.
    n_total : int
        Total number of operational processes. Must be > 0.
    t_avg : float
        Average cycle time (hours) per automated process execution.
        Must be > 0.
    sgmi : float
        Service Graph Maturity Index. Must be ≥ 0.
    beta : float, optional
        Sensitivity exponent for SGMI. Default is 1.0.
    rho : float, optional
        Process Sedimentation Index in [0, 1). Default is 0.0.

    Returns
    -------
    float
        The Automation Velocity value. Units: processes per hour
        (scaled by SGMI^β and sedimentation drag).

    Raises
    ------
    ValueError
        If any input constraint is violated (negative counts, zero
        denominator, rho out of range, etc.).

    Examples
    --------
    >>> av = compute_automation_velocity(60, 100, 0.5, 0.72, beta=1.2, rho=0.15)
    """
    # --- Input validation ---
    if n_auto < 0:
        raise ValueError(f"n_auto must be non-negative, got {n_auto}.")
    if n_total <= 0:
        raise ValueError(f"n_total must be positive, got {n_total}.")
    if n_auto > n_total:
        raise ValueError(
            f"n_auto ({n_auto}) cannot exceed n_total ({n_total})."
        )
    if t_avg <= 0:
        raise ValueError(f"t_avg must be positive, got {t_avg}.")
    if sgmi < 0:
        raise ValueError(f"sgmi must be non-negative, got {sgmi}.")
    if not (0.0 <= rho < 1.0):
        raise ValueError(f"rho must be in [0, 1), got {rho}.")

    automation_ratio = n_auto / n_total
    speed_factor = 1.0 / t_avg
    maturity_amplifier = sgmi ** beta
    sedimentation_drag = 1.0 - rho

    av = automation_ratio * speed_factor * maturity_amplifier * sedimentation_drag
    return float(av)


class AutomationVelocityModel:
    """
    Object-oriented wrapper for repeated AV computations with fixed
    sensitivity parameters.

    Parameters
    ----------
    beta : float, optional
        SGMI sensitivity exponent. Default is 1.0.
    rho : float, optional
        Process Sedimentation Index. Default is 0.0.
    """

    def __init__(self, beta: float = 1.0, rho: float = 0.0) -> None:
        if not (0.0 <= rho < 1.0):
            raise ValueError(f"rho must be in [0, 1), got {rho}.")
        self.beta = float(beta)
        self.rho = float(rho)

    def compute(
        self,
        n_auto: int,
        n_total: int,
        t_avg: float,
        sgmi: float,
    ) -> float:
        """
        Compute AV using the model's stored β and ρ.

        Parameters
        ----------
        n_auto : int
            Number of automated processes.
        n_total : int
            Total number of processes.
        t_avg : float
            Average cycle time (hours).
        sgmi : float
            Service Graph Maturity Index.

        Returns
        -------
        float
            Automation Velocity.
        """
        return compute_automation_velocity(
            n_auto=n_auto,
            n_total=n_total,
            t_avg=t_avg,
            sgmi=sgmi,
            beta=self.beta,
            rho=self.rho,
        )


if __name__ == "__main__":
    # Scenario: A telco with 60 automated processes out of 100,
    # average cycle time of 0.5 hours, SGMI = 0.72
    av = compute_automation_velocity(
        n_auto=60, n_total=100, t_avg=0.5,
        sgmi=0.72, beta=1.2, rho=0.15,
    )
    print(f"Automation Velocity = {av:.4f}")

    # Using the class for scenario comparison
    model = AutomationVelocityModel(beta=1.0, rho=0.10)

    print("\nAV across different SGMI values (fixed β=1.0, ρ=0.10):")
    for sgmi_val in [0.1, 0.3, 0.5, 0.7, 0.9]:
        val = model.compute(n_auto=60, n_total=100, t_avg=0.5, sgmi=sgmi_val)
        print(f"  SGMI={sgmi_val:.1f}  →  AV = {val:.4f}")

    # Sedimentation impact
    print("\nImpact of sedimentation (ρ) on AV (SGMI=0.72, β=1.2):")
    for rho_val in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9]:
        val = compute_automation_velocity(
            60, 100, 0.5, 0.72, beta=1.2, rho=rho_val,
        )
        print(f"  ρ={rho_val:.1f}  →  AV = {val:.4f}")