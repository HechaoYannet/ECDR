"""Step 10 - locate the two escape-depth thresholds exactly.

M1 -> M2 threshold: exact, from the certificate (Lambda crosses 1).
M2 -> M3 threshold: numerical, but obtainable in ONE scan.  For each peak-feasible
design we keep the whole suffix-maximum curve, and maintain

    G(omega_low) = min over designs of max over w >= omega_low of |T|

Then M2 is feasible at band edge omega_low exactly when G(omega_low) <= T_iso, and
the threshold is where the curve crosses.  One pass answers every band edge.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np
from scipy.optimize import brentq

from ecdr.bench import default_family_spec, make_family, m1_evidence, m3_evidence
from ecdr.l0 import G, IsolationTask, TunedMassDamper, certify_passive_sdof
from ecdr.l0.invariants import tf_coeffs
from ecdr.l0.peaks import peak_of

line = "=" * 78
spec = default_family_spec()
probe = spec.task(100.0)
wn1 = float(np.sqrt(G / probe.delta_max))
T_iso = probe.T_iso
A_max = probe.A_max

# ---- M1 threshold: exact ---------------------------------------------------
crit1 = brentq(lambda f: certify_passive_sdof(
    IsolationTask("c", f, spec.T_iso_db, spec.A_max_db, spec.delta_mm / 1e3)).Lambda - 1.0,
    20.0, 600.0, xtol=1e-10)
print(line)
print("M1 -> M2 threshold (exact): f_low = " + format(crit1, ".6f") + " Hz")
print("  for f_low below this, a passive SDOF is PROVABLY infeasible; above it the")
print("  certificate constructs a witness.")
print(line)

# ---- M2 threshold curve: one scan -----------------------------------------
print()
print("scanning the passive chain, accumulating the whole threshold curve ...")
mech = TunedMassDamper()
zetas1 = np.concatenate([np.logspace(-2.5, -0.7, 10), np.linspace(0.2, 1.0, 9)])
mus = np.concatenate([np.logspace(-3.0, -1.0, 9), np.linspace(0.1, 0.5, 5)])
ratios = np.logspace(-0.4, 1.0, 14)
zetas2 = np.concatenate([np.logspace(-1.5, -0.7, 6), np.linspace(0.2, 1.0, 6)])

n_grid = 20000
w = np.logspace(np.log10(0.02), np.log10(2.0e5), n_grid)
Gcurve = np.full(n_grid, np.inf)
n_examined = 0
n_feasible = 0

for z1 in zetas1:
    for mu in mus:
        for ratio in ratios:
            for z2 in zetas2:
                n_examined += 1
                prm = (wn1, float(z1), float(mu), float(ratio), float(z2))
                num, den = tf_coeffs("M2_tuned_mass_damper", prm)
                f = (lambda ww, prm=prm: mech.transmissibility(ww, prm))
                pk, _ = peak_of(f, num, den, n_grid=3000, refine=False)
                if pk > A_max * (1 + 1e-9):
                    continue
                n_feasible += 1
                T = np.abs(f(w))
                suffix = np.maximum.accumulate(T[::-1])[::-1]
                np.minimum(Gcurve, suffix, out=Gcurve)

print("  examined " + str(n_examined) + ", peak-feasible " + str(n_feasible))

ok = Gcurve <= T_iso
if not ok.any():
    print("  M2 never reaches the limit anywhere in the scanned grid")
    crit2 = float("nan")
else:
    i = int(np.argmax(ok))
    if i == 0:
        crit2 = float(w[0])
    else:
        lo, hi = w[i - 1], w[i]
        crit2 = float(brentq(
            lambda ww: np.interp(np.log(ww), np.log(w), Gcurve) - T_iso,
            lo, hi, xtol=1e-12))

print()
print(line)
print("M2 -> M3 threshold (numerical): f_low = " + format(crit2 / 2 / np.pi, ".4f") + " Hz")
print("  above this band edge some passive chain design reaches |T| <= "
      + format(T_iso, ".4f") + "; below it none of the " + str(n_feasible) + " scanned does.")
print(line)

print()
print(line)
print("REGIMES")
print(line)
print("  f_low <  " + format(crit2 / 2 / np.pi, ".2f") + " Hz : depth 3 - only the active mechanism escapes")
print("  " + format(crit2 / 2 / np.pi, ".2f") + " .. " + format(crit1, ".2f") + " Hz : depth 2 - the passive chain suffices")
print("  f_low >  " + format(crit1, ".2f") + " Hz : depth 1 - the initial passive SDOF already suffices")

# sampled curve for the registry
idx = np.unique(np.clip(np.searchsorted(w, np.exp(np.linspace(np.log(w[0]), np.log(w[-1]), 400))), 0, n_grid - 1))
curve = [{"omega_low": float(w[j]), "f_low_hz": float(w[j] / 2 / np.pi),
          "best_in_band_T": float(Gcurve[j]) if np.isfinite(Gcurve[j]) else None}
         for j in idx]

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "thresholds.json").write_text(json.dumps({
    "n_examined": n_examined, "n_peak_feasible": n_feasible,
    "M1_threshold_hz": crit1,
    "M2_threshold_hz": crit2 / 2 / np.pi if np.isfinite(crit2) else None,
    "T_iso": float(T_iso),
    "m2_threshold_curve": curve,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/thresholds.json")
