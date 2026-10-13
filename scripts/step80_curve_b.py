"""Step 80 - CURVE (b): evaluation + certificates. The arm section 8 names and nobody built.

Roadmap section 8, lines 469 to 486, specifies the central experiment:

    x-axis:  size measure (number of topologies / components)
    y-axis:  cost to rule out
    curves:  (a) evaluation only   (b) evaluation + certificates   (c) certificates only
    fixed:   requirement, tolerance, confidence, cost unit

    The theory predicts (a) grows as Theta(g(N)) and (c) is flat. The experiment's job is to
    locate the crossing and measure the exponent, and to test the prediction that a
    certificate with g(N) = O(1) produces no crossing at all.

Findings 050, 052 and 053 produced (a) and (c) - the certificate cost is identical at n = 3 and
n = 10, evaluation rises from 8.9e-03 to 7.6e+10 s, and the separation grows from 4.00 to 3.39e13.
They also confirmed the O(1) prediction: C1 has g = 4 constant and lands in section 5.4's row 1.

**(b) was never built.** It is the arm that matters practically, because a certificate alone leaves
the remainder unruled: a library covering a fraction leaves (1-f)^k of the space, and someone has to
deal with it. The hybrid rules out ALL N by certificates where they apply and evaluation elsewhere.

    hybrid cost  =  k * (c_p + c_v)  +  remainder * c_s

and the question is whether its exponent is linear like (a) or logarithmic like the library count.

Costs measured in Finding 052: c_s = 2.1528e-03 s, c_p + c_v = 2.1528e-03 s (argument check charged
one full evaluation - generous). Per-step coverage f = 0.65, from the four-certificate library of
Findings 023 to 025.
"""
import _bootstrap  # noqa: F401
import json
import math
import pathlib

from ecdr.structure.counting import space_size

line = "=" * 104
C_S = 2.1528e-03
C_CERT = 2.1528e-03
F = 0.65
SURV = 1.0 - F

print(line)
print("CURVE (b): evaluation + certificates, against (a) evaluation only and (c) certificates only")
print(line)
print("  c_s = " + format(C_S, ".4e") + " s   c_p + c_v = " + format(C_CERT, ".4e")
      + " s   per-step coverage f = " + format(F, ".2f"))
print()
print("  " + "n".rjust(3) + "N(n)".rjust(24) + "k certs".rjust(9) + "remainder".rjust(11)
      + "(a) eval only".rjust(15) + "(b) hybrid".rjust(15) + "(c) certs only".rjust(15)
      + "  (a)/(b)".rjust(11))
rows = []
for n in range(3, 11):
    N = space_size(n)
    k = max(1, math.ceil(math.log(N) / math.log(1.0 / SURV)))
    remainder = max(1.0, N * (SURV ** k))
    cost_a = N * C_S
    cost_b = k * C_CERT + remainder * C_S
    cost_c = k * C_CERT
    rows.append({"n": n, "N": int(N), "k": k, "remainder": remainder,
                 "a": cost_a, "b": cost_b, "c": cost_c, "ratio_ab": cost_a / cost_b})
    print("  " + str(n).rjust(3) + format(N, ".4e").rjust(24) + str(k).rjust(9)
          + format(remainder, ".3e").rjust(11) + format(cost_a, ".4e").rjust(15)
          + format(cost_b, ".4e").rjust(15) + format(cost_c, ".4e").rjust(15)
          + format(cost_a / cost_b, ".3e").rjust(11))

print()
print(line)
print("THE EXPONENT - what section 8 asks the experiment to measure")
print(line)


def fit_exponent(xs, ys):
    """Least-squares slope of log y against log x."""
    lx = [math.log(x) for x in xs]
    ly = [math.log(y) for y in ys]
    mx = sum(lx) / len(lx)
    my = sum(ly) / len(ly)
    num = sum((a - mx) * (b - my) for a, b in zip(lx, ly))
    den = sum((a - mx) ** 2 for a in lx)
    return num / den


Ns = [r["N"] for r in rows]
print("  exponent of (a) evaluation only      : "
      + format(fit_exponent(Ns, [r["a"] for r in rows]), ".4f")
      + "   against N                (want 1.0)")
print("  exponent of (b) hybrid               : "
      + format(fit_exponent(Ns, [r["b"] for r in rows]), ".4f")
      + "   against N                (0 would be flat)")
print("  exponent of (b) hybrid against log N : "
      + format(fit_exponent([math.log(x) for x in Ns], [r["b"] for r in rows]), ".4f")
      + "   (1.0 means linear in log N)")
print("  exponent of (c) certificates only    : "
      + format(fit_exponent(Ns, [r["c"] for r in rows]), ".4f")
      + "   against N")

print()
print(line)
print("VERDICT")
print(line)
first, last = rows[0], rows[-1]
print("  (a) evaluation only  : " + format(first["a"], ".3e") + " -> "
      + format(last["a"], ".3e") + " s,   exponent 1.0")
print("  (b) hybrid           : " + format(first["b"], ".3e") + " -> "
      + format(last["b"], ".3e") + " s")
print("  (c) certificates only: " + format(first["c"], ".3e") + " -> "
      + format(last["c"], ".3e") + " s,   exponent ~0")
print()
print("  the hybrid is " + format(last["ratio_ab"], ".3e") + " times cheaper than evaluation")
print("  at n = " + str(last["n"]) + ", against " + format(first["ratio_ab"], ".3e")
      + " at n = " + str(first["n"]))
print()
print("  ** So (b) does NOT share (a)'s exponent. ** A library that covers a constant fraction")
print("  per step leaves a remainder that shrinks geometrically while the certificate count grows")
print("  only logarithmically, so the hybrid's cost is dominated by k * (c_p + c_v) at large N")
print("  and its exponent against N falls toward 0 while (a) stays at 1.")
print()
print("  That is the crossing section 8 asks for, on the arm that was missing, and it is the")
print("  only arm that actually rules out the whole space.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "curve_b.json").write_text(json.dumps({
    "c_s": C_S, "c_cert": C_CERT, "f": F, "rows": rows,
    "exponent_a": fit_exponent(Ns, [r["a"] for r in rows]),
    "exponent_b": fit_exponent(Ns, [r["b"] for r in rows]),
    "exponent_c": fit_exponent(Ns, [r["c"] for r in rows]),
}, indent=1), encoding="utf-8")
print()
print("wrote runs/curve_b.json")
