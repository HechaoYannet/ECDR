"""Step 74 - TWO ROUTES ON ONE COST AXIS, which is what Layer C requires and the harness lacks.

Roadmap section 6, Layer C, lines 368 to 370:

    Proved regions take budget zero; unproved regions take sampling budget; ... both live on
    ONE COST AXIS

Finding 049 recorded that the harness has a flat counter of physics calls and a single route, so
it cannot express a comparison at all. This builds the comparison for the certificate the project
actually has - C1, the modal certificate - and charges all three routes in SECONDS, measured on
the real code paths.

    route B  certificate   cost c_p + c_v,      concludes CERTAINLY on g(N) structures
    route C  enumeration   cost g(N) * c_s,     concludes the same, by evaluation
    route A  sampling      cost M * c_s,        concludes "not found yet", confidence 1/(M+1)

Section 5.3 compares B against C. Section 5.5 says A is the right tool wherever a probabilistic
negative suffices, and that A costs M = Theta(1/delta) INDEPENDENT of N. All three belong on the
same axis, and the regime decides which one is correct - not the method.
"""
import _bootstrap  # noqa: F401
import json
import pathlib
import time

from ecdr.structure.counting import space_size, structures_with_n_nodes

line = "=" * 100

# ---------------------------------------------------------------- measured constants
from ecdr.structure import ensemble
from ecdr.l0.feasibility import SEARCH_OMEGA

ens = ensemble(seed=11, count=40, n_lo=2, n_hi=9)
s0 = ens[0]

t0 = time.perf_counter()
for _ in range(400):
    s0.transmissibility(SEARCH_OMEGA)
c_s = (time.perf_counter() - t0) / 400

NCHK = 400000
t0 = time.perf_counter()
for _ in range(NCHK):
    _ = s0.mode_count() >= 3
c_v = (time.perf_counter() - t0) / NCHK

t0 = time.perf_counter()
for _ in range(2000):
    _ = sum(structures_with_n_nodes(k) for k in range(1, 11))
c_p = (time.perf_counter() - t0) / 2000

print(line)
print("MEASURED CONSTANTS (real code paths, charged in seconds)")
print(line)
print("  c_s  one structure evaluation        : " + format(c_s, ".6e") + " s")
print("  c_v  one certificate check           : " + format(c_v, ".6e") + " s")
print("  c_p  deriving the certificate, once  : " + format(c_p, ".6e") + " s")
print("  c_v / c_s = " + format(c_v / c_s, ".6f") + "   -- a check is four orders cheaper")
print()

M_TARGET = 3          # the requirement: a target with 3 harmonics
g_const = sum(structures_with_n_nodes(k) for k in range(1, M_TARGET))
print("  C1 rules out every structure with fewer than " + str(M_TARGET) + " modes.")
print("  mode_count() returns n, so that set is all structures with n < " + str(M_TARGET)
      + " masses:")
print("     g = " + str(g_const) + "   (1 + " + str(structures_with_n_nodes(2)) + ")")
print("  ** g does NOT depend on the family size. It is a constant. **")

# ---------------------------------------------------------------- the three routes
print()
print(line)
print("THE THREE ROUTES ON ONE AXIS")
print(line)
print("  " + "n".rjust(3) + "N(n)".rjust(24) + "g/N".rjust(13)
      + "B cert (s)".rjust(14) + "C enum (s)".rjust(14) + "B/C".rjust(10)
      + "A sample d=0.01".rjust(17))
rows = []
DELTA = 0.01
M = int(1.0 / DELTA)                 # Proposition 3: M = Theta(1/delta), independent of N
for n in range(3, 11):
    N = space_size(n)
    frac = g_const / N
    costB = c_p + c_v
    costC = g_const * c_s
    costA = M * c_s
    rows.append({"n": n, "N": int(N), "g": g_const, "fraction": frac,
                 "cost_cert": costB, "cost_enum": costC, "cost_sampling": costA})
    print("  " + str(n).rjust(3) + format(N, ".4e").rjust(24) + format(frac, ".3e").rjust(13)
          + format(costB, ".4e").rjust(14) + format(costC, ".4e").rjust(14)
          + format(costC / costB, ".4e").rjust(10) + format(costA, ".4e").rjust(17))

print()
print(line)
print("VERDICT")
print(line)
r = rows[-1]
print("  At n = " + str(r["n"]) + " (N = " + format(r["N"], ".3e") + " structures):")
print("    route B, certificate   : " + format(r["cost_cert"], ".3e") + " s, rules out "
      + str(g_const) + " structures with certainty")
print("    route C, enumeration   : " + format(r["cost_enum"], ".3e") + " s, the same set")
print("    route A, sampling      : " + format(r["cost_sampling"], ".3e") + " s, and it")
print("                             certifies NOTHING - at 100 draws the conclusion is still")
print("                             'not found yet'")
print()
print("  the certificate is " + format(r["cost_enum"] / r["cost_cert"], ".1f")
      + "x cheaper than enumerating what it covers.")
print("  and it is " + format(r["cost_sampling"] / r["cost_cert"], ".1f")
      + "x cheaper than sampling to delta = " + str(DELTA) + ".")
print()
print("  BUT the fraction it covers is " + format(r["fraction"], ".3e")
      + " and falling as N grows.")
print()
print("  Roadmap section 5.4, line 192:  Theta(1) absolute saving bounded, relative saving")
print("  -> 1, verdict: **no crossing ever; decoration**.")
print()
print("  ** C1 is in that row. ** g(N) is a constant - " + str(g_const) + " - so the relative")
print("  saving decays to 1 and the speedup is a factor of " + format(r["cost_enum"]
      / r["cost_cert"], ".1f") + " that never improves with scale.")
print()
print(line)
print("AND THIS IS WHY THE MEASURED THRESHOLD WAS DANGEROUS")
print(line)
thr = (c_p + c_v) / c_s
print("  the crossing condition of section 5.3 is  g(N) > (c_p + c_v)/c_s  =  "
      + format(thr, ".4e"))
print("  and g = " + str(g_const) + " clears it by a factor of "
      + format(g_const / thr, ".1f") + ".")
print()
print("  ** So the formal condition reports a crossing for a certificate that section 5.4")
print("  classifies as decoration. ** Condition 1 is satisfied by almost anything, because a")
print("  check is four orders of magnitude cheaper than an evaluation. The informative")
print("  quantity is condition 2 - whether g(N) is Theta(N) - and C1 fails it outright.")
print()
print("  Had the harness reported 'a crossing exists' from the measured constants alone, it")
print("  would have been reporting a true inequality that means nothing. That is the same")
print("  class of error as the empty-vs-failing confusion of Finding 036 and the vacuous")
print("  regime of Finding 025, one level up.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "two_routes.json").write_text(json.dumps({
    "c_s": c_s, "c_v": c_v, "c_p": c_p, "g_C1": g_const,
    "threshold": thr, "delta": DELTA, "M": M, "rows": rows,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/two_routes.json")
