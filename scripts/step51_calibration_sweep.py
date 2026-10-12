"""Step 51 - sweeping the calibration: where does the library stop working?

Finding 024 found that a tight calibration depletes the space before the library finishes
its members - after three cuts at the 30th percentile only about one structure of 600
remained - but it could not say where the boundary lies, because the four thresholds were
tied to a single percentile in a way that made their marginals move in different
directions.

This sweeps a single tightness parameter.  For each target marginal f, every certificate
rules out exactly the f-fraction of the space its own ordering selects:

    C1 modal     the f-fraction with the FEWEST components
    C2 statics   the f-fraction with the LARGEST sag
    C3 slow      the f-fraction with the LARGEST omega_1^2 bound
    C4 fast      the f-fraction with the SMALLEST omega_n^2 bound

so all four marginals are exactly f by construction.  The quantity that decides whether the
library works is the SEQUENTIAL CONDITIONAL - the fraction of what remains that the next
certificate takes - and the figure of merit is the per-round survival, since

    rounds for N  =  log N / log( 1 / survival )

is what has to stay small.  Sweeping f asks: is there an optimum, and where does the
mechanism fail on either side?
"""
import _bootstrap  # noqa: F401
import json
import math
import pathlib

import numpy as np

from ecdr.structure import ensemble

line = "=" * 94
N = 800


def fast_bound(s):
    M, C, K, f, g = s.matrices()
    return float(np.max(np.abs(K).sum(axis=1) / np.diag(M)))


def quantities(ens):
    n = np.array([s.n for s in ens], dtype=float)
    sag = np.array([s.static_deflection() for s in ens])
    slow = np.array([sum(s.ground_k.values()) / s.masses.sum() for s in ens])
    fast = np.array([fast_bound(s) for s in ens])
    return n, sag, slow, fast


def rank_cut(values, f, largest):
    """Rule out exactly the f-fraction at the given end of the ordering."""
    order = np.argsort(values)
    if largest:
        order = order[::-1]
    k = int(round(f * len(values)))
    mask = np.zeros(len(values), dtype=bool)
    mask[order[:k]] = True
    return mask


def sweep(n_max, seed, extra_edges=0, value_dist="log"):
    ens = ensemble(seed=seed, count=N, n_lo=2, n_hi=n_max,
                   extra_edges=extra_edges, value_dist=value_dist)
    n, sag, slow, fast = quantities(ens)
    rows = []
    for f in np.arange(0.1, 0.95, 0.1):
        cuts = [rank_cut(n, f, False), rank_cut(sag, f, True),
                rank_cut(slow, f, True), rank_cut(fast, f, False)]
        names = ["C1 modal", "C2 statics", "C3 slow", "C4 fast"]
        remain = np.ones(N, dtype=bool)
        seq = []
        for nm, c in zip(names, cuts):
            before = int(remain.sum())
            remain = remain & ~c
            after = int(remain.sum())
            cond = 1 - after / max(before, 1)
            seq.append({"cut": nm, "conditional": float(cond), "remaining": after})
        surv = float(remain.mean())
        kk = math.log(1e10) / math.log(1 / surv) if 0 < surv < 1 else float("inf")
        rows.append({"f": float(f), "sequence": seq, "survival": surv,
                     "rounds_1e10": kk, "certificates": 4 * kk,
                     "final_count": int(remain.sum())})
    return rows


print(line)
print("A. original family, marginal cut f swept from 0.1 to 0.9")
print(line)
print("  " + "f".rjust(5) + "f2|1".rjust(9) + "f3|1,2".rjust(10) + "f4|1,2,3".rjust(11)
      + "survival".rjust(11) + "left of 800".rjust(13) + "rounds 1e10".rjust(13)
      + "certs".rjust(8))
rows_a = sweep(8, 105)
for r in rows_a:
    s = r["sequence"]
    print("  " + format(r["f"], ".1f").rjust(5)
          + format(s[1]["conditional"], ".4f").rjust(9)
          + format(s[2]["conditional"], ".4f").rjust(10)
          + format(s[3]["conditional"], ".4f").rjust(11)
          + format(r["survival"], ".5f").rjust(11)
          + str(r["final_count"]).rjust(13)
          + format(r["rounds_1e10"], ".2f").rjust(13)
          + format(r["certificates"], ".0f").rjust(8))

print()
print(line)
print("B. new family (loops, uniform values, n to 7)")
print(line)
print("  " + "f".rjust(5) + "f2|1".rjust(9) + "f3|1,2".rjust(10) + "f4|1,2,3".rjust(11)
      + "survival".rjust(11) + "left of 800".rjust(13) + "rounds 1e10".rjust(13)
      + "certs".rjust(8))
rows_b = sweep(7, 900, extra_edges=2, value_dist="uniform")
for r in rows_b:
    s = r["sequence"]
    print("  " + format(r["f"], ".1f").rjust(5)
          + format(s[1]["conditional"], ".4f").rjust(9)
          + format(s[2]["conditional"], ".4f").rjust(10)
          + format(s[3]["conditional"], ".4f").rjust(11)
          + format(r["survival"], ".5f").rjust(11)
          + str(r["final_count"]).rjust(13)
          + format(r["rounds_1e10"], ".2f").rjust(13)
          + format(r["certificates"], ".0f").rjust(8))

print()
print(line)
print("C. where the mechanism works")
print(line)
for tag, rows in (("original", rows_a), ("new", rows_b)):
    ok = [r for r in rows if min(x["conditional"] for x in r["sequence"][1:]) > 0.1
          and r["final_count"] >= 20]
    if ok:
        best = min(ok, key=lambda r: r["rounds_1e10"])
        print("  " + tag.ljust(9)
              + "usable f range: " + format(min(r["f"] for r in ok), ".1f") + " to "
              + format(max(r["f"] for r in ok), ".1f")
              + "   best f = " + format(best["f"], ".1f")
              + "  rounds " + format(best["rounds_1e10"], ".2f")
              + "  certificates " + format(best["certificates"], ".0f"))
    else:
        print("  " + tag.ljust(9) + "no f in the sweep left a usable space")
print()
print("  The failure on the tight side is DEPLETION: the certificates between them remove")
print("  so much that later members find nothing to cut, and their conditionals are then")
print("  measured on a handful of structures.  The failure on the loose side is the opposite")
print("  - each certificate is cheap but takes little, so more rounds are needed.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "calibration_sweep.json").write_text(json.dumps(
    {"original": rows_a, "new_family": rows_b}, indent=1), encoding="utf-8")
print()
print("wrote runs/calibration_sweep.json")
