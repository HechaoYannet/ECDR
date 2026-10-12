"""Task family for the L0 precision-positioning testbed.

A task is the requirement; a mechanism class is the candidate design space.  The
pair (task, mechanism) is the analogue of a BOCoDe problem: a fixed formulation
with a parameter vector, an objective and constraints.  BOCoDe has no mechanism
axis at all, which is precisely the gap this registry fills.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..l0 import G, IsolationTask

# The mechanism inventory.  Order matters: it defines escape depth, the smallest
# index that can solve a task.
MECHANISM_ORDER = ("M1_passive_sdof", "M2_tuned_mass_damper", "M3_sky_hook_active")


@dataclass(frozen=True)
class FamilySpec:
    """Constants held fixed across the family; only f_low varies."""

    T_iso_db: float = -20.0
    A_max_db: float = 3.0
    delta_mm: float = 1.0
    force_budget_mult: float = 2.0

    def task(self, f_low: float) -> IsolationTask:
        delta = self.delta_mm / 1e3
        wn_min_sq = G / delta
        name = "T_f" + format(f_low, "g") + "_Tm" + format(abs(self.T_iso_db), "g") \
               + "_Ap" + format(self.A_max_db, "g")
        return IsolationTask(
            name=name,
            f_low=float(f_low),
            T_iso_db=self.T_iso_db,
            A_max_db=self.A_max_db,
            delta_max=delta,
            force_per_disp_max=self.force_budget_mult * wn_min_sq,
        )


def default_family_spec() -> FamilySpec:
    return FamilySpec()


def make_family(f_lows, spec: FamilySpec | None = None):
    spec = spec or FamilySpec()
    return [spec.task(f) for f in f_lows]
