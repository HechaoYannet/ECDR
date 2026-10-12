"""Smoke test: run the local-refinement baseline on one mechanism of one task."""
import _bootstrap  # noqa: F401
from ecdr.bench import (MechanismProblem, default_family_spec, make_family,
                        m1_evidence, m2_scan, m3_evidence, solve_within_mechanism)
from ecdr.l0 import PassiveSDOF, TunedMassDamper, SkyHookActive

spec = default_family_spec()
hard = spec.task(60.0)
print("task:", hard.name)
print("  M1 certificate:", m1_evidence(hard)["status"])
print("  M3 decision   :", m3_evidence(hard)["status"])
print()
for mech in (PassiveSDOF(), TunedMassDamper(), SkyHookActive()):
    p = MechanismProblem(hard, mech)
    r = solve_within_mechanism(p, seed=1, maxiter=60, popsize=12)
    print("  " + mech.name.ljust(22) + " obj=" + format(r["objective"], ".6f")
          + "  grid-feasible=" + str(r["feasible_by_grid"])
          + "  evals=" + str(r["evaluations"]))
    print("      constraints:", [round(c, 4) for c in r["constraints"]])