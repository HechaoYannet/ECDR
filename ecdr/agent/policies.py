"""Abandonment policies: the single thing that varies between experimental arms.

Every policy answers one question, after each generation:

    should the agent stop spending budget on this mechanism class?

They differ only in WHAT THEY BASE THAT ON.  Per Finding 003 section 1.4:

    certificate   P1/P2/P7 sound: abandon only on a proof of infeasibility
    streak        heuristic: N consecutive non-improving generations
    plateau       heuristic: best-so-far has not moved by delta over a window
    surrogate     heuristic: extrapolate the best-so-far curve, abandon if the
                  predicted asymptote cannot reach the target
    never         control: pure local refinement, never leaves the mechanism
    oracle        upper bound: knows the ground-truth minimal mechanism

The heuristic arms are deliberately given reasonable, tuned-by-hand settings, not
strawmen: the claim under test is about the KIND of signal, not about a badly
configured baseline.
"""
from __future__ import annotations

import numpy as np


class Policy:
    name = "policy"

    def should_abandon(self, state) -> bool:
        raise NotImplementedError

    def describe(self) -> str:
        return self.name


class NeverAbandon(Policy):
    name = "never"

    def should_abandon(self, state):
        return False


class FailureStreak(Policy):
    """Abandon after K generations with no improvement of at least tol."""

    def __init__(self, k: int = 6, tol: float = 1e-3):
        self.k, self.tol = k, tol
        self.name = "streak_k" + str(k)

    def should_abandon(self, state):
        h = state["history"]
        if len(h) <= self.k:
            return False
        return (h[-1 - self.k] - h[-1]) < self.tol


class Plateau(Policy):
    """Abandon when best-so-far has moved less than delta over a window."""

    def __init__(self, window: int = 8, delta: float = 5e-3):
        self.window, self.delta = window, delta
        self.name = "plateau_w" + str(window)

    def should_abandon(self, state):
        h = state["history"]
        if len(h) <= self.window:
            return False
        return (h[-1 - self.window] - h[-1]) < self.delta


class Surrogate(Policy):
    """Fit the tail of the best-so-far curve and extrapolate its asymptote.

    Uses a simple three-parameter saturating fit  y = a - b * exp(-c t)  by least
    squares on the tail.  Abandons when the fitted asymptote a cannot reach the
    required in-band transmissibility.  This is the most plausible learned-style
    alternative to a certificate, so it is the interesting comparison.
    """

    def __init__(self, window: int = 10, margin: float = 0.98):
        self.window, self.margin = window, margin
        self.name = "surrogate_w" + str(window)

    def should_abandon(self, state):
        h = state["history"]
        if len(h) <= self.window:
            return False
        t = np.arange(self.window, dtype=float)
        y = np.array(h[-self.window:], dtype=float)
        best = np.inf
        for c in np.linspace(0.05, 2.0, 40):
            e = np.exp(-c * t)
            A = np.column_stack([np.ones_like(t), -e])
            coef, *_ = np.linalg.lstsq(A, y, rcond=None)
            resid = float(np.sum((A @ coef - y) ** 2))
            best = min(best, resid)
            if resid == best:
                asymptote = float(coef[0])
        target = -state["target_T"]         # objective is minus in-band |T|
        return asymptote < target * self.margin


def certificate_verdict(task, mechanism_class: str):
    """Three-valued, per CORE's tiering: infeasible / feasible / unknown.

    Infeasibility certificates are exact for M1 (the Lambda certificate).  The
    sky-hook DOES admit an exact decision procedure at L0, but it is withheld from
    these arms on purpose: using it would let the arm construct a witness directly,
    and the comparison would then measure construction rather than pruning.  It is
    reported separately and labelled.
    """
    from ..bench import m1_evidence
    if mechanism_class == "M1_passive_sdof":
        ev = m1_evidence(task)
        if ev["status"] == "proved_infeasible":
            return "infeasible", ev
        if ev["status"] == "feasible":
            return "feasible", ev
        return "unknown", ev
    return "unknown", {"status": "no certificate exists for this class"}


class CertificatePure(Policy):
    """Tier 1 only: prune on a proof, keep on a proof, otherwise never stop.

    This is the honest cost of soundness without a fallback, and it is included to
    show it: with no certificate for the intermediate class the arm has no way to
    leave it, and burns its budget there.
    """

    name = "certificate_pure"

    def __init__(self, task, mechanism_class: str):
        self.task = task
        self.mechanism_class = mechanism_class
        self._v = None

    def should_abandon(self, state):
        if self._v is None:
            self._v = certificate_verdict(self.task, self.mechanism_class)
        return self._v[0] == "infeasible"


class CertificateHybrid(Policy):
    """CORE's discipline: hard where certified, soft where not.

    infeasible -> abandon, hard (tier 1, sound, cached)
    feasible   -> keep, hard (tier 1)
    unknown    -> delegate to a soft, expiring heuristic (tier 3)

    This is the arm the ECDR thesis actually proposes after Finding 005: a
    certifier converts an expensive soft signal into a cheap hard one WHERE THE
    PHYSICS PERMITS, and elsewhere behaves like 2026 practice.
    """

    name = "certificate_hybrid"

    def __init__(self, task, mechanism_class: str, fallback=None):
        self.task = task
        self.mechanism_class = mechanism_class
        self.fallback = fallback or Surrogate()
        self._v = None
        self.used_certificate = None

    def should_abandon(self, state):
        if self._v is None:
            self._v = certificate_verdict(self.task, self.mechanism_class)
        verdict = self._v[0]
        if verdict == "infeasible":
            self.used_certificate = True
            return True
        if verdict == "feasible":
            self.used_certificate = True
            return False
        self.used_certificate = False
        return self.fallback.should_abandon(state)


class Oracle(Policy):
    """Upper bound: abandon a mechanism iff it is known NOT to be able to work.

    A first version compared against the MINIMAL feasible class, which was wrong:
    on a depth-2 task the minimal class is M2, but M3 also solves the task, so
    abandoning M3 threw away a working option and the oracle scored 0 percent at
    depth 2.  The oracle must know the feasibility map, not the minimum.
    """

    name = "oracle"

    def __init__(self, task, mechanism_class: str, feasibility=None):
        self.mechanism_class = mechanism_class
        self.feasibility = feasibility or {}

    def should_abandon(self, state):
        return not bool(self.feasibility.get(self.mechanism_class, False))


POLICY_FACTORY = {
    "never": lambda task, mech, minimal: NeverAbandon(),
    "streak": lambda task, mech, minimal: FailureStreak(),
    "plateau": lambda task, mech, minimal: Plateau(),
    "surrogate": lambda task, mech, minimal: Surrogate(),
    "certificate_pure": lambda task, mech, minimal: CertificatePure(task, mech),
    "certificate_hybrid": lambda task, mech, minimal: CertificateHybrid(task, mech),
    "oracle": lambda task, mech, feasibility: Oracle(task, mech, feasibility),
}

ARM_LABELS = {
    "never": "pure local refinement, never escapes",
    "streak": "heuristic: K non-improving generations",
    "plateau": "heuristic: best-so-far stalls over a window",
    "surrogate": "heuristic: extrapolate the best-so-far curve",
    "certificate_pure": "sound pruning only, no fallback",
    "certificate_hybrid": "hard where certified, soft elsewhere (ECDR proposal)",
    "oracle": "knows the ground-truth minimal mechanism (upper bound)",
}
