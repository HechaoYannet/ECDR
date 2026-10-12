"""Generic numerical feasibility checks and witness search for any L0 mechanism.

The certificate in certificates.py is analytic and only covers M1.  For M2 and
M3 there is no such closed form, so feasibility is established the other way
round: by exhibiting a *witness* (an explicit parameter vector that satisfies
every constraint).  Existence is proved by construction; non-existence is only
ever claimed where a certificate exists.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np

from .mechanisms import Mechanism
from .task import IsolationTask

# Dense log-spaced frequency grid; the band constraint and the peak both need to
# be resolved, so we cover five decades around the interesting region.
DEFAULT_OMEGA = np.logspace(np.log10(0.05), np.log10(5.0e4), 20000)

# 0.7 % spacing across six decades: enough to resolve the peaks and the band edge
# while keeping a 50 000-evaluation witness search affordable.
SEARCH_OMEGA = np.logspace(np.log10(0.05), np.log10(5.0e4), 3000)


def constraint_violation(
    mech: Mechanism,
    params: Sequence[float],
    task: IsolationTask,
    omega: np.ndarray | None = None,
) -> float:
    """Max normalised constraint violation. <= 0 means every constraint holds.

    Normalisation makes the different constraints commensurate, which matters
    for the penalty-based witness search.
    """
    omega = DEFAULT_OMEGA if omega is None else np.asarray(omega, dtype=float)
    T = np.abs(mech.transmissibility(omega, params))
    if not np.all(np.isfinite(T)):
        return float("inf")

    violations = [
        float(T[omega >= task.omega_low].max() / task.T_iso - 1.0),
        float(T.max() / task.A_max - 1.0),
        float(mech.static_deflection(params) / task.delta_max - 1.0),
    ]
    if task.force_per_disp_max is not None:
        F = np.abs(mech.actuator_force_per_disp(omega, params))
        violations.append(float(F.max() / task.force_per_disp_max - 1.0))
    return max(violations)


def violation_grid(
    mech: Mechanism,
    task: IsolationTask,
    i: int,
    j: int,
    grid_i: np.ndarray,
    grid_j: np.ndarray,
    other: Sequence[float],
    omega: np.ndarray | None = None,
) -> np.ndarray:
    """Brute-force violation over a 2-D slice of the parameter space.

    Used to *independently falsify* a certificate: if the certificate says a
    mechanism is infeasible, no cell of any grid may come back feasible.
    """
    out = np.empty((grid_i.size, grid_j.size))
    for a, vi in enumerate(grid_i):
        for b, vj in enumerate(grid_j):
            p = list(other)
            p[i] = float(vi)
            p[j] = float(vj)
            out[a, b] = constraint_violation(mech, p, task, omega)
    return out


def search_witness(
    mech: Mechanism,
    task: IsolationTask,
    seed: int = 0,
    maxiter: int = 400,
    popsize: int = 40,
    omega: np.ndarray | None = None,
) -> dict:
    """Look for an explicit feasible parameter vector using differential evolution.

    Returns a dict with the best parameters found, the resulting violation, and
    a boolean witness flag.  A negative violation *is* the feasibility proof.
    """
    from scipy.optimize import differential_evolution

    grid = SEARCH_OMEGA if omega is None else omega

    def objective(x):
        return constraint_violation(mech, x, task, grid)

    result = differential_evolution(
        objective,
        bounds=list(mech.param_bounds),
        seed=seed,
        maxiter=maxiter,
        popsize=popsize,
        tol=1e-12,
        polish=True,
        mutation=(0.3, 1.0),
        recombination=0.9,
        init="sobol",
        updating="immediate",
        workers=1,
    )
    params = [float(v) for v in result.x]
    # Re-score on the fine grid: a witness that only passes the coarse grid is
    # no witness at all.
    viol_fine = constraint_violation(mech, params, task)
    return {
        "mechanism": mech.name,
        "witness_found": bool(viol_fine <= 0.0),
        "violation_search_grid": float(result.fun),
        "violation": viol_fine,
        "params": dict(zip(mech.param_names, params)),
        "constraint_report": describe_constraints(mech, params, task),
    }


def describe_constraints(mech: Mechanism, params: Sequence[float], task: IsolationTask,
                         omega: np.ndarray | None = None) -> dict:
    """Human-readable margin on each constraint, for the witness report."""
    omega = DEFAULT_OMEGA if omega is None else np.asarray(omega, dtype=float)
    T = np.abs(mech.transmissibility(omega, params))
    band = omega >= task.omega_low
    rep = {
        "in_band_max_T": float(T[band].max()),
        "in_band_limit": float(task.T_iso),
        "peak_T": float(T.max()),
        "peak_limit": float(task.A_max),
        "static_deflection_mm": float(mech.static_deflection(params) * 1e3),
        "static_deflection_limit_mm": float(task.delta_max * 1e3),
    }
    if task.force_per_disp_max is not None:
        F = np.abs(mech.actuator_force_per_disp(omega, params))
        rep["max_force_per_disp"] = float(F.max())
        rep["force_per_disp_limit"] = float(task.force_per_disp_max)
    return rep
