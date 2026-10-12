"""BOCoDe-style problem records for the ECDR registry.

BOCoDe (arXiv 2608.15073) standardised engineering benchmarks as

    evaluate(x) -> (obj, cons)

with per-problem machine-readable metadata.  This module adopts that interface
exactly, and adds the two fields BOCoDe has no notion of:

    mechanism_class          which design space x lives in
    evidence                 what is known about solvability, and how

Adopting the interface is what makes the strong baselines comparable rather than
reimplemented: the same optimiser, the same budget accounting, the same problem
object -- the only thing that varies is the mechanism class, i.e. the inventory
the agent is allowed to reach for.

IMPORTANT asymmetry, deliberate and documented
----------------------------------------------
evaluate() uses a FREQUENCY GRID, because it is the agent inner loop and must be
cheap.  A grid can miss a sharp resonance (see ecdr/l0/peaks.py, where one was
under-reported by a factor of 178386).  Therefore evaluate() is NOT evidence of
feasibility.  Only the certificate (M1, M3) or an explicit witness checked with
the exact peak routine (M2) is evidence.  Keeping the cheap signal and the sound
signal in separate code paths is integrity rule 5 of Finding 003.
"""
from __future__ import annotations

import numpy as np

from ..l0 import G
from ..l0.mechanisms import Mechanism
from ..l0.task import IsolationTask

# Cheap grid for search.  A grid can miss narrow peaks; that is why it is used for
# scoring only, never for certification.
SEARCH_GRID = np.logspace(np.log10(0.02), np.log10(2.0e5), 4000)


class MechanismProblem:
    """One (task, mechanism) pair, in BOCoDe canonical form."""

    def __init__(self, task: IsolationTask, mechanism: Mechanism, grid=None):
        self.task = task
        self.mechanism = mechanism
        self.grid = SEARCH_GRID if grid is None else np.asarray(grid, dtype=float)
        self.name = task.name + "::" + mechanism.name
        self.mechanism_class = mechanism.name
        self.param_names = tuple(mechanism.param_names)
        self.bounds = tuple(mechanism.param_bounds)
        self.dim = len(self.bounds)

    # ---- BOCoDe interface --------------------------------------------------
    def sample(self, n: int, seed: int = 0) -> np.ndarray:
        rng = np.random.default_rng(seed)
        lo = np.array([b[0] for b in self.bounds])
        hi = np.array([b[1] for b in self.bounds])
        return lo + (hi - lo) * rng.random((n, self.dim))

    def evaluate(self, x):
        """Return (objective, constraints).  Objective is MAXIMISED; cons <= 0 is feasible."""
        x = np.asarray(x, dtype=float).ravel()
        T = np.abs(self.mechanism.transmissibility(self.grid, x))
        band = self.grid >= self.task.omega_low
        in_band = float(T[band].max())

        cons = [float(T.max() / self.task.A_max - 1.0),
                float(self.mechanism.static_deflection(x) / self.task.delta_max - 1.0)]
        if self.task.force_per_disp_max is not None:
            F = np.abs(self.mechanism.actuator_force_per_disp(self.grid, x))
            cons.append(float(F.max() / self.task.force_per_disp_max - 1.0))
        return -in_band, np.array(cons)

    def metadata(self) -> dict:
        return {
            "problem_id": self.name,
            "task_id": self.task.name,
            "mechanism_class": self.mechanism_class,
            "dim": self.dim,
            "param_names": list(self.param_names),
            "bounds": [list(b) for b in self.bounds],
            "f_low_hz": self.task.f_low,
            "T_iso": float(self.task.T_iso),
            "A_max": float(self.task.A_max),
            "delta_max_mm": float(self.task.delta_max * 1e3),
            "objective": "maximise minus in-band max |T|",
            "constraints": ["peak", "static_sag"] + (["actuator_force"]
                            if self.task.force_per_disp_max is not None else []),
            "source": "ecdr.l0 analytic testbed",
        }


def solve_within_mechanism(problem: MechanismProblem, seed: int = 0, maxiter: int = 300,
                           popsize: int = 20):
    """Strongest search INSIDE one mechanism class -- the local-refinement baseline.

    This is the arm that gets the identical operator set and budget but is never
    allowed to leave its mechanism class.  Returning the objective profile lets the
    cost ledger charge every evaluation.
    """
    from scipy.optimize import differential_evolution

    ledger = {"calls": 0}

    def neg_obj(x):
        ledger["calls"] += 1
        obj, cons = problem.evaluate(x)
        penalty = float(np.maximum(cons, 0.0).sum())
        return -obj + 1e3 * penalty

    res = differential_evolution(neg_obj, bounds=list(problem.bounds), seed=seed,
                                 maxiter=maxiter, popsize=popsize, tol=1e-10,
                                 polish=True, init="sobol", workers=1)
    obj, cons = problem.evaluate(res.x)
    return {
        "problem_id": problem.name,
        "mechanism_class": problem.mechanism_class,
        "objective": float(obj),
        "constraints": [float(c) for c in cons],
        "feasible_by_grid": bool(np.all(np.array(cons) <= 0.0)),
        "params": {k: float(v) for k, v in zip(problem.param_names, res.x)},
        "evaluations": int(ledger["calls"]),
    }
