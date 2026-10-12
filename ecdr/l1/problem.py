"""L1 problem records: the same BOCoDe interface, evaluated at the higher rung.

The difference from L0 is entirely in the constraints.  L1 asks whether a design
holds across a PERTURBATION BOX and, for the active mechanism, whether it still
works with a finite-bandwidth actuator.  It never relaxes an L0 constraint, which is
what makes L0 infeasibility certificates transfer.
"""
from __future__ import annotations

import numpy as np

from ..l0.task import IsolationTask
from ..l0.mechanisms import Mechanism

# Cheaper than L0's grid because every evaluation is multiplied by the number of
# perturbation samples.  Still only a search signal, never a certificate.
L1_SEARCH_GRID = np.logspace(np.log10(0.05), np.log10(1.0e5), 1500)


class MechanismProblemL1:
    """One (task, mechanism) pair at L1, in BOCoDe canonical form."""

    def __init__(self, task: IsolationTask, mechanism: Mechanism, rel: float = 0.06,
                 n_pert: int = 5, grid=None, seed: int = 0):
        self.task = task
        self.mechanism = mechanism
        self.rel = rel
        self.n_pert = n_pert
        self.grid = L1_SEARCH_GRID if grid is None else np.asarray(grid, dtype=float)
        self.name = task.name + "::" + mechanism.name + "::L1"
        self.mechanism_class = mechanism.name
        self.param_names = tuple(mechanism.param_names)
        self.bounds = tuple(mechanism.param_bounds)
        self.dim = len(self.bounds)
        self._rng = np.random.default_rng(seed)
        lo = np.array([b[0] for b in self.bounds], dtype=float)
        hi = np.array([b[1] for b in self.bounds], dtype=float)
        self._lo, self._hi = lo, hi
        # perturbation directions are FIXED per problem so the objective is a
        # deterministic function of x; otherwise the searcher optimises noise
        self._dirs = 1.0 + rel * (2.0 * np.random.default_rng(12345 + seed).random(
            (n_pert, self.dim)) - 1.0)

    def sample(self, n: int, seed: int = 0) -> np.ndarray:
        rng = np.random.default_rng(seed)
        return self._lo + (self._hi - self._lo) * rng.random((n, self.dim))

    def evaluate(self, x):
        """Worst case over the perturbation box.  Objective maximised, cons <= 0 ok."""
        x = np.asarray(x, dtype=float).ravel()
        band = self.grid >= self.task.omega_low
        # objective is maximised and we store -in_band, so the worst case is the
        # MINIMUM and the accumulator must start at +inf
        worst_obj = np.inf
        worst_cons = [-np.inf, -np.inf, -np.inf]
        for d in self._dirs:
            p = np.clip(x * d, self._lo, self._hi)
            T = np.abs(self.mechanism.transmissibility(self.grid, p))
            in_band = float(T[band].max())
            # The objective is MAXIMISED and the value stored is -in_band, so the
            # worst case over the perturbation box is the MINIMUM of these.  Taking
            # the maximum instead optimises the most OPTIMISTIC direction in the box,
            # which makes the search chase designs that then fail independent
            # verification.  Confirmed by counterexample before the fix:
            # evaluate returned 0.095015 while the worst of the same five directions
            # was 0.107885 and verify_l1 returned 0.110556.
            worst_obj = min(worst_obj, -in_band)
            worst_cons[0] = max(worst_cons[0], float(T.max() / self.task.A_max - 1.0))
            worst_cons[1] = max(worst_cons[1],
                                float(self.mechanism.static_deflection(p) / self.task.delta_max - 1.0))
            if self.task.force_per_disp_max is not None:
                F = np.abs(self.mechanism.actuator_force_per_disp(self.grid, p))
                worst_cons[2] = max(worst_cons[2],
                                    float(F.max() / self.task.force_per_disp_max - 1.0))
        return worst_obj, np.array(worst_cons)

    def metadata(self) -> dict:
        return {
            "problem_id": self.name, "task_id": self.task.name,
            "mechanism_class": self.mechanism_class, "fidelity": "L1",
            "dim": self.dim, "param_names": list(self.param_names),
            "bounds": [list(b) for b in self.bounds],
            "perturbation_rel": self.rel, "n_perturbation": self.n_pert,
            "objective": "maximise minus worst-case in-band |T| over the perturbation box",
        }


def verify_l1(mechanism: Mechanism, params, task, rel: float = 0.06, n_pert: int = 24,
              grid=None, seed: int = 909) -> dict:
    """Independent L1 verification: more perturbation samples, finer grid.

    Kept separate from the search objective on purpose (Finding 003 integrity rule 5).
    """
    g = np.logspace(np.log10(0.02), np.log10(2.0e5), 8000) if grid is None else np.asarray(grid)
    rng = np.random.default_rng(seed)
    p = np.asarray(params, dtype=float)
    lo = np.array([b[0] for b in mechanism.param_bounds], dtype=float)
    hi = np.array([b[1] for b in mechanism.param_bounds], dtype=float)
    band = g >= task.omega_low
    worst_in = -np.inf
    worst_peak = -np.inf
    worst_sag = -np.inf
    worst_force = -np.inf
    for _ in range(n_pert):
        d = 1.0 + rel * (2.0 * rng.random(p.shape) - 1.0)
        q = np.clip(p * d, lo, hi)
        T = np.abs(mechanism.transmissibility(g, q))
        worst_in = max(worst_in, float(T[band].max()))
        worst_peak = max(worst_peak, float(T.max()))
        worst_sag = max(worst_sag, float(mechanism.static_deflection(q)))
        if task.force_per_disp_max is not None:
            F = np.abs(mechanism.actuator_force_per_disp(g, q))
            worst_force = max(worst_force, float(F.max()))
    ok = (worst_peak <= task.A_max and worst_sag <= task.delta_max
          and worst_in <= task.T_iso)
    if task.force_per_disp_max is not None:
        ok = ok and worst_force <= task.force_per_disp_max
    return {
        "worst_in_band_T": worst_in, "limit": float(task.T_iso),
        "worst_peak": worst_peak, "worst_sag_mm": worst_sag * 1e3,
        "worst_force_per_disp": None if task.force_per_disp_max is None else worst_force,
        "meets_isolation_target": bool(ok),
    }
