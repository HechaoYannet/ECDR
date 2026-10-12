"""Step 58 - read the Modelica CSV and compare with L0.

The Modelica model declares a mass, a spring, a damper and a moving ground and connects
them; it contains no equations of motion.  The tool assembles them.  If the number it
produces matches the frequency-domain transmissibility, then the MODELLING is confirmed -
not just the numerics, which is all the Julia rung could do.
"""
import _bootstrap  # noqa: F401
import csv
import json
import pathlib

import numpy as np

from ecdr.l0 import PassiveSDOF

line = "=" * 84
CSV = pathlib.Path(__file__).resolve().parents[1] / "ecdr" / "l2" / "modelica" / "smoke" / "SdofIso_res.csv"

with CSV.open() as fh:
    rd = csv.DictReader(fh)
    t = np.array([float(r["time"]) for r in rd])
with CSV.open() as fh:
    rd = csv.DictReader(fh)
    xp = np.array([float(r["x_payload"]) for r in rd])

print(line)
print("Modelica output")
print(line)
print("  samples            : " + str(t.size))
print("  time span          : " + format(t[0], ".3f") + " to " + format(t[-1], ".3f") + " s")

wn = 99.03
zeta = 0.5426
omega = 62.83185307179586
A = 1.0
T = float(np.abs(PassiveSDOF().transmissibility(np.array([omega]), (wn, zeta)))[0])

period = 2 * np.pi / omega
print("  excitation period  : " + format(period, ".6f") + " s")

print()
print(line)
print("last-period amplitude, as a function of how much of the record is used")
print(line)
print("  " + "periods kept".rjust(14) + "t_start".rjust(10) + "max|x_payload|".rjust(18)
      + "ratio to |T|".rjust(14))
rows = []
for nkeep in (1, 2, 4, 8, 20):
    t0 = t[-1] - nkeep * period
    m = t >= t0
    amp = float(np.abs(xp[m]).max())
    rows.append({"periods": nkeep, "t_start": float(t0), "amp": amp,
                 "ratio": amp / T if T else float("nan")})
    print("  " + str(nkeep).rjust(14) + format(t0, ".4f").rjust(10)
          + format(amp, ".10e").rjust(18) + format(amp / T if T else float("nan"), ".8f").rjust(14))

print()
print(line)
print("comparison")
print(line)
print("  L0 frequency-domain |T| at omega = " + format(omega, ".6f") + " : "
      + format(T, ".10e"))
best = rows[0]
print("  Modelica last-period amplitude                    : " + format(best["amp"], ".10e"))
rel = abs(best["amp"] - T) / T
print("  relative difference                               : " + format(rel, ".3e"))
print()
if rel < 5e-3:
    print("  MATCH.  A model containing no equations of motion reproduces the frequency-")
    print("  domain transmissibility.  This is the check the Julia rung could not give:")
    print("  it tests whether the equations are right, not whether they are solved right.")
else:
    print("  MISMATCH.  Investigate before drawing any conclusion.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "modelica_smoke.json").write_text(json.dumps({
    "omega": omega, "L0_T": T, "rows": rows,
    "best_amp": best["amp"], "rel_diff": rel,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/modelica_smoke.json")
