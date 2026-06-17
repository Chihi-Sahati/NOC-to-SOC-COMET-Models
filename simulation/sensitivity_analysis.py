#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMET Framework - Sensitivity Analysis
========================================
Varies key parameters (beta in SGMI, lambda in MTTR, rho in AV) across ranges
and shows impact on outputs (AV, MCI, MTTR).

Formulas:
  SGMI(beta)  = (1 - beta) * MCI + beta * (Data_Fabric + Service_Graph) / 10
  AV(rho)     = 1 - (1 - rho) * exp(-rho * MCI)
  MTTR(lambda) = MTTR_0 * exp(-lambda * DFI)

where DFI = Digital Fitness Index and lambda is the improvement coefficient.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Base parameters
# ---------------------------------------------------------------------------

DIMENSIONS = [
    "Data_Fabric", "Service_Graph", "AI_Analytics", "Closed_Loop_Auto",
    "Culture", "Org_Readiness", "Strategic_Alignment",
]

WEIGHTS = np.array([0.18, 0.16, 0.15, 0.14, 0.14, 0.12, 0.11])

# Reference operator (mid-tier) scores
REFERENCE_SCORES = np.array([2.8, 2.5, 2.3, 2.1, 2.7, 2.9, 3.0])

# MTTR baseline (minutes)
MTTR_0 = 240.0  # 4 hours for a typical mid-tier operator


def compute_mci(scores: np.ndarray) -> float:
    """Maturity Composite Index (MCI)."""
    return float(np.dot(scores, WEIGHTS))


def compute_sgmi(scores: np.ndarray, beta: float) -> float:
    """Service Graph Maturity Index parameterised by beta."""
    mci = compute_mci(scores)
    sg = (scores[0] + scores[1]) / 10.0
    return float((1.0 - beta) * mci + beta * sg)


def compute_av(mci: float, rho: float) -> float:
    """Availability parameterised by rho."""
    return float(1.0 - (1.0 - rho) * np.exp(-rho * mci))


def compute_dfi(scores: np.ndarray) -> float:
    """
    Digital Fitness Index (DFI).

    Weighted combination emphasising data-oriented dimensions.

        DFI = 0.25*Data_Fabric + 0.25*Service_Graph + 0.25*AI_Analytics
              + 0.15*Closed_Loop_Auto + 0.10*Org_Readiness
    """
    w = np.array([0.25, 0.25, 0.25, 0.15, 0.10, 0.0, 0.0])
    return float(np.dot(scores, w))


def compute_mttr(dfi: float, lam: float) -> float:
    """
    Mean Time To Recovery (MTTR).

        MTTR(lambda) = MTTR_0 * exp(-lambda * DFI)

    Higher DFI and lambda → lower MTTR.
    """
    return float(MTTR_0 * np.exp(-lam * dfi))


# ---------------------------------------------------------------------------
# Sensitivity sweeps
# ---------------------------------------------------------------------------

def sensitivity_sweep():
    """Run parameter sweeps and return arrays suitable for plotting."""

    mci_base = compute_mci(REFERENCE_SCORES)
    dfi_base = compute_dfi(REFERENCE_SCORES)

    # --- 1. beta sensitivity (affects SGMI) ---
    beta_range = np.linspace(0.0, 1.0, 51)       # 0 → 1
    sgmi_vals = np.array([compute_sgmi(REFERENCE_SCORES, b) for b in beta_range])

    # --- 2. rho sensitivity (affects AV) ---
    rho_range = np.linspace(0.1, 1.0, 51)        # 0.1 → 1.0
    av_vals = np.array([compute_av(mci_base, r) for r in rho_range])

    # --- 3. lambda sensitivity (affects MTTR) ---
    lambda_range = np.linspace(0.0, 2.0, 51)    # 0 → 2.0
    mttr_vals = np.array([compute_mttr(dfi_base, l) for l in lambda_range])

    # --- 4. DFI vs MTTR curve (vary DFI, fixed lambda=0.8) ---
    dfi_range = np.linspace(0.0, 5.0, 51)
    mttr_dfi_curve = np.array([compute_mttr(d, 0.8) for d in dfi_range])

    # --- 5. MCI sensitivity to individual dimension scores ---
    dim_sensitivity = np.zeros((7, 51))
    for dim_idx in range(7):
        score_range = np.linspace(0.0, 5.0, 51)
        for si, s in enumerate(score_range):
            temp = REFERENCE_SCORES.copy()
            temp[dim_idx] = s
            dim_sensitivity[dim_idx, si] = compute_mci(temp)

    return {
        "mci_base": mci_base,
        "dfi_base": dfi_base,
        "beta_range": beta_range,
        "sgmi_vals": sgmi_vals,
        "rho_range": rho_range,
        "av_vals": av_vals,
        "lambda_range": lambda_range,
        "mttr_vals": mttr_vals,
        "dfi_range": dfi_range,
        "mttr_dfi_curve": mttr_dfi_curve,
        "dim_sensitivity": dim_sensitivity,
        "dim_score_range": np.linspace(0.0, 5.0, 51),
    }


# ---------------------------------------------------------------------------
# Pretty-print results
# ---------------------------------------------------------------------------

def print_sensitivity(results: dict):
    print("=" * 78)
    print("  COMET Framework — Sensitivity Analysis")
    print("=" * 78)
    print()

    print(f"  Reference MCI : {results['mci_base']:.4f}")
    print(f"  Reference DFI : {results['dfi_base']:.4f}")
    print(f"  MTTR baseline : {MTTR_0:.1f} minutes")
    print()

    # --- Beta sweep ---
    print("─" * 78)
    print("  1. SGMI Sensitivity to beta")
    print("     SGMI(beta) = (1-beta)*MCI + beta*(DF+SG)/10")
    print("─" * 78)
    print(f"  {'beta':>8}  {'SGMI':>10}")
    for i in [0, 10, 20, 30, 40, 50]:
        b = results["beta_range"][i]
        sg = results["sgmi_vals"][i]
        print(f"  {b:>8.2f}  {sg:>10.4f}")
    print(f"  SGMI range: [{results['sgmi_vals'].min():.4f}, {results['sgmi_vals'].max():.4f}]")
    print()

    # --- Rho sweep ---
    print("─" * 78)
    print("  2. Availability Sensitivity to rho")
    print("     AV(rho) = 1 - (1-rho)*exp(-rho*MCI)")
    print("─" * 78)
    print(f"  {'rho':>8}  {'AV':>14}  {'AV (%)':>12}")
    for i in [0, 10, 20, 30, 40, 50]:
        r = results["rho_range"][i]
        av = results["av_vals"][i]
        print(f"  {r:>8.2f}  {av:>14.6f}  {av*100:>11.4f}%")
    print(f"  AV range: [{results['av_vals'].min()*100:.4f}%, "
          f"{results['av_vals'].max()*100:.4f}%]")
    print()

    # --- Lambda sweep ---
    print("─" * 78)
    print("  3. MTTR Sensitivity to lambda")
    print("     MTTR(lambda) = MTTR_0 * exp(-lambda * DFI)")
    print("─" * 78)
    print(f"  {'lambda':>8}  {'MTTR (min)':>12}  {'MTTR (hrs)':>12}")
    for i in [0, 10, 20, 30, 40, 50]:
        lam = results["lambda_range"][i]
        mt = results["mttr_vals"][i]
        print(f"  {lam:>8.2f}  {mt:>12.2f}  {mt/60:>12.2f}")
    print(f"  MTTR range: [{results['mttr_vals'].min():.2f}, "
          f"{results['mttr_vals'].max():.2f}] minutes")
    print()

    # --- DFI vs MTTR ---
    print("─" * 78)
    print("  4. DFI vs MTTR Relationship (lambda = 0.8)")
    print("─" * 78)
    print(f"  {'DFI':>8}  {'MTTR (min)':>12}")
    for i in [0, 10, 20, 30, 40, 50]:
        d = results["dfi_range"][i]
        mt = results["mttr_dfi_curve"][i]
        print(f"  {d:>8.2f}  {mt:>12.2f}")
    print()

    # --- MCI sensitivity to dimensions ---
    print("─" * 78)
    print("  5. MCI Sensitivity to Individual Dimensions")
    print("     (Each dimension varied 0→5 while others held at reference)")
    print("─" * 78)
    print(f"  {'Dimension':<20} {'MCI@0':>8} {'MCI@5':>8} {'Delta':>8}")
    for dim_idx, dim_name in enumerate(DIMENSIONS):
        mci_at_0 = results["dim_sensitivity"][dim_idx, 0]
        mci_at_5 = results["dim_sensitivity"][dim_idx, -1]
        delta = mci_at_5 - mci_at_0
        print(f"  {dim_name:<20} {mci_at_0:>8.4f} {mci_at_5:>8.4f} {delta:>+8.4f}")
    print()
    print("=" * 78)

    # --- Elasticity summary ---
    print()
    print("  ELASTICITY SUMMARY (partial derivative of MCI w.r.t. each dimension)")
    print("─" * 78)
    score_range = results["dim_score_range"]
    for dim_idx, dim_name in enumerate(DIMENSIONS):
        dmci = np.gradient(results["dim_sensitivity"][dim_idx], score_range)
        avg_elasticity = np.mean(dmci)
        print(f"  ∂MCI/∂{dim_name:<20} ≈ {avg_elasticity:>8.4f}")
    print("=" * 78)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    results = sensitivity_sweep()
    print_sensitivity(results)

    # Save for plot_results.py
    np.savez(
        "/home/z/my-project/COMET-Framework/simulation/sensitivity_results.npz",
        beta_range=results["beta_range"],
        sgmi_vals=results["sgmi_vals"],
        rho_range=results["rho_range"],
        av_vals=results["av_vals"],
        lambda_range=results["lambda_range"],
        mttr_vals=results["mttr_vals"],
        dfi_range=results["dfi_range"],
        mttr_dfi_curve=results["mttr_dfi_curve"],
        dim_sensitivity=results["dim_sensitivity"],
        dim_score_range=results["dim_score_range"],
    )
    print()
    print("Sensitivity results saved to simulation/sensitivity_results.npz")


if __name__ == "__main__":
    main()
