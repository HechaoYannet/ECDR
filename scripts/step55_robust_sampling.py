"""Step 55 - is robust_violation's sampled worst case the ACTUAL worst case?

The concern
-----------
Finding 008's false-positive zone, 172.34 < f_low < 239.72 Hz, comes from step15, which
called

    robust_violation(m1, p, task, SEARCH_OMEGA, rel=0.10, n=12, seed=3)

That function draws n random points in a +-10 percent box around p and returns the MAXIMUM
violation over them.  It is therefore a LOWER BOUND on the true worst case over the box.

If the true worst case is worse, then a design can be declared robust when it is not, and
the real threshold is HIGHER than 239.72 - meaning the false-positive zone is WIDER than
reported.  The direction of the error is known in advance even if its size is not, which is
what makes this testable.

The test
--------
For designs that the original method declares robust, compare the n = 12 sampled maximum
against a dense search of the same box that includes the four corners, many random points,
and a local refinement from the best of them.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.l0 import G, IsolationTask, PassiveSDOF, certify_passive_sdof
from ecdr.l0.feasibility import SEARCH_OMEGA
from ecdr.l1 import robust_violation

line = "=" * 92
m1 = PassiveSDOF()


def l0_feasible(task, p):
    T = np.abs(m1.transmissibility(SEARCH_OMEGA, p))
    band = SEARCH_OMEGA >= task.omega_low
    return (T[band].max() <= task.T_iso and T.max() <= task.A_max
            and m1.static_deflection(p) <= task.delta_max)


def violation_at(mech, p, task, omega):
    T = np.abs(mech.transmissibility(omega, p))
    band = omega >= task.omega_low
    v = [float(T[band].max() / task.T_iso - 1.0),
         float(T.max() / task.A_max - 1.0),
         float(mech.static_deflection(p) / task.delta_max - 1.0)]
    if task.force_per_disp_max is not None:
        F = np.abs(mech.actuator_force_per_disp(omega, p))
        v.append(float(F.max() / task.force_per_disp_max - 1.0))
    return max(v)


def dense_violation(mech, p, task, rel, n_big=4000, seed=99, refine=True):
    """Worst violation over the box by corners + many random points + local refinement."""
    p = np.asarray(p, dtype=float)
    hard_lo = np.array([b[0] for b in mech.param_bounds], dtype=float)
    hard_hi = np.array([b[1] for b in mech.param_bounds], dtype=float)
    # The box under test is the PERTURBATION box, intersected with the hard parameter
    # bounds.  Clipping the search to the hard bounds instead lets the refinement walk to
    # wn = 400, zeta = 2.0 for a nominal of (110.5, 0.596) - far outside a +-10 percent box
    # - and report an out-of-box point as the worst case.
    lo = np.maximum(p * (1.0 - rel), hard_lo)
    hi = np.minimum(p * (1.0 + rel), hard_hi)
    rng = np.random.default_rng(seed)
    cands = []
    for a in (1 - rel, 1 + rel):
        for b in (1 - rel, 1 + rel):
            cands.append(np.clip(p * np.array([a, b]), lo, hi))
    F = 1.0 + rel * (2.0 * rng.random((n_big, p.size)) - 1.0)
    cands.extend(np.clip(p * F, lo, hi))
    vals = [violation_at(mech, q, task, SEARCH_OMEGA) for q in cands]
    best = float(np.max(vals))
    bestp = cands[int(np.argmax(vals))]
    if refine:
        # coordinate-wise shrinking search from the best point found
        step = rel / 2.0
        cur, curv = np.array(bestp, dtype=float), best
        for _ in range(40):
            improved = False
            for k in range(p.size):
                for sgn in (1.0, -1.0):
                    q = cur.copy()
                    q[k] = np.clip(q[k] * (1.0 + sgn * step), lo[k], hi[k])
                    v = violation_at(mech, q, task, SEARCH_OMEGA)
                    if v > curv:
                        cur, curv, improved = q, v, True
            if not improved:
                step /= 2.0
                if step < 1e-5:
                    break
    inside = bool(np.all(cur >= lo - 1e-12) and np.all(cur <= hi + 1e-12))
    if not inside:
        raise AssertionError("refinement left the perturbation box: " + str(cur))
    return best, curv, cur


def best_robust_design(task, rel, n_pert, seed):
    wn_min = float(np.sqrt(G / task.delta_max))
    for wn in np.linspace(wn_min, 3.0 * wn_min, 70):
        for z in np.concatenate([np.linspace(0.35, 1.5, 90), np.linspace(1.55, 3.5, 40)]):
            p = (wn, float(z))
            if not l0_feasible(task, p):
                continue
            if robust_violation(m1, p, task, SEARCH_OMEGA, rel=rel, n=n_pert, seed=3) <= 0.0:
                return p
    return None


print(line)
print("A. reproduce the original threshold, then stress the designs it accepts")
print(line)
print("  " + "f_low Hz".rjust(10) + "design (wn, zeta)".rjust(24) + "n=12 max".rjust(12)
      + "dense max".rjust(12) + "difference".rjust(12) + "  verdict".rjust(12))
rows = []
for f in (200.0, 220.0, 239.72, 250.0, 270.0, 300.0):
    task = IsolationTask("probe", f, -20.0, 3.0, 1.0e-3)
    p = best_robust_design(task, 0.10, 12, seed=3)
    if p is None:
        print("  " + format(f, ".2f").rjust(10) + "        no robust design found".rjust(24))
        continue
    sampled = robust_violation(m1, p, task, SEARCH_OMEGA, rel=0.10, n=12, seed=3)
    dense, refined, at = dense_violation(m1, p, task, 0.10)
    flip = dense > 0.0
    rows.append({"f_low": f, "wn": p[0], "zeta": p[1], "sampled": sampled,
                 "dense": dense, "refined": refined, "at": [float(at[0]), float(at[1])],
                 "flips": bool(flip)})
    print("  " + format(f, ".2f").rjust(10)
          + ("(" + format(p[0], ".2f") + ", " + format(p[1], ".3f") + ")").rjust(24)
          + format(sampled, ".4e").rjust(12) + format(dense, ".4e").rjust(12)
          + format(dense - sampled, ".4e").rjust(12)
          + ("   VIOLATES" if flip else "   holds").rjust(12))

print()
print(line)
print("B. what the dense search finds that the sample misses")
print(line)
n_flip = sum(1 for r in rows if r["flips"])
print("  designs the n=12 sampling called robust : " + str(len(rows)))
print("  of those, actually violating the box    : " + str(n_flip))
if rows:
    gaps = [r["dense"] - r["sampled"] for r in rows]
    print("  sampled-vs-dense gap, min / max         : " + format(min(gaps), ".4e")
          + " / " + format(max(gaps), ".4e"))
    worst = max(rows, key=lambda r: r["dense"])
    print()
    print("  worst case: f_low = " + format(worst["f_low"], ".1f")
          + ", sampled " + format(worst["sampled"], ".4e")
          + ", dense " + format(worst["dense"], ".4e"))
    print("    the dense worst point is at wn = " + format(worst["at"][0], ".5f")
          + ", zeta = " + format(worst["at"][1], ".5f")
          + "  (nominal " + format(worst["wn"], ".5f") + ", " + format(worst["zeta"], ".5f") + ")")

print()
print(line)
print("C. VERDICT")
print(line)
if n_flip:
    print("  The n = 12 sampling UNDERSTATES the worst case, and designs it certifies as")
    print("  robust actually violate the box.  The true threshold is higher than 239.72 Hz,")
    print("  so the false-positive zone of Finding 008 is WIDER than reported, in the")
    print("  direction predicted before the test was run.")
else:
    print("  The n = 12 sampling is adequate on this box: no design it certifies as robust")
    print("  fails the dense search.  Finding 008's threshold stands as computed.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "robust_sampling_check.json").write_text(json.dumps({
    "rows": rows, "n_flips": n_flip,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/robust_sampling_check.json")
