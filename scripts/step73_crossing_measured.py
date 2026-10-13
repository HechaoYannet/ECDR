"""Step 73 - the crossing with MEASURED constants, not asserted ones.

Roadmap section 5.3, Proposition 2:

    cost to certainly rule out C_N by evaluation  =  Theta(g(N) * c_s)
    cost to certainly rule out C_N by certificate =  c_p + c_v
    certification is cheaper exactly when  g(N) > (c_p + c_v) / c_s

Section 5.6 lists Proposition 2 as "provable algebra", which it is. But the algebra has never been
evaluated against MEASURED values of c_p, c_v and c_s, and Finding 049 recorded that without a cost
axis none of the harness work could be evidence for the crossing. This measures the three constants
on the real code paths and evaluates the condition.

    c_s  one structure evaluation            Structure.transmissibility over the search grid
    c_v  one certificate CHECK on a structure  mode_count() compared against the bound
    c_p  deriving the certificate for a family the counting argument, once

The certificate is C1 from the roadmap section 6 table: a structure with fewer than m independent
modes cannot produce m harmonics, so every topology with n < m is ruled out.
"""
import _bootstrap  # noqa: F401
import json
import pathlib
import statistics
import time

import numpy as np

from ecdr.l0.feasibility import SEARCH_OMEGA
from ecdr.structure import ensemble
from ecdr.structure.counting import structures_with_n_nodes

line = "=" * 96


def timeit(fn, repeat=7):
    """Median wall time, with the spread reported so a difference cannot be noise."""
    ts = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t0)
    return statistics.median(ts), min(ts), max(ts)


ens = ensemble(seed=11, count=60, n_lo=2, n_hi=9)
print(line)
print("MEASURED COST CONSTANTS  (median of 7, on the real code paths)")
print(line)

# --- c_s: evaluating one structure ------------------------------------------------
sample = ens[:20]


def one_eval():
    for s in sample:
        s.transmissibility(SEARCH_OMEGA)


def one_eval_once():
    sample[0].transmissibility(SEARCH_OMEGA)


cs_total, cs_lo, cs_hi = timeit(one_eval)
c_s, cs_lo1, cs_hi1 = timeit(one_eval_once, repeat=51)
print("  c_s  one transmissibility evaluation over the search grid")
print("       per structure : " + format(c_s, ".6e") + " s   (min "
      + format(cs_lo1, ".3e") + ", max " + format(cs_hi1, ".3e") + ")")
print("       cross-check   : " + format(cs_total / len(sample), ".6e") + " s per structure over "
      + str(len(sample)) + " structures")

# --- c_v: CHECKING the certificate on one structure --------------------------------
# Measured in a BATCH. A single check is a comparison against an integer attribute and came
# out at "1e-7 s with a minimum of 0.0", which is the timer's resolution, not the cost. A
# constant quoted from a measurement below the clock's resolution is not a measurement.
CHECK_BATCH = 200000


def one_check():
    s = sample[0]
    for _ in range(CHECK_BATCH):
        n_modes = s.mode_count()      # what the checker computes
        _ = n_modes >= 3              # compared against the claimed bound m = 3


t0 = time.perf_counter()
one_check()
elapsed = time.perf_counter() - t0
c_v = elapsed / CHECK_BATCH
print("  c_v  one certificate check on one structure")
print("       : " + format(c_v, ".6e") + " s   (from " + str(CHECK_BATCH)
      + " checks in " + format(elapsed, ".4f") + " s)")
print("       ONE check alone is below the timer resolution, so it is measured in a batch.")

# --- c_p: DERIVING the certificate for a family -------------------------------------
# The modal certificate's argument is a counting statement: n degrees of freedom admit at
# most n independent harmonics, so every topology with n < m is excluded. Deriving it means
# enumerating the excluded family's SIZE, which is the counting function.
def derive_family(m_max=11):
    # A001187 is tabulated to n = 10; above that the count is not available and the function
    # raises rather than returning a wrong number.
    total = sum(structures_with_n_nodes(n) for n in range(1, m_max))


c_p, cp_lo, cp_hi = timeit(derive_family, repeat=51)
print("  c_p  deriving the certificate once, over the whole family")
print("       : " + format(c_p, ".6e") + " s   (min " + format(cp_lo, ".3e")
      + ", max " + format(cp_hi, ".3e") + ")")

print()
print(line)
print("g(N): how many structures the certificate rules out")
print(line)
print("  " + "n".rjust(4) + "structures_with_n_nodes".rjust(26) + "cumulative g(N)".rjust(20))
cum = 0
rows = []
for n in range(1, 11):
    c = structures_with_n_nodes(n)
    cum += c
    rows.append({"n": n, "count": int(c), "g_N": int(cum)})
    if True:
        print("  " + str(n).rjust(4) + str(int(c)).rjust(26) + str(int(cum)).rjust(20))

print()
print(line)
print("PROPOSITION 2, evaluated with the measured constants")
print(line)
c_s_eff = c_s
threshold_small = (c_p + c_v) / c_s_eff
print("  c_s = " + format(c_s, ".6e") + " s      c_v = " + format(c_v, ".6e")
      + " s      c_p = " + format(c_p, ".6e") + " s")
print("  c_v / c_s = " + format(c_v / c_s, ".4f")
      + "     (how much dearer a check is than an evaluation)")
print()
print("  crossing condition:  g(N)  >  (c_p + c_v) / c_s  =  "
      + format(threshold_small, ".6e"))
print()
print("  " + "n".rjust(4) + "g(N)".rjust(22) + "  crossing?".rjust(12))
first = None
for r in rows:
    cross = r["g_N"] > threshold_small
    if cross and first is None:
        first = r["n"]
    if True:
        print("  " + str(r["n"]).rjust(4) + format(r["g_N"], ".4e").rjust(22)
              + ("   YES" if cross else "   no").rjust(12))
print()
if first:
    print("  g(N) overtakes the threshold at n = " + str(first))
    print()
    print("  So from n = " + str(first) + " upward the certificate is cheaper than evaluation,")
    print("  and the margin grows without bound because g(N) is exponential in n while")
    print("  (c_p + c_v)/c_s is a CONSTANT fixed by the machine and the code paths.")

print()
print(line)
print("what this is and is not")
print(line)
print("  IS : Proposition 2 evaluated against measured wall-clock constants on the real code")
print("       paths, with the spread shown so the constants are not point guesses.")
print("  NOT: a demonstration that the agent USES the certificate. This measures the cost")
print("       side only. The search side has not been run against the same structures.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "crossing_measured.json").write_text(json.dumps({
    "c_s": c_s, "c_s_min": cs_lo1, "c_s_max": cs_hi1,
    "c_v": c_v, "c_v_batch": CHECK_BATCH,
    "c_p": c_p, "c_p_min": cp_lo, "c_p_max": cp_hi,
    "threshold": threshold_small, "g_N": rows, "first_crossing_n": first,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/crossing_measured.json")
