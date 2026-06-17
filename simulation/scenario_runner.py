#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMET Framework - Scenario Runner
=================================
Simulates maturity progression for 3 telecom operator types using a Markov chain
model. Computes all COMET indicators: MCI, SGMI, AV, CRC, CMF, TS.

Operator types:
  - Advanced (e.g., HKT/Orange):   high scores (3.5-4.5), high CRC, high CMF
  - Mid-tier:                      medium scores (2.0-3.5), medium CRC, CMF
  - Lagging:                       low scores (1.0-2.5), low CRC, CMF

Dimensions (7 maturity dimensions, scored 0-5):
  Data_Fabric, Service_Graph, AI_Analytics, Closed_Loop_Auto,
  Culture, Org_Readiness, Strategic_Alignment
"""

import numpy as np

# ---------------------------------------------------------------------------
# COMET Indicator Formulas
# ---------------------------------------------------------------------------

DIMENSIONS = [
    "Data_Fabric", "Service_Graph", "AI_Analytics", "Closed_Loop_Auto",
    "Culture", "Org_Readiness", "Strategic_Alignment",
]

# Dimension weights – sum to 1.0
WEIGHTS = np.array([0.18, 0.16, 0.15, 0.14, 0.14, 0.12, 0.11])


def compute_mci(scores: np.ndarray) -> float:
    """Maturity Composite Index (MCI): weighted average of 7 dimensions."""
    return float(np.dot(scores, WEIGHTS))


def compute_sgmi(scores: np.ndarray, beta: float = 0.4) -> float:
    """
    Service Graph Maturity Index (SGMI).

        SGMI = (1 - beta) * MCI + beta * (Data_Fabric + Service_Graph) / 10

    beta controls the weighting toward data/service-graph dimensions.
    """
    mci = compute_mci(scores)
    sg_component = (scores[0] + scores[1]) / 10.0  # Data_Fabric + Service_Graph
    return float((1 - beta) * mci + beta * sg_component)


def compute_av(mci: float, rho: float = 0.6) -> float:
    """
    Availability (AV): maps MCI to a 99.0% – 99.999% range.

        AV = 1 - (1 - rho) * exp(-rho * MCI)

    Returns availability as a fraction (e.g., 0.9999).
    """
    return float(1.0 - (1.0 - rho) * np.exp(-rho * mci))


def compute_crc(scores: np.ndarray) -> float:
    """
    Cognitive Readiness Coefficient (CRC).

    Combines AI_Analytics, Culture, and Org_Readiness with emphasis on
    the cultural dimension.

        CRC = 0.35 * AI_Analytics/5 + 0.35 * Culture/5 + 0.30 * Org_Readiness/5
    """
    ai = scores[2] / 5.0
    cul = scores[4] / 5.0
    org = scores[5] / 5.0
    return float(0.35 * ai + 0.35 * cul + 0.30 * org)


def compute_cmf(scores_prev: np.ndarray, scores_curr: np.ndarray) -> float:
    """
    Change Momentum Factor (CMF).

        CMF = mean(score_curr - score_prev) / max_possible_delta

    max_possible_delta = 5 (full range per dimension). Clamped to [0, 1].
    """
    delta = np.mean(scores_curr - scores_prev)
    cmf = max(0.0, min(1.0, delta / 5.0))
    return float(cmf)


def compute_ts(mci: float, sgmi: float, av: float, crc: float, cmf: float) -> float:
    """
    Transformation Score (TS).

        TS = 0.25*MCI + 0.20*SGMI + 0.20*AV + 0.20*CRC + 0.15*CMF

    All inputs normalised to [0, 1] before weighting.
    """
    mci_n = mci / 5.0
    sgmi_n = sgmi / 5.0
    av_n = av  # already in [0,1]
    cmf_n = cmf  # already in [0,1]
    crc_n = crc  # already in [0,1]
    return float(
        0.25 * mci_n + 0.20 * sgmi_n + 0.20 * av_n + 0.20 * crc_n + 0.15 * cmf_n
    )


# ---------------------------------------------------------------------------
# Markov Chain Maturity Model
# ---------------------------------------------------------------------------

def build_transition_matrix(crc: float, cmf: float) -> np.ndarray:
    """
    Build a 6-state (levels 0-5) transition probability matrix.

    CRC and CMF influence the probability of advancing to the next maturity
    level. Higher CRC → stronger propensity to advance; higher CMF → recent
    momentum is maintained.

    Returns a (6, 6) row-stochastic matrix where P[i][j] = Prob(state i → j).
    """
    P = np.zeros((6, 6))
    advance_prob = 0.15 * (crc + cmf) / 2.0  # 0 to 0.15 base
    retreat_prob = 0.03 * (1.0 - crc)        # 0 to 0.03

    for level in range(6):
        if level == 0:
            # Can only stay or advance
            P[level, 0] = 1.0 - advance_prob
            P[level, 1] = advance_prob
        elif level == 5:
            # Can only stay or retreat
            P[level, 5] = 1.0 - retreat_prob
            P[level, 4] = retreat_prob
        else:
            P[level, level] = 1.0 - advance_prob - retreat_prob
            P[level, level + 1] = advance_prob
            P[level, level - 1] = retreat_prob
            # Clamp to avoid numerical negativity
            P[level, level] = max(P[level, level], 0.0)
            # Normalise row
            P[level] = P[level] / P[level].sum()

    return P


def simulate_maturity(initial_scores: np.ndarray, crc: float, cmf: float,
                       months: int = 36) -> np.ndarray:
    """
    Simulate maturity score evolution using a Markov chain per dimension.

    Each dimension starts at its initial score (rounded to nearest integer
    representing its maturity level) and transitions monthly according to
    the transition matrix. The output is a continuous-valued score that
    blends the Markov level with fractional noise.

    Returns shape (months+1, 7) array of dimension scores.
    """
    rng = np.random.default_rng(42)
    n_dim = len(initial_scores)
    trajectory = np.zeros((months + 1, n_dim))
    trajectory[0] = initial_scores.copy()

    P = build_transition_matrix(crc, cmf)

    # Convert initial scores to discrete levels (0-5)
    levels = np.clip(np.round(initial_scores).astype(int), 0, 5)

    for t in range(1, months + 1):
        for d in range(n_dim):
            row = P[levels[d]]
            new_level = rng.choice(6, p=row)
            levels[d] = new_level
            # Map level back to a score in [0, 5] with small noise
            trajectory[t, d] = new_level + rng.uniform(-0.2, 0.2)
            trajectory[t, d] = np.clip(trajectory[t, d], 0.0, 5.0)

    return trajectory


# ---------------------------------------------------------------------------
# Operator Profile Generation
# ---------------------------------------------------------------------------

def generate_operator_profile(op_type: str) -> dict:
    """
    Return initial scores and expected CRC / CMF ranges for each operator type.
    """
    if op_type == "Advanced":
        base_scores = np.array([4.2, 4.0, 4.5, 3.8, 4.1, 4.3, 4.4])
    elif op_type == "Mid-tier":
        base_scores = np.array([2.8, 2.5, 2.3, 2.1, 2.7, 2.9, 3.0])
    else:  # Lagging
        base_scores = np.array([1.8, 1.5, 1.2, 1.0, 1.6, 1.9, 2.0])

    crc = compute_crc(base_scores)
    cmf = compute_cmf(base_scores * 0.95, base_scores)  # small assumed prior delta

    return {
        "type": op_type,
        "scores": base_scores,
        "crc": crc,
        "cmf": cmf,
    }


# ---------------------------------------------------------------------------
# Main Simulation
# ---------------------------------------------------------------------------

def main():
    months = 36
    operator_types = ["Advanced", "Mid-tier", "Lagging"]
    results = {}

    print("=" * 82)
    print("  COMET Framework — Scenario Runner")
    print("  Markov Chain Maturity Progression Simulation (36 months)")
    print("=" * 82)
    print()

    for op_type in operator_types:
        profile = generate_operator_profile(op_type)
        scores0 = profile["scores"]
        crc0 = profile["crc"]
        cmf0 = profile["cmf"]

        trajectory = simulate_maturity(scores0, crc0, cmf0, months)

        # Compute indicators at month 0 and month 36
        mci_0 = compute_mci(trajectory[0])
        sgmi_0 = compute_sgmi(trajectory[0])
        av_0 = compute_av(mci_0)

        mci_36 = compute_mci(trajectory[-1])
        sgmi_36 = compute_sgmi(trajectory[-1])
        av_36 = compute_av(mci_36)
        crc_36 = compute_crc(trajectory[-1])
        cmf_36 = compute_cmf(trajectory[-2], trajectory[-1])
        ts_36 = compute_ts(mci_36, sgmi_36, av_36, crc_36, cmf_36)

        results[op_type] = {
            "trajectory": trajectory,
            "mci_0": mci_0, "mci_36": mci_36,
            "sgmi_0": sgmi_0, "sgmi_36": sgmi_36,
            "av_0": av_0, "av_36": av_36,
            "crc_36": crc_36, "cmf_36": cmf_36, "ts_36": ts_36,
        }

        # Print per-operator summary
        print(f"--- {op_type} Operator ---")
        print(f"  Initial MCI : {mci_0:.4f}   ->   Month-36 MCI : {mci_36:.4f}")
        print(f"  Initial SGMI: {sgmi_0:.4f}   ->   Month-36 SGMI: {sgmi_36:.4f}")
        print(f"  Initial AV : {av_0:.6f} ({av_0*100:.4f}%)  ->  "
              f"Month-36 AV : {av_36:.6f} ({av_36*100:.4f}%)")
        print(f"  CRC (month 36): {crc_36:.4f}")
        print(f"  CMF (month 36): {cmf_36:.4f}")
        print(f"  TS  (month 36): {ts_36:.4f}")
        print()

    # ----- Comparative Summary Table -----
    header = (
        f"{'Operator':<12}{'MCI0':>8}{'MCI36':>8}{'dMCI':>8}"
        f"{'SGMI0':>8}{'SGMI36':>8}{'AV36':>10}{'CRC36':>8}"
        f"{'CMF36':>8}{'TS36':>8}"
    )
    print("=" * 88)
    print("  COMPARATIVE SUMMARY TABLE")
    print("=" * 88)
    print(header)
    print("-" * 88)
    for op_type in operator_types:
        r = results[op_type]
        delta_mci = r["mci_36"] - r["mci_0"]
        line = (
            f"{op_type:<12}{r['mci_0']:>8.4f}{r['mci_36']:>8.4f}{delta_mci:>+8.4f}"
            f"{r['sgmi_0']:>8.4f}{r['sgmi_36']:>8.4f}{r['av_36']:>10.6f}"
            f"{r['crc_36']:>8.4f}{r['cmf_36']:>8.4f}{r['ts_36']:>8.4f}"
        )
        print(line)
    print("=" * 88)
    print()

    # ----- MCI Evolution (monthly) -----
    print("Monthly MCI evolution:")
    print(f"{'Month':>5}", end="")
    for op_type in operator_types:
        print(f"{op_type:>12}", end="")
    print()
    print("-" * 41)
    for t in range(0, months + 1, 3):  # every 3 months
        print(f"{t:>5}", end="")
        for op_type in operator_types:
            mci_t = compute_mci(results[op_type]["trajectory"][t])
            print(f"{mci_t:>12.4f}", end="")
        print()
    print()

    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    np.savez(
        os.path.join(base_dir, "simulation", "simulation_results.npz"),
        months=np.arange(months + 1),
        advanced_trajectory=results["Advanced"]["trajectory"],
        midtier_trajectory=results["Mid-tier"]["trajectory"],
        lagging_trajectory=results["Lagging"]["trajectory"],
    )
    print("Simulation results saved to simulation/simulation_results.npz")


if __name__ == "__main__":
    main()
