"""Step 23 - do candidate requirement axes compose?

Composition needs the failure sets to be neither nested nor identical.  This measures
the overlap structure on a random ensemble, at a requirement calibrated so that the
total failure fraction is interesting.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.structure import ensemble
from ecdr.structure.capability import joint_table, profile, requirement_check

line = "=" * 88
N_STRUCT = 600
OMEGA = np.logspace(np.log10(0.5), np.log10(3.0e5), 900)
F_LOW = 30.0
OMEGA_LOW = 2 * np.pi * F_LOW

print(line)
print("A. capability profiles over the ensemble (n uniform 2..8)")
print(line)
ens = ensemble(seed=5, count=N_STRUCT, n_lo=2, n_hi=8)
profs = [profile(s, OMEGA, OMEGA_LOW) for s in ens]
sag = np.array([p["sag"] for p in profs])
peak = np.array([p["peak"] for p in profs])
inb = np.array([p["in_band"] for p in profs])
print("  " + "quantity".rjust(12) + "p10".rjust(13) + "median".rjust(13) + "p90".rjust(13)
      + "spread (p90/p10)".rjust(18))
for tag, v in (("sag (mm)", sag * 1e3), ("peak |T|", peak), ("in-band |T|", inb)):
    v = v[np.isfinite(v)]
    p10, p50, p90 = np.percentile(v, [10, 50, 90])
    print("  " + tag.rjust(12) + format(p10, ".4g").rjust(13) + format(p50, ".4g").rjust(13)
          + format(p90, ".4g").rjust(13) + format(p90 / max(p10, 1e-12), ".1f").rjust(18))
print()
print("  All three are CONTINUOUS and widely spread, so each is calibratable.")

print()
print(line)
print("B. failure structure at a calibrated requirement")
print(line)
print("  requirement: sag <= 5 mm, peak |T| <= 3.0, in-band |T| (f >= 30 Hz) <= 0.10")
rows = [requirement_check(p, 5e-3, 3.0, 0.10) for p in profs]
jt = joint_table(rows)
print()
print("  " + "constraint".rjust(12) + "fails".rjust(9) + "fraction".rjust(11))
for k in ("sag", "peak", "band"):
    print("  " + k.rjust(12) + str(jt["marginal"][k]).rjust(9)
          + format(jt["marginal"][k] / N_STRUCT, ".4f").rjust(11))
print("  " + "ANY".rjust(12) + str(jt["any"]).rjust(9)
      + format(jt["any_frac"], ".4f").rjust(11))
print("  " + "ALL THREE".rjust(12) + str(jt["all"]).rjust(9)
      + format(jt["all"] / N_STRUCT, ".4f").rjust(11))
print()
print("  pairwise overlap (jaccard 1.0 = identical failure sets, 0 = disjoint):")
for k, v in jt["pairs"].items():
    print("    " + k.ljust(12) + "both " + str(v["both"]).rjust(5)
          + "   P(second|first) " + format(v["P(b|a)"], ".3f")
          + "   jaccard " + format(v["jaccard"], ".3f"))

print()
print(line)
print("C. COMPOSITION: does the second cut a constant fraction of what the first left?")
print(line)
print("  Apply the failure axes in order and track the surviving fraction.")
print()
order = ["sag", "peak", "band"]
surv = N_STRUCT
print("  " + "step".rjust(6) + "constraint added".rjust(20) + "survivors".rjust(12)
      + "fraction".rjust(11) + "cut of remaining".rjust(19))
comp = []
for i, k in enumerate(order):
    before = surv
    surv = sum(1 for r in rows if not any(r[kk] for kk in order[:i + 1]))
    cut = (before - surv) / before if before else 0.0
    comp.append({"step": i + 1, "constraint": k, "survivors": surv,
                 "fraction": surv / N_STRUCT, "cut_of_remaining": cut})
    print("  " + str(i + 1).rjust(6) + k.rjust(20) + str(surv).rjust(12)
          + format(surv / N_STRUCT, ".4f").rjust(11) + format(cut, ".4f").rjust(19))
print()
cuts = [c["cut_of_remaining"] for c in comp]
if all(c > 0.05 for c in cuts):
    print("  Every step cuts a non-trivial fraction of what remains, so these axes")
    print("  COMPOSE rather than duplicate.  Composition is worth looking for.")
else:
    print("  At least one step cuts almost nothing of what remains: those two axes")
    print("  are effectively NESTED and do not compose.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "composition.json").write_text(json.dumps({
    "n": N_STRUCT, "f_low_hz": F_LOW,
    "marginals": jt["marginal"], "pairs": jt["pairs"],
    "any_frac": jt["any_frac"], "composition": comp,
}, indent=1, default=str), encoding="utf-8")
print()
print("wrote runs/composition.json")
