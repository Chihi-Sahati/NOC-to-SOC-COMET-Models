# -*- coding: utf-8 -*-
"""
TS (Transformation Success) Regression Model — COMET Framework.

This module implements the linear regression model for predicting
Transformation Success (TS) as a function of multiple COMET indicators
and their interactions with Time Maturity (TM).

Mathematical Formulation:
    TS = γ₁·MCI + γ₂·CRC + γ₃·CMF + γ₄·AV
       + γ₅·(CRC × TM) + γ₆·(CMF × TM) + ε

where:
    MCI = Maturity Coherence Index
    CRC = Cultural Readiness Coefficient
    CMF = Contextual Maturity Factor
    AV  = Automation Velocity
    TM  = Time Maturity (years since transformation start)
    γ₁ … γ₆ = regression coefficients
    ε  = error term (zero-mean Gaussian noise in simulation)

The model supports two modes:
    1. Prediction with user-supplied coefficients.
    2. Estimation of coefficients from observed data via OLS.

References:
    COMET Framework — NOC-to-SOC Unified Theory of Intelligent Service
    Transformation in Telecommunications.
"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np


class TransformationSuccessModel:
    """
    Regression model for Transformation Success (TS).

    Parameters
    ----------
    coefficients : array-like of 6 floats or None
        [γ₁, γ₂, γ₃, γ₄, γ₅, γ₆]. If None, must call `fit` before
        `predict`.

    Attributes
    ----------
    coefficients_ : np.ndarray or None
        Fitted or supplied coefficients.
    r_squared_ : float or None
        R² from the most recent OLS fit.
    residuals_ : np.ndarray or None
        Residuals from the most recent OLS fit.
    """

    # Design-matrix column names for interpretability
    FEATURE_NAMES = [
        "MCI",
        "CRC",
        "CMF",
        "AV",
        "CRC_x_TM",
        "CMF_x_TM",
    ]

    def __init__(
        self,
        coefficients: Optional[Sequence[float]] = None,
    ) -> None:
        if coefficients is not None:
            self.coefficients_ = np.asarray(coefficients, dtype=np.float64)
            if self.coefficients_.shape != (6,):
                raise ValueError(
                    f"coefficients must have 6 elements, got {self.coefficients_.size}."
                )
        else:
            self.coefficients_ = None
        self.r_squared_: Optional[float] = None
        self.residuals_: Optional[np.ndarray] = None

    @staticmethod
    def _build_design_matrix(
        mci: np.ndarray,
        crc: np.ndarray,
        cmf: np.ndarray,
        av: np.ndarray,
        tm: np.ndarray,
    ) -> np.ndarray:
        """
        Build the n×6 design matrix X for the regression.

        Parameters
        ----------
        mci, crc, cmf, av, tm : array-like, each of length n

        Returns
        -------
        np.ndarray, shape (n, 6)
        """
        mci = np.asarray(mci, dtype=np.float64)
        crc = np.asarray(crc, dtype=np.float64)
        cmf = np.asarray(cmf, dtype=np.float64)
        av = np.asarray(av, dtype=np.float64)
        tm = np.asarray(tm, dtype=np.float64)

        n = len(mci)
        for name, arr in [("MCI", mci), ("CRC", crc), ("CMF", cmf),
                          ("AV", av), ("TM", tm)]:
            if arr.shape != (n,):
                raise ValueError(
                    f"All inputs must have the same length. "
                    f"{name} has length {len(arr)}, expected {n}."
                )

        X = np.column_stack([
            mci,                # γ₁
            crc,                # γ₂
            cmf,                # γ₃
            av,                 # γ₄
            crc * tm,           # γ₅  (interaction)
            cmf * tm,           # γ₆  (interaction)
        ])
        return X

    def fit(
        self,
        mci: Sequence[float],
        crc: Sequence[float],
        cmf: Sequence[float],
        av: Sequence[float],
        tm: Sequence[float],
        ts: Sequence[float],
    ) -> "TransformationSuccessModel":
        """
        Estimate coefficients via Ordinary Least Squares (OLS).

        Parameters
        ----------
        mci, crc, cmf, av, tm : array-like
            Predictor variables, each of length n.
        ts : array-like
            Observed Transformation Success, length n.

        Returns
        -------
        self

        Raises
        ------
        ValueError
            If inputs are too short for OLS (need n > 6).
        np.linalg.LinAlgError
            If the design matrix is singular.
        """
        X = self._build_design_matrix(mci, crc, cmf, av, tm)
        y = np.asarray(ts, dtype=np.float64)

        if X.shape[0] <= X.shape[1]:
            raise ValueError(
                f"Need more observations ({X.shape[0]}) than "
                f"features ({X.shape[1]})."
            )

        # OLS: β = (X'X)^{-1} X'y
        # Using numpy least-squares for numerical stability
        result = np.linalg.lstsq(X, y, rcond=None)
        self.coefficients_ = result[0]
        y_pred = X @ self.coefficients_
        self.residuals_ = y - y_pred

        ss_res = float(np.sum(self.residuals_ ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        self.r_squared_ = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        return self

    def predict(
        self,
        mci: float | Sequence[float],
        crc: float | Sequence[float],
        cmf: float | Sequence[float],
        av: float | Sequence[float],
        tm: float | Sequence[float],
    ) -> float | np.ndarray:
        """
        Predict TS given input features.

        Parameters
        ----------
        mci, crc, cmf, av, tm : float or array-like
            Input features. Can be scalars (single prediction) or
            sequences (batch prediction).

        Returns
        -------
        float or np.ndarray
            Predicted TS value(s).

        Raises
        ------
        RuntimeError
            If coefficients have not been set or fitted.
        """
        if self.coefficients_ is None:
            raise RuntimeError(
                "Model has no coefficients. Supply them at init or call fit()."
            )

        # Normalise scalars to 1-element arrays
        single = False
        for name, val in [("mci", mci), ("crc", crc), ("cmf", cmf),
                          ("av", av), ("tm", tm)]:
            if isinstance(val, (int, float)):
                single = True
                break

        if single:
            mci = np.atleast_1d(np.asarray(mci, dtype=np.float64))
            crc = np.atleast_1d(np.asarray(crc, dtype=np.float64))
            cmf = np.atleast_1d(np.asarray(cmf, dtype=np.float64))
            av = np.atleast_1d(np.asarray(av, dtype=np.float64))
            tm = np.atleast_1d(np.asarray(tm, dtype=np.float64))

        X = self._build_design_matrix(mci, crc, cmf, av, tm)
        y_pred = X @ self.coefficients_

        if single:
            return float(y_pred[0])
        return y_pred

    def summary(self) -> str:
        """Return a human-readable summary of the model."""
        lines = ["Transformation Success (TS) Regression Model"]
        lines.append("=" * 50)
        if self.coefficients_ is not None:
            lines.append("Coefficients:")
            for name, coef in zip(self.FEATURE_NAMES, self.coefficients_):
                lines.append(f"  γ_{self.FEATURE_NAMES.index(name)+1} ({name:12s}) = {coef:+.6f}")
            if self.r_squared_ is not None:
                lines.append(f"\nR² = {self.r_squared_:.6f}")
        else:
            lines.append("No coefficients (call fit() or supply at init).")
        return "\n".join(lines)


if __name__ == "__main__":
    np.random.seed(42)

    # --- Synthetic training data ---
    n = 50
    mci = np.random.uniform(0.3, 0.9, n)
    crc = np.random.uniform(0.2, 0.8, n)
    cmf = np.random.uniform(0.3, 0.7, n)
    av = np.random.uniform(0.1, 2.0, n)
    tm = np.random.uniform(0.5, 5.0, n)

    # True coefficients
    true_gammas = np.array([0.25, 0.30, 0.15, 0.10, 0.05, 0.08])
    noise = np.random.normal(0, 0.02, n)

    X = TransformationSuccessModel._build_design_matrix(mci, crc, cmf, av, tm)
    ts_observed = X @ true_gammas + noise

    # --- Fit the model ---
    model = TransformationSuccessModel()
    model.fit(mci, crc, cmf, av, tm, ts_observed)
    print(model.summary())

    # --- Predict ---
    ts_pred = model.predict(mci=0.75, crc=0.65, cmf=0.55, av=1.2, tm=3.0)
    print(f"\nPredicted TS for a sample input = {ts_pred:.4f}")

    # --- Batch predict ---
    batch_ts = model.predict(
        mci=[0.6, 0.8], crc=[0.5, 0.7], cmf=[0.4, 0.6], av=[0.8, 1.5], tm=[2.0, 4.0],
    )
    print(f"Batch predictions: {batch_ts}")