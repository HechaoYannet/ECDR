"""Step 75 - the library on the cost axis, and why c_v is not one number.

Roadmap section 5.3, Proposition 2, writes the certificate route as c_p + c_v - ONE check cost
and ONE derivation cost, as if a certificate were a certificate. Section 5.4 line 181 then gives
the library result

    k = O( log N / log(1/(1-f)) )

so the library's cost is treated as k * (c_p + c_v) against N * c_s for enumeration. The count
grows additively per decade of N while sampling grows multiplicatively, which is the whole claim.

**Both expressions hide that the four certificates have check costs differing by orders of
magnitude.** The modal check compares one integer; the statics check builds K and solves a linear
system. If a check costs what an evaluation costs, applying it to k structures can cost more than
evaluating them, and the crossing inverts.

This measures each check on the real code paths and then charges the library SEQUENTIALLY - as it
is actually applied, each certificate only to the survivors of the ones before it.
"""
import _bootstrap  # noqa: F401
import json
import pathlib
import time

import numpy as np

from ecdr.l0.feasibility import SEARCH_OMEGA
from ecdr.structure import ensemble

line = "=" * 100
N_SAMPLES = 400
ens = ensemble(seed=101, count=N_SAMPLES, n_lo=2, n_hi=8)
print(line)
print("THE FOUR CHECKS, each timed on " + str(len(ens)) + " structures")
print(line)


def cut_modal(s, tau):
    return s.n < tau


def cut_statics(s, tau):
    return s.static_deflection() > tau


def cut_slow(s, tau):
    return sum(s.ground_k.values()) / s.masses.sum() > tau


def cut_fast(s, tau):
    return fast_bound(s) > tau


def fast_bound(s):
    """omega_n^2 <= max_i (K_ii + sum_{j!=i} |K_ij|) / m_i, computed row by row."""
    M, C, K, f, g = s.matrices()
    best = -np.inf
    for i in range(s.n):
        row = abs(K[i, :]).sum()
        best = max(best, (K[i, i] + (row - abs(K[i, i]))) / M[i, i])
    return float(best)


def timed(fn, reps=5):
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t0)
    return min(ts) / len(ens)


t0 = time.perf_counter()
for _ in range(5):
    for s in ens:
        s.transmissibility(SEARCH_OMEGA)
c_s = (time.perf_counter() - t0) / (5 * len(ens))

m_med = float(np.median([s.n for s in ens]))
sag_med = float(np.median([s.static_deflection() for s in ens]))
slow_med = float(np.median([sum(s.ground_k.values()) / s.masses.sum() for s in ens]))
fast_med = float(np.median([fast_bound(s) for s in ens]))

def run_modal():
    for s in ens: cut_modal(s, m_med)
def run_statics():
    for s in ens: cut_statics(s, sag_med)
def run_slow():
    for s in ens: cut_slow(s, slow_med)
def run_fast():
    for s in ens: cut_fast(s, fast_med)

cvs = {"modal": timed(run_modal), "statics": timed(run_statics),
       "slow": timed(run_slow), "fast": timed(run_fast)}

print("  " + "certificate".rjust(12) + "c_v per structure".rjust(19) + "c_v / c_s".rjust(12)
      + "   what the check does")
desc = {"modal": "reads an integer attribute",
        "statics": "builds K and solves K x = m g",
        "slow": "sums ground stiffnesses and masses",
        "fast": "builds K and takes row sums"}
for k in ("modal", "statics", "slow", "fast"):
    print("  " + k.rjust(12) + format(cvs[k], ".6e").rjust(19)
          + format(cvs[k] / c_s, ".6f").rjust(12) + "   " + desc[k])
print()
print("  c_s, one full transmissibility evaluation : " + format(c_s, ".6e") + " s")
print()
lo, hi = min(cvs.values()), max(cvs.values())
print("  ** the four check costs span a factor of " + format(hi / lo, ".1f") + " **")
print("  and the dearest is " + format(hi / c_s, ".4f") + " of a full evaluation.")

print()
print(line)
print("THE LIBRARY, charged SEQUENTIALLY - each certificate only to what survived the last")
print(line)
alive = np.ones(len(ens), dtype=bool)
seq = [("modal", cut_modal, m_med), ("statics", cut_statics, sag_med),
       ("slow", cut_slow, slow_med), ("fast", cut_fast, fast_med)]
t0 = time.perf_counter()
print("  " + "step".rjust(10) + "applied to".rjust(12) + "cut".rjust(8) + "cost (s)".rjust(12)
      + "cumulative (s)".rjust(15))
cum = 0.0
detail = []
for name, fn, tau in seq:
    n_alive = int(alive.sum())
    t1 = time.perf_counter()
    for i, s in enumerate(ens):
        if alive[i] and fn(s, tau):
            alive[i] = False
    dt = time.perf_counter() - t1
    cum += dt
    detail.append({"cert": name, "applied_to": n_alive, "cost": dt, "cumulative": cum})
    print("  " + name.rjust(10) + str(n_alive).rjust(12) + str(int((~alive).sum())).rjust(8)
          + format(dt, ".6e").rjust(12) + format(cum, ".6e").rjust(15))
survivors = int(alive.sum())
print()
print("  survivors " + str(survivors) + " of " + str(len(ens)) + "   ->  fraction survived "
      + format(survivors / len(ens), ".4f"))
print("  the whole library, sequential, on " + str(len(ens)) + " structures : "
      + format(cum, ".6e") + " s")
print("  the same " + str(len(ens)) + " structures by full evaluation          : "
      + format(len(ens) * c_s, ".6e") + " s")
print("  ratio library / evaluation : " + format(cum / (len(ens) * c_s), ".6f"))

print()
print(line)
print("VERDICT")
print(line)
print("  What section 5.3 assumes   :  library cost = k * (c_p + c_v),  one c_v for all")
print("  What is measured           :  c_v ranges over a factor of "
      + format(hi / lo, ".1f") + " across the four")
print("  and the sequential cost is :  " + format(cum, ".6e") + " s against "
      + format(len(ens) * c_s, ".6e") + " s by evaluation")
print()
if cum < len(ens) * c_s:
    print("  The library is cheaper than evaluating the same structures - but by a factor of")
    print("  " + format(len(ens) * c_s / cum, ".2f") + ", NOT by the factor k * c_v / (N * c_s) that")
    print("  a single averaged c_v would predict.")
else:
    print("  ** The library is MORE EXPENSIVE than evaluating the same structures. **")
    print("  A check that costs what an evaluation costs cannot buy anything by being applied")
    print("  to the same structures - and c_p + c_v hides that.")

print()
print("  The structural point: the modal check is free because the mode count is an")
print("  attribute; the other three recompute something from the matrices. The cheap one")
print("  is the one Finding 050 classified as decoration, and the expensive ones are the")
print("  ones that actually cover a constant fraction.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "library_cost.json").write_text(json.dumps({
    "c_s": c_s, "c_v": cvs, "sequential": detail,
    "library_total": cum, "enumeration_total": len(ens) * c_s,
    "survivors": survivors, "n": len(ens),
}, indent=1), encoding="utf-8")
print()
print("wrote runs/library_cost.json")
