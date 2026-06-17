# -*- coding: utf-8 -*-
"""
Markov Transition Model for Maturity Levels — COMET Framework.

This module models the stochastic evolution of maturity levels across
transformation dimensions using a multinomial logit (softmax) parameterisation
of transition probabilities. Each dimension's maturity level can move
between discrete states (0 through M-1) based on contextual covariates.

Mathematical Formulation:
    P(L_k^{t+1} = j | L_k^t = i, X) = exp(X · β_ij) / Σ_l exp(X · β_il)

where:
    L_k^t   = maturity level of dimension k at time t
    i, j    = current and next maturity levels (discrete states)
    X       = vector of covariates (e.g., investment, cultural readiness)
    β_ij    = coefficient vector for transition from i to j
    M       = number of maturity levels (default 6, i.e. levels 0–5)

The transition matrix is recomputed at each step based on the covariates,
allowing time-varying or scenario-dependent transitions.

References:
    COMET Framework — NOC-to-SOC Unified Theory of Intelligent Service
    Transformation in Telecommunications.
"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np


def softmax(logits: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Numerically stable softmax along the given axis.
    """
    shifted = logits - np.max(logits, axis=axis, keepdims=True)
    exp_vals = np.exp(shifted)
    return exp_vals / np.sum(exp_vals, axis=axis, keepdims=True)


def compute_transition_matrix(
    covariates: np.ndarray,
    beta: np.ndarray,
    n_levels: int,
) -> np.ndarray:
    """
    Compute the M×M transition matrix P using the multinomial logit form.

    Parameters
    ----------
    covariates : np.ndarray, shape (p,)
        Covariate vector X (p features).
    beta : np.ndarray, shape (n_levels, n_levels, p)
        Coefficient tensors β[i, j, :] for transition from level i to j.
    n_levels : int
        Number of maturity levels M.

    Returns
    -------
    np.ndarray, shape (n_levels, n_levels)
        Row-stochastic transition matrix P where P[i, j] =
        P(L^{t+1} = j | L^t = i, X).
    """
    # logits[i, j] = X · β[i, j, :]
    logits = np.einsum("p,ijp->ij", covariates, beta)
    P = softmax(logits, axis=1)
    return P


def simulate_markov_chain(
    initial_state: int,
    covariates_seq: np.ndarray,
    beta: np.ndarray,
    n_levels: int = 6,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    """
    Simulate a single-dimension Markov chain over T time steps.

    Parameters
    ----------
    initial_state : int
        Starting maturity level (0 to n_levels-1).
    covariates_seq : np.ndarray, shape (T, p)
        Covariate vectors for each time step.
    beta : np.ndarray, shape (n_levels, n_levels, p)
        Coefficient tensors.
    n_levels : int
        Number of maturity levels.
    rng : np.random.Generator or None
        Random number generator. If None, a new one is created.

    Returns
    -------
    np.ndarray, shape (T+1,)
        Maturity level at each time step (including initial state).
    """
    if rng is None:
        rng = np.random.default_rng()

    if not (0 <= initial_state < n_levels):
        raise ValueError(
            f"initial_state must be in [0, {n_levels-1}], got {initial_state}."
        )

    T = covariates_seq.shape[0]
    trajectory = np.empty(T + 1, dtype=int)
    trajectory[0] = initial_state
    current = initial_state

    for t in range(T):
        P = compute_transition_matrix(covariates_seq[t], beta, n_levels)
        probs = P[current, :]
        next_state = rng.choice(n_levels, p=probs)
        trajectory[t + 1] = next_state
        current = next_state

    return trajectory


class MarkovMaturityModel:
    """
    Full Markov maturity simulation with multi-dimensional support.

    Parameters
    ----------
    n_levels : int, optional
        Number of discrete maturity levels (0 to n_levels-1).
        Default is 6.
    n_covariates : int, optional
        Number of covariates p. Default is 3.
    seed : int or None, optional
        Random seed for reproducibility.
    """

    def __init__(
        self,
        n_levels: int = 6,
        n_covariates: int = 3,
        seed: Optional[int] = None,
    ) -> None:
        if n_levels < 2:
            raise ValueError(f"n_levels must be ≥ 2, got {n_levels}.")
        if n_covariates < 1:
            raise ValueError(f"n_covariates must be ≥ 1, got {n_covariates}.")

        self.n_levels = n_levels
        self.n_covariates = n_covariates
        self.rng = np.random.default_rng(seed)
        self.beta: Optional[np.ndarray] = None

    def set_beta(self, beta: np.ndarray) -> None:
        """
        Set the coefficient tensor β.

        Parameters
        ----------
        beta : np.ndarray, shape (n_levels, n_levels, n_covariates)
        """
        expected = (self.n_levels, self.n_levels, self.n_covariates)
        if beta.shape != expected:
            raise ValueError(
                f"beta must have shape {expected}, got {beta.shape}."
            )
        self.beta = beta.copy()

    def generate_random_beta(
        self,
        loc: float = 0.0,
        scale: float = 0.3,
    ) -> np.ndarray:
        """
        Generate a random coefficient tensor.

        Encourages diagonal dominance (self-transition bias) by adding
        extra weight to β[i, i, :].

        Parameters
        ----------
        loc : float
            Mean of the normal distribution for off-diagonal entries.
        scale : float
            Standard deviation.

        Returns
        -------
        np.ndarray, shape (n_levels, n_levels, n_covariates)
        """
        M, p = self.n_levels, self.n_covariates
        beta = self.rng.normal(loc=loc, scale=scale, size=(M, M, p))
        # Bias diagonal (self-loops) to be more likely
        for i in range(M):
            beta[i, i, :] += 1.0
        self.beta = beta
        return beta

    def simulate(
        self,
        initial_levels: Sequence[int],
        covariates_seq: np.ndarray,
        n_steps: int | None = None,
    ) -> np.ndarray:
        """
        Simulate maturity trajectories for multiple dimensions.

        Parameters
        ----------
        initial_levels : array-like
            Initial maturity level for each dimension.
        covariates_seq : np.ndarray, shape (T, p) or (T, K, p)
            If 2-D (T, p), the same covariates are used for all
            dimensions. If 3-D (T, K, p), each dimension gets its own
            covariate sequence.
        n_steps : int or None
            Override number of time steps. If None, uses the first
            dimension of covariates_seq.

        Returns
        -------
        np.ndarray, shape (K, T+1)
            Maturity trajectory for each dimension K.
        """
        if self.beta is None:
            raise RuntimeError("Call set_beta() or generate_random_beta() first.")

        initial = np.asarray(initial_levels, dtype=int)
        K = len(initial)

        if covariates_seq.ndim == 2:
            T = covariates_seq.shape[0] if n_steps is None else n_steps
            if n_steps is not None:
                covariates_seq = covariates_seq[:T]
            # Broadcast to (T, K, p)
            cov_seq_3d = np.tile(
                covariates_seq[:, np.newaxis, :],
                (1, K, 1),
            )
        elif covariates_seq.ndim == 3:
            T = covariates_seq.shape[0] if n_steps is None else n_steps
            cov_seq_3d = covariates_seq[:T]
        else:
            raise ValueError(
                f"covariates_seq must be 2-D or 3-D, got {covariates_seq.ndim}-D."
            )

        trajectories = np.empty((K, T + 1), dtype=int)
        for k in range(K):
            trajectories[k] = simulate_markov_chain(
                initial_state=int(initial[k]),
                covariates_seq=cov_seq_3d[:, k, :],
                beta=self.beta,
                n_levels=self.n_levels,
                rng=self.rng,
            )

        return trajectories

    def expected_maturity(
        self,
        covariates: np.ndarray,
        current_levels: Sequence[int],
        n_simulations: int = 1000,
    ) -> np.ndarray:
        """
        Monte Carlo estimate of expected maturity after one transition.

        Parameters
        ----------
        covariates : np.ndarray, shape (p,) or (K, p)
        current_levels : array-like
            Current maturity levels.
        n_simulations : int
            Number of Monte Carlo samples.

        Returns
        -------
        np.ndarray, shape (K,)
            Expected maturity for each dimension after one step.
        """
        if self.beta is None:
            raise RuntimeError("Call set_beta() or generate_random_beta() first.")

        current = np.asarray(current_levels, dtype=int)
        K = len(current)

        cov = np.atleast_2d(covariates)  # (K, p) or (1, p)
        if cov.shape[0] == 1:
            cov = np.tile(cov, (K, 1))

        expected = np.zeros(K, dtype=float)
        for k in range(K):
            P = compute_transition_matrix(cov[k], self.beta, self.n_levels)
            probs = P[current[k], :]
            expected[k] = np.dot(np.arange(self.n_levels), probs)

        return expected


if __name__ == "__main__":
    np.random.seed(42)

    # Setup: 6 maturity levels, 3 covariates
    model = MarkovMaturityModel(n_levels=6, n_covariates=3, seed=42)
    model.generate_random_beta(loc=0.0, scale=0.3)

    print("Beta tensor shape:", model.beta.shape)
    print("Diagonal bias (self-transition encouragement) applied.\n")

    # Generate covariate sequence: 50 time steps, 5 dimensions
    T, K = 50, 5
    covariates_seq = np.random.normal(0.5, 0.2, size=(T, K, 3))
    initial_levels = [1, 2, 0, 1, 3]  # Starting maturity per dimension

    # Simulate
    trajectories = model.simulate(initial_levels, covariates_seq)
    print(f"Trajectories shape: {trajectories.shape}")
    print(f"  (K={K} dimensions, T+1={T+1} time steps)\n")

    # Print first and last states for each dimension
    dim_names = ["Network", "Service", "Customer", "Process", "Culture"]
    for k, name in enumerate(dim_names):
        print(
            f"  {name:10s}: start={trajectories[k, 0]}, "
            f"end={trajectories[k, -1]}, "
            f"mean={trajectories[k].mean():.2f}, "
            f"max={trajectories[k].max()}"
        )

    # Expected maturity analysis
    current = [1, 2, 0, 1, 3]
    cov_now = np.array([[0.6, 0.5, 0.4]] * K)
    expected = model.expected_maturity(cov_now, current)
    print(f"\nExpected maturity after 1 step:")
    for name, cur, exp in zip(dim_names, current, expected):
        print(f"  {name:10s}: current={cur}, E[next]={exp:.3f}")

    # Transition matrix inspection for dimension 0
    P = compute_transition_matrix(cov_now[0], model.beta, model.n_levels)
    print(f"\nTransition matrix for '{dim_names[0]}' (row-stochastic):")
    print(np.array2string(P, precision=3, suppress_small=True))