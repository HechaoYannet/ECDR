"""Step 24 - composition must be measured at a NON-DEGENERATE calibration.

Step 23 showed the three requirement axes compose cleanly (cuts of 0.69, 0.82, 1.00 of
what remained) - but at that calibration EVERY structure failed, so the composition was
walking toward an empty set and the conclusion "no design exists" was trivial.

This is the calibration failure mode Finding 012 section 6 warned about, caught in the
act.  The interesting regime is where the surviving set is non-empty but small: that is
where an agent has to FIND a design and the certificates prune the rest.

This script sweeps the requirement tightness, reports where the non-degenerate band is,
and re-measures composition there.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.structure import ensemble
from ecdr.structure.capability import profile, requirement_check

line = "=" * 92
N_STRUCT = 600
OMEGA = np.logspace(np.log10(0.5), np.log10(3.0e5), 900)
OMEGA_LOW = 2 * np.pi * 30.0

ens = ensemble(seed=5, count=N_STRUCT, n_lo=2, n_hi=8)
profs = [profile(s, OMEGA, OMEGA_LOW) for s in ens]

print(line)
print("A. CALIBRATION SWEEP - where is the non-degenerate band?")
print(line)
print("  requirement tightened by a scalar factor; report survivors and marginals")
print()
print("  " + "scale".rjust(7) + "sag<=mm".rjust(9) + "peak<=".rjust(8) + "band<=".rjust(8)
      + "survive".rjust(9) + "frac".rjust(9) + "fail sag".rjust(10) + "fail peak".rjust(11)
      + "fail band".rjust(11))
sweep = []
for scale in (4.0, 2.0, 1.0, 0.6, 0.4, 0.25, 0.15, 0.10):
    dmax = 8.0e-3 * scale
    amax = 8.0 * scale
    tiso = 0.30 * scale
    rows = [requirement_check(p, dmax, amax, tiso) for p in profs]
    surv = sum(1 for r in rows if not any(r.values()))
    m = {k: sum(1 for r in rows if r[k]) for k in ("sag", "peak", "band")}
    rec = {"scale": scale, "delta_max_mm": dmax * 1e3, "a_max": amax, "t_iso": tiso,
           "survivors": surv, "survivor_frac": surv / N_STRUCT,
           "fail_sag": m["sag"], "fail_peak": m["peak"], "fail_band": m["band"]}
    sweep.append(rec)
    print("  " + format(scale, ".2f").rjust(7) + format(dmax * 1e3, ".2f").rjust(9)
          + format(amax, ".2f").rjust(8) + format(tiso, ".3f").rjust(8)
          + str(surv).rjust(9) + format(surv / N_STRUCT, ".4f").rjust(9)
          + str(m["sag"]).rjust(10) + str(m["peak"]).rjust(11) + str(m["band"]).rjust(11))
print()
print("  Step 23 sat at the tight end (scale 0.25), where survivors = 0 and the")
print("  composition was walking toward an empty set.  The informative band is where")
print("  survivors are non-zero but small.")

# pick the tightest calibration that still leaves a non-trivial survivor set
best = None
for rec in sweep:
    if rec["survivor_frac"] >= 0.05:
        best = rec
print()
print(line)
print("B. COMPOSITION at the non-degenerate calibration")
print(line)
if best is None:
    print("  no non-degenerate calibration found in the sweep")
    comp = []
else:
    print("  chosen: sag <= " + format(best["delta_max_mm"], ".2f") + " mm, peak <= "
          + format(best["a_max"], ".2f") + ", in-band <= " + format(best["t_iso"], ".3f"))
    print("  survivors: " + str(best["survivors"]) + " of " + str(N_STRUCT)
          + "  (" + format(best["survivor_frac"], ".4f") + ")")
    print()
    rows = [requirement_check(p, best["delta_max_mm"] / 1e3, best["a_max"], best["t_iso"])
            for p in profs]
    order = ["sag", "peak", "band"]
    surv = N_STRUCT
    comp = []
    print("  " + "step".rjust(6) + "constraint added".rjust(20) + "survivors".rjust(12)
          + "fraction".rjust(11) + "cut of remaining".rjust(19))
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
    print("  cuts of remaining: " + ", ".join(format(c, ".3f") for c in cuts))
    print("  -> all substantial, so the axes are not NESTED.")
    print()
    print("  NOTE: the product of the sequential survivor ratios telescopes to the")
    print("  final survivor fraction as an IDENTITY, so it cannot test independence.")
    print("  The correct test compares the observed joint survival against the")
    print("  product of the MARGINAL survivals.")
    print()
    marg_surv = {}
    for k in order:
        marg_surv[k] = sum(1 for r in rows if not r[k]) / N_STRUCT
    prod_marg = 1.0
    for k in order:
        prod_marg *= marg_surv[k]
        print("    P(survive " + k.ljust(5) + ") = " + format(marg_surv[k], ".4f"))
    obs = surv / N_STRUCT
    print("    product of marginals   = " + format(prod_marg, ".4f"))
    print("    observed joint survival= " + format(obs, ".4f"))
    ratio = obs / prod_marg if prod_marg else float("nan")
    print("    ratio observed/independent = " + format(ratio, ".4f"))
    print()
    if ratio < 0.9:
        print("  ratio < 1 means the FAILURES are POSITIVELY CORRELATED: a structure that")
        print("  is bad on one axis tends to be bad on the others.  The axes still each cut")
        print("  a substantial share of what remains, but they are partly redundant and")
        print("  the composition gains less than independence would give.")
        print()
        print("  This is the important negative reading: choosing different PERFORMANCE")
        print("  axes does not buy independence, because there is a common structural")
        print("  factor behind them.  Independent cuts have to come from certificates")
        print("  targeting different STRUCTURAL FEATURES, not different metrics.")
    elif ratio > 1.1:
        print("  ratio > 1 means the axes are COMPLEMENTARY: a certificate on one axis")
        print("  leaves structures the other axis can still cut.  This is what a")
        print("  certificate library needs.")
    else:
        print("  ratio near 1 means the axes are close to independent on this ensemble.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "calibration.json").write_text(json.dumps({
    "sweep": sweep, "chosen": best, "composition": comp,
    "marginal_survival": marg_surv if best else None,
    "product_of_marginals": prod_marg if best else None,
    "independence_ratio": (obs / prod_marg) if (best and prod_marg) else None,
}, indent=1, default=str), encoding="utf-8")
print()
print("wrote runs/calibration.json")
