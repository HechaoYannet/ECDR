"""A restartable population search, identical across every experimental arm.

The experiment must isolate ONE thing: the signal used to decide when a mechanism
class is abandoned.  So the searcher is deliberately fixed, simple, deterministic
given a seed, and interruptible between generations, so that a controller can stop
it and spend the remaining budget elsewhere.

This is the analogue of Heuresis holding the agent loop fixed and varying only the
search strategy (Finding 003, borrow list item 7), with the roles swapped: here the
loop is fixed and the ABANDONMENT SIGNAL varies.
"""
from __future__ import annotations

import numpy as np


class PopulationSearch:
    """A (mu + lambda) evolution strategy with box constraints.

    Deterministic given the seed.  One call to generation() advances exactly one
    generation and reports how many objective evaluations it consumed, so the cost
    ledger is exact rather than estimated.
    """

    def __init__(self, problem, seed: int = 0, popsize: int = 16, offspring: int = 16,
                 sigma: float = 0.22, penalty: float = 1.0e3):
        self.problem = problem
        self.penalty = penalty
        self.rng = np.random.default_rng(seed)
        lo = np.array([b[0] for b in problem.bounds], dtype=float)
        hi = np.array([b[1] for b in problem.bounds], dtype=float)
        self.lo, self.hi = lo, hi
        self.sigma = sigma
        self.offspring = offspring
        self.evals = 0

        self.pop = self.rng.uniform(lo, hi, size=(popsize, problem.dim))
        self.fit = np.array([self._score(x)[0] for x in self.pop])
        self.evals += popsize
        self.best_obj = float(np.max(self.fit))
        self.best_x = self.pop[int(np.argmax(self.fit))].copy()
        self.history = [self.best_obj]

    def _score(self, x):
        x = np.clip(x, self.lo, self.hi)
        obj, cons = self.problem.evaluate(x)
        violation = float(np.maximum(cons, 0.0).sum())
        return obj - self.penalty * violation, obj, cons

    def generation(self) -> int:
        """Advance one generation.  Returns the number of evaluations consumed."""
        idx = self.rng.integers(0, self.pop.shape[0], size=self.offspring)
        steps = self.rng.normal(0.0, self.sigma, size=(self.offspring, self.problem.dim))
        cand = np.clip(self.pop[idx] + steps * (self.hi - self.lo), self.lo, self.hi)
        cfit = np.array([self._score(x)[0] for x in cand])
        self.evals += self.offspring

        all_x = np.vstack([self.pop, cand])
        all_f = np.concatenate([self.fit, cfit])
        keep = np.argsort(all_f)[::-1][: self.pop.shape[0]]
        self.pop, self.fit = all_x[keep], all_f[keep]

        cur = float(np.max(self.fit))
        if cur > self.best_obj:
            self.best_obj = cur
            self.best_x = self.pop[int(np.argmax(self.fit))].copy()
        self.history.append(self.best_obj)
        return self.offspring

    def best_feasible(self):
        """Best design that satisfies every constraint, verified on the exact peak."""
        from ..l0.invariants import tf_coeffs
        from ..l0.peaks import peak_of
        from ..l0.certificates import peak_transmissibility_sdof, peak_transmissibility_skynook
        from ..l0.peaks import peak_of as _po

        mech = self.problem.mechanism
        # exact peak via the mechanism callable, coefficients only to seed candidates
        try:
            num, den = tf_coeffs(mech.name, self.best_x)
        except Exception:
            num, den = None, None
        f = (lambda w: mech.transmissibility(w, self.best_x))
        if num is None:
            return None
        pk, _ = _po(f, num, den, n_grid=4000, refine=False)
        band = self.problem.grid >= self.problem.task.omega_low
        T = np.abs(f(self.problem.grid))
        in_band = float(T[band].max())
        sag = float(mech.static_deflection(self.best_x))
        ok = (pk <= self.problem.task.A_max * (1 + 1e-9)) and (sag <= self.problem.task.delta_max)
        if self.problem.task.force_per_disp_max is not None:
            F = np.abs(mech.actuator_force_per_disp(self.problem.grid, self.best_x))
            ok = ok and (float(F.max()) <= self.problem.task.force_per_disp_max)
        return {
            "params": self.best_x.copy(),
            "exact_peak": float(pk),
            "in_band_T": in_band,
            "static_sag_mm": sag * 1e3,
            "constraints_ok": bool(ok),
            "meets_isolation_target": bool(ok and in_band <= self.problem.task.T_iso),
        }
