# -*- coding: utf-8 -*-
"""
SGMI (Service Graph Maturity Index) — COMET Framework.

The Service Graph Maturity Index quantifies how mature and well-connected
a telecom operator's service graph is. It captures the degree to which
service nodes are interconnected and their contributions weighted by
importance, modelling the diminishing returns of additional connectivity
via a saturation (exponential) function.

Mathematical Formulation:
    SGMI = (1 / K) * Σₖ wₖ · (1 − exp(−α · Cₖ))

where:
    K    = total number of service nodes in the graph
    Cₖ   = connectivity metric for node k (e.g. number of links, or a
            normalised degree centrality in [0, ∞))
    wₖ   = importance weight for node k (default 1.0, weights need not
            sum to 1 because of the 1/K normalisation)
    α    = sensitivity parameter controlling the saturation rate.
            Higher α means faster saturation — connectivity improvements
            yield diminishing returns sooner.

Special cases:
    - If α → ∞, SGMI → (1/K) Σ wₖ   (fully saturated, max maturity)
    - If α → 0,  SGMI → 0             (no maturity signal captured)
    - If Cₖ = 0 for all k, SGMI = 0  (no connectivity, zero maturity)

References:
    COMET Framework — NOC-to-SOC Unified Theory of Intelligent Service
    Transformation in Telecommunications.
"""

from __future__ import annotations

import numpy as np
from typing import Optional, Sequence


class ServiceGraphMaturityIndex:
    """
    Computes the Service Graph Maturity Index (SGMI).

    Parameters
    ----------
    alpha : float, optional
        Sensitivity parameter controlling saturation. Must be > 0.
        Default is 1.0.
    weights : array-like or None, optional
        Per-node importance weights. If None, uniform weights (all 1.0)
        are used. Length must match the number of nodes.
    """

    def __init__(
        self,
        alpha: float = 1.0,
        weights: Optional[Sequence[float]] = None,
    ) -> None:
        if alpha <= 0:
            raise ValueError(f"alpha must be positive, got {alpha}.")
        self.alpha = float(alpha)
        self.weights: Optional[np.ndarray] = None
        if weights is not None:
            self.weights = np.asarray(weights, dtype=np.float64)

    def compute(
        self,
        connectivity: Sequence[float],
    ) -> float:
        """
        Compute SGMI for a set of service nodes.

        Parameters
        ----------
        connectivity : array-like
            Connectivity values Cₖ for each of the K service nodes.
            Must be non-negative.

        Returns
        -------
        float
            The Service Graph Maturity Index in [0, ∞), bounded above by
            the mean weight when connectivity is very large.

        Raises
        ------
        ValueError
            If connectivity is empty, contains negative values, or if
            weights length does not match connectivity length.
        """
        c = np.asarray(connectivity, dtype=np.float64)

        if c.size == 0:
            raise ValueError("connectivity array must not be empty.")
        if np.any(c < 0):
            raise ValueError("connectivity values must be non-negative.")

        k = c.size

        w = self.weights
        if w is not None:
            w = np.asarray(w, dtype=np.float64)
            if w.shape != c.shape:
                raise ValueError(
                    f"Weights length ({w.size}) must match connectivity "
                    f"length ({k})."
                )
        else:
            w = np.ones(k, dtype=np.float64)

        # Saturating maturity contribution per node
        maturity = w * (1.0 - np.exp(-self.alpha * c))
        sgmi = np.mean(maturity)

        return float(sgmi)

    def compute_matrix(
        self,
        adjacency: np.ndarray,
        node_weights: Optional[Sequence[float]] = None,
    ) -> float:
        """
        Compute SGMI from an adjacency matrix.

        Parameters
        ----------
        adjacency : np.ndarray, shape (K, K)
            Binary or weighted adjacency matrix of the service graph.
            Symmetric for undirected graphs.
        node_weights : array-like or None
            Override per-node weights. If None, uses self.weights.

        Returns
        -------
        float
            SGMI computed from degree centrality derived from the
            adjacency matrix.
        """
        adjacency = np.asarray(adjacency, dtype=np.float64)
        if adjacency.ndim != 2 or adjacency.shape[0] != adjacency.shape[1]:
            raise ValueError(
                "adjacency must be a square 2-D array "
                f"(got shape {adjacency.shape})."
            )

        # Degree centrality (row sums) as the connectivity metric
        connectivity = adjacency.sum(axis=1)

        w = node_weights if node_weights is not None else self.weights
        # Temporarily override weights for this call
        original_weights = self.weights
        if w is not None:
            self.weights = np.asarray(w, dtype=np.float64)
        try:
            result = self.compute(connectivity)
        finally:
            self.weights = original_weights

        return result


def compute_sgmi(
    connectivity: Sequence[float],
    alpha: float = 1.0,
    weights: Optional[Sequence[float]] = None,
) -> float:
    """
    Convenience function to compute SGMI in one call.

    Parameters
    ----------
    connectivity : array-like
        Per-node connectivity values.
    alpha : float
        Sensitivity parameter (must be > 0).
    weights : array-like or None
        Per-node importance weights.

    Returns
    -------
    float
        The Service Graph Maturity Index.

    Examples
    --------
    >>> compute_sgmi([3, 5, 2, 8, 1], alpha=0.5)
    """
    model = ServiceGraphMaturityIndex(alpha=alpha, weights=weights)
    return model.compute(connectivity)


if __name__ == "__main__":
    # Example 1: Simple connectivity array
    connectivities = [3.0, 5.0, 2.0, 8.0, 1.0]
    weights = [1.0, 1.5, 1.0, 2.0, 0.5]  # node 3 (idx 3) is most important

    sgmi = compute_sgmi(connectivities, alpha=0.5, weights=weights)
    print(f"SGMI (α=0.5, weighted)  = {sgmi:.4f}")

    # Example 2: Using the class with an adjacency matrix
    adjacency = np.array([
        [0, 1, 1, 0, 1],
        [1, 0, 1, 1, 0],
        [1, 1, 0, 1, 0],
        [0, 1, 1, 0, 1],
        [1, 0, 0, 1, 0],
    ], dtype=float)

    model = ServiceGraphMaturityIndex(alpha=0.3)
    sgmi_mat = model.compute_matrix(adjacency)
    print(f"SGMI (from adjacency)  = {sgmi_mat:.4f}")

    # Example 3: Varying alpha to show saturation behaviour
    print("\nSensitivity to alpha (uniform weights, same connectivity):")
    for a in [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]:
        val = compute_sgmi(connectivities, alpha=a)
        print(f"  α={a:5.1f}  →  SGMI = {val:.4f}")