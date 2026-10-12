"""Step 48 - does near-independence COMPOUND across three certificates?

Finding 022 measured a TWO-certificate library at an independence ratio of 0.88 to 0.95 and
flagged that the ratio is near independent, not independent, so the correction would
compound: 0.88^2 = 0.77 and worse with more members.

Step 47 supplied a third SOUND certificate on a different mechanism:

    C3 time scale   Rayleigh's principle with the trial vector 1 gives
                    omega_1^2 <= (sum of ground stiffness) / (sum of masses),
                    so a requirement omega_1 <= omega_max is refuted whenever the ratio
                    exceeds omega_max^2.  0 violations in 300 networks, and the bound is
                    uncorrelated with the modal count (rho = -0.006).

Now the three are applied together and the JOINT survival is compared against the product of
the MARGINALS - not against a sequentially-telescoped quantity, which would be an identity.

    three sound certificates
      C1 modal      n < m                     -> infeasible
      C2 statics    sag > delta_max           -> infeasible
      C3 timescale  ratio > omega_max^2       -> infeasible

Each threshold is placed at its own marginal median, so each cuts about half the space and
the product of marginals is about 0.125.  If the observed joint is also about 0.125 the
three compose multiplicatively and the library argument holds.
"""
import _bootstrap  # noqa: F401
import json
import math
import pathlib

import numpy as np

from ecdr.structure import ensemble

line = "=" * 90
N_SAMPLES = 600


def space(n_max, seed):
    ens = ensemble(seed=seed, count=N_SAMPLES, n_lo=2, n_hi=n_max)
    n = np.array([s.n for s in ens], dtype=float)
    sag = np.array([s.static_deflection() for s in ens])
    M, C, K, f, g = None, None, None, None, None
    ratio = np.array([sum(s.ground_k.values()) / s.masses.sum() for s in ens])
    return n, sag, ratio


print(line)
print("A. three cuts, each calibrated at its own marginal median")
print(line)
print("  " + "n_max".rjust(6) + "N".rjust(6) + "f1".rjust(8) + "f2".rjust(8) + "f3".rjust(8)
      + "prod marg".rjust(11) + "observed".rjust(10) + "RATIO".rjust(9))
rows = []
for n_max in (5, 6, 7, 8):
    n, sag, ratio = space(n_max, 100 + n_max)
    m = int(np.median(n))
    c1 = n < m
    c2 = sag > np.median(sag)
    c3 = ratio > np.median(ratio)
    f1, f2, f3 = float(c1.mean()), float(c2.mean()), float(c3.mean())
    surv = ~(c1 | c2 | c3)
    obs = float(surv.mean())
    prod = (1 - f1) * (1 - f2) * (1 - f3)
    rows.append({"n_max": n_max, "N": N_SAMPLES, "m": m,
                 "f1": f1, "f2": f2, "f3": f3,
                 "prod_marginals": prod, "observed_joint": obs,
                 "ratio": obs / prod if prod else float("nan"),
                 "survivors": int(surv.sum())})
    print("  " + str(n_max).rjust(6) + str(N_SAMPLES).rjust(6)
          + format(f1, ".4f").rjust(8) + format(f2, ".4f").rjust(8)
          + format(f3, ".4f").rjust(8) + format(prod, ".4f").rjust(11)
          + format(obs, ".4f").rjust(10)
          + format(obs / prod if prod else float("nan"), ".4f").rjust(9))

print()
print(line)
print("B. the same, with the marginal test replaced by an explicit warning")
print(line)
print("  The product of (1-f_i) is NOT the observed joint by construction here, because")
print("  each f_i is a MARGINAL, not a conditional.  That is the difference from the")
print("  identity trap in Finding 022, where f_B was defined as P(B | not A).  So a ratio")
print("  away from 1 is real information.")

print()
print(line)
print("C. does the correction compound?")
print(line)
r = np.array([x["ratio"] for x in rows])
print("  ratio across n_max " + str([x["n_max"] for x in rows]) + " : "
      + ", ".join(format(v, ".4f") for v in r))
print("  mean ratio : " + format(float(r.mean()), ".4f"))
print()
for k in (2, 3, 5, 10, 20):
    print("    after " + str(k).rjust(2) + " cuts, the accumulated correction is "
          + format(float(r.mean()) ** (k - 1), ".4f"))
print()
if r.mean() > 0.9:
    print("  -> the correction is mild and the product of marginals is a good approximation")
    print("     for at least three cuts.  The library arithmetic of Finding 022 stands.")
else:
    print("  -> the correction is material; the library arithmetic has to carry a factor")
    print("     of " + format(float(r.mean()) ** (k - 1), ".4f") + " after k cuts.")

print()
print(line)
print("D. library arithmetic with all three certificates")
print(line)
print("  " + "n_max".rjust(6) + "per-cut survival".rjust(18) + "pairs for N=1e6".rjust(19)
      + "for N=1e10".rjust(13))
for x in rows:
    surv = x["prod_marginals"]
    k6 = math.log(1e6) / math.log(1 / surv)
    k10 = math.log(1e10) / math.log(1 / surv)
    print("  " + str(x["n_max"]).rjust(6) + format(surv, ".4f").rjust(18)
          + format(k6, ".1f").rjust(19) + format(k10, ".1f").rjust(13))
print()
print("  Each 'pair' here is a full three-certificate round, so the certificate count is")
print("  three times the number shown.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "three_certificate.json").write_text(json.dumps({
    "rows": rows, "mean_ratio": float(r.mean()),
    "corrections": {str(k): float(r.mean()) ** (k - 1) for k in (2, 3, 5, 10, 20)},
}, indent=1), encoding="utf-8")
print()
print("wrote runs/three_certificate.json")
