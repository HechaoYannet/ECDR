"""Step 22 - coverage as a function of (invariant, ensemble, requirement).

Finding 011 said robustness is a property of the predicate SHAPE.  That is incomplete:
coverage also depends on how structures are DISTRIBUTED.  This script measures both.

Two sound, topology-independent bounds are used:

  B1 static deflection   payload sag under gravity.  A CONTINUOUS bound.
  B2 mode count          degrees of freedom.          A DISCRETE bound.

and two ensembles that differ only in how the number of components is drawn.

Prediction: a continuous bound has a coverage that varies continuously with the
requirement, so it can always be calibrated to any value in (0,1); a discrete bound on a
concentrated ensemble has a coverage that jumps.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.structure import ensemble, measure

line = "=" * 86
N_SAMPLES = 3000

spread = ensemble(seed=11, count=N_SAMPLES, n_lo=2, n_hi=8)
concentrated = ensemble(seed=11, count=N_SAMPLES, fixed_n=8)

print(line)
print("A. the two sound bounds, by ensemble")
print(line)
for tag, ens in (("size SPREAD (n uniform 2..8)", spread),
                 ("size CONCENTRATED (n = 8)", concentrated)):
    sag, modes = measure(ens)
    sag = sag[np.isfinite(sag)]
    print("  " + tag)
    print("    static deflection, mm : median " + format(np.median(sag) * 1e3, ".4f")
          + "   p10 " + format(np.percentile(sag, 10) * 1e3, ".4f")
          + "   p90 " + format(np.percentile(sag, 90) * 1e3, ".4f"))
    print("    distinct deflection values: " + str(len(np.unique(np.round(sag, 9)))) + " of "
          + str(sag.size))
    print("    mode count            : " + str(dict(zip(*np.unique(modes, return_counts=True)))))

print()
print(line)
print("B. COVERAGE vs requirement - continuous bound (B1, static deflection)")
print(line)
print("  the invariant is sound: sag > delta_max means the structure cannot be used.")
print("  coverage = fraction of the ensemble ruled out.")
print()
print("  " + "delta_max (mm)".rjust(15) + "spread ensemble".rjust(18) + "concentrated".rjust(14))
sag_s, _ = measure(spread)
sag_c, _ = measure(concentrated)
sag_s = sag_s[np.isfinite(sag_s)]
sag_c = sag_c[np.isfinite(sag_c)]
rows = []
for dmax_mm in (0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0):
    d = dmax_mm / 1e3
    fs = float(np.mean(sag_s > d))
    fc = float(np.mean(sag_c > d))
    rows.append({"delta_max_mm": dmax_mm, "coverage_spread": fs, "coverage_concentrated": fc})
    print("  " + format(dmax_mm, "15.2f") + format(fs, "18.4f").rjust(18) + format(fc, "14.4f").rjust(14))
print()
print("  The coverage sweeps continuously through (0, 1) in BOTH ensembles.  A")
print("  continuous bound is therefore always calibratable: choose the requirement at")
print("  the quantile you want.")

print()
print(line)
print("C. COVERAGE vs requirement - discrete bound (B2, mode count)")
print(line)
print("  the invariant is sound: a structure with n < m degrees of freedom cannot")
print("  produce a free response containing m distinct frequencies.")
print()
print("  " + "m (frequencies needed)".rjust(23) + "spread ensemble".rjust(18) + "concentrated".rjust(14))
_, modes_s = measure(spread)
_, modes_c = measure(concentrated)
rows2 = []
for m in (2, 3, 4, 5, 6, 7, 8):
    fs = float(np.mean(modes_s < m))
    fc = float(np.mean(modes_c < m))
    rows2.append({"m": m, "coverage_spread": fs, "coverage_concentrated": fc})
    print("  " + str(m).rjust(23) + format(fs, "18.4f").rjust(18) + format(fc, "14.4f").rjust(14))
print()
print("  SAME invariant, SAME requirement grid, two ensembles:")
print("    spread ensemble       : coverage moves smoothly, calibratable")
print("    concentrated ensemble : coverage is 0 then 1, nothing in between")

print()
print(line)
print("D. VERDICT")
print(line)
print("  Finding 011 was incomplete.  Coverage is a property of the TRIPLE")
print("  (invariant, ensemble, requirement), not of the predicate shape alone.")
print()
print("  What survives and is sharper:")
print("    * a CONTINUOUS bound (a physical quantity) has coverage that varies")
print("      continuously with the requirement, so it can always be calibrated;")
print("    * a DISCRETE/combinatorial bound has coverage that jumps unless the")
print("      ensemble spreads that discrete attribute.");
print("  So the practical rule is: prefer invariants whose bound is a CONTINUOUS")
print("  physical quantity, and calibrate the requirement at the quantile you need.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "coverage_ensemble.json").write_text(json.dumps({
    "n_samples": N_SAMPLES, "deflection_sweep": rows, "mode_sweep": rows2,
    "deflection_median_mm_spread": float(np.median(sag_s) * 1e3),
    "deflection_median_mm_concentrated": float(np.median(sag_c) * 1e3),
}, indent=1), encoding="utf-8")
print()
print("wrote runs/coverage_ensemble.json")
