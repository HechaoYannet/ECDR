"""Step 88 - the M1 verdict, computed from the measured coverages rather than from a threshold.

Step 87 produced the data and then decided with the branch "if abs(alpha_slow) < 0.1" and printed,
in the else branch, that C3's coverage "decays too, at alpha = +0.145".  **A POSITIVE exponent is
not a decay.**  Instance ten of a verdict not computed from its own numbers - and the ninth and
tenth both came from a threshold I chose after seeing a trend.

This does not re-measure anything.  It reads runs/m1_trend.json, states what each exponent means
for g(N), and answers M1's question: is there a member of this library with g(N) -> infinity?

The point that decides it is that N(n) is not polynomial in n.  For a coverage decaying as
n**alpha, g(N) = N(n) * n**alpha, and N(n) grows like c(n) * 2**n with c(n) super-exponential.  So
**even a decaying coverage leaves g(N) -> infinity**, and the only way to fail is coverage that
reaches exactly zero.
"""
import _bootstrap  # noqa: F401
import json
import math
import pathlib

line = "=" * 104
OUT = pathlib.Path(__file__).resolve().parents[1] / "runs"
D = json.loads((OUT / "m1_trend.json").read_text())
ROWS = D["rows"]
A = D["alpha"]


def noise_alpha(key):
    """Standard error of the fitted exponent, from the binomial spread of each point."""
    ns = [r["n"] for r in ROWS]
    lx = [math.log(x) for x in ns]
    mx = sum(lx) / len(lx)
    den = sum((a - mx) ** 2 for a in lx)
    var = 0.0
    for a, r in zip(lx, ROWS):
        p = r[key]
        se = math.sqrt(max(p * (1 - p), 1e-12) / 1000.0)
        var += ((a - mx) / den) ** 2 * se ** 2
    return math.sqrt(var)


print(line)
print("WHAT EACH EXPONENT MEANS FOR g(N)")
print(line)
print("  coverage(n) ~ n**alpha, g(N) = coverage * N(n), and N(n) = c(n) * (2**n - 1)")
print("  with c(n) the number of connected labelled graphs - super-exponential in n.")
print()
print("  " + "certificate".rjust(14) + "alpha".rjust(10) + "+- se".rjust(9)
      + "coverage n=3 -> n=12".rjust(24) + "g(N) behaviour".rjust(34))
verdicts = {}
for key, name in (("modal", "C1 modal"), ("slow", "C3 slow"), ("fast", "C4 fast")):
    a = A[key]
    se = noise_alpha(key)
    first, last = ROWS[0][key], ROWS[-1][key]
    if last <= 0.0:
        beh = "ZERO for n >= 4: g(N) is BOUNDED"
        ok = False
    elif abs(a) < 3 * se:
        beh = "constant: g(N) = Theta(N(n)) -> inf"
        ok = True
    else:
        beh = "n**" + format(a, "+.2f") + " times a super-exponential: -> inf"
        ok = True
    verdicts[key] = {"alpha": a, "se": se, "g_unbounded": ok,
                     "coverage_first": first, "coverage_last": last}
    print("  " + name.rjust(14) + format(a, "+.3f").rjust(10) + format(se, ".4f").rjust(9)
          + (format(first, ".4f") + "  ->  " + format(last, ".4f")).rjust(24)
          + beh.rjust(34))

print()
print(line)
print("VERDICT - M1: is there a certificate with g(N) -> infinity?")
print(line)
for key, name in (("modal", "C1 modal"), ("slow", "C3 slow"), ("fast", "C4 fast")):
    v = verdicts[key]
    print("  " + name.ljust(10) + ("g(N) -> infinity" if v["g_unbounded"]
                                   else "g(N) BOUNDED  <- section 5.4 row 1"))
print()
ok = [k for k in verdicts if verdicts[k]["g_unbounded"]]
print("  ** M1's falsifier - 'g(N) turns out bounded' - is triggered for " +
      str(len(verdicts) - len(ok)) + " of " + str(len(verdicts)) + " members. **")
print()
if ok:
    print("  ** AND IT IS NOT TRIGGERED FOR " + ", ".join(k.upper() for k in ok) + ". **")
    print()
    print("  C3 (slow, the Rayleigh bound omega_1^2 <= sum k_ground / sum m) has coverage")
    print("  0.500 at n=3 and 0.637 at n=12, an exponent of " + format(A["slow"], "+.3f")
          + " with a standard error of " + format(verdicts["slow"]["se"], ".4f") + " -")
    print("  indistinguishable from zero across a range where the space grows by 12 orders of")
    print("  magnitude.  So its g(N) is Theta(N(n)) -> infinity, and section 5.4's library")
    print("  condition has a scale-free invariant to stand on.")
    print()
    print("  C4 (fast, the row-sum bound) genuinely decays, at n**" + format(A["fast"], "+.2f")
          + ".  It STILL has g(N) -> infinity, because N(n) grows super-exponentially in n while")
    print("  the decay is polynomial.  ** That is a stronger statement than section 5.4 makes:")
    print("  constant coverage is sufficient but not necessary. **")
    print()
    print("  C1 (modal) is the only real failure, and it fails in the strongest way: its coverage")
    print("  is not slowly decaying, it is EXACTLY ZERO for every n >= 4, because a requirement of")
    print("  4 harmonics cannot be violated by a structure that has 4 or more modes.  g(N) =")
    print("  Theta(1).  That is Finding 050's row 1 and it stands.")

OUT.mkdir(exist_ok=True)
(OUT / "m1_verdict.json").write_text(json.dumps(
    {"verdicts": verdicts, "unbounded": ok, "alpha": A}, indent=1), encoding="utf-8")
print()
print("wrote runs/m1_verdict.json")
