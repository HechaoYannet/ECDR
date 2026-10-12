"""Step 61 - evaluate the linearized model and compare against L0.

Two dumps exist:
  linearized_model_exact.mo   Position(exact = true)  - the ideal position CONSTRAINT
  linearized_model.mo         Position(exact = false) - a second-order Bessel filter

The exact one dumps B = 0 and D = 1, whose transfer function is 1 at every frequency.
The states omc chose there are the damper's RELATIVE coordinates, in which the input enters
through its second derivative, so x' = A x + B u cannot represent it and omc silently leaves
B at zero.

The filtered one has four states - the two relative coordinates plus the two filter states -
with a nonzero B and C = [1, 0, 1, 0], D = 0, which is structurally what the physics
requires: the payload is the relative displacement plus the ground displacement.
"""
import _bootstrap  # noqa: F401
import json
import pathlib
import re

import numpy as np

from ecdr.l0 import PassiveSDOF

line = "=" * 90
WORK = pathlib.Path(__file__).resolve().parents[1] / "runs" / "modelica_work"


def parse(path):
    txt = pathlib.Path(path).read_text(encoding="utf-8")
    out = {}
    for key in ("n", "m", "p"):
        mm = re.search(r"parameter Integer " + key + r"\s*=\s*(\d+)", txt)
        out[key] = int(mm.group(1)) if mm else None
    for key in ("A", "B", "C", "D"):
        mm = re.search(r"parameter Real " + key + r"\[[^\]]*\]\s*=\s*\[(.*?)\];", txt, re.S)
        rows = [r for r in mm.group(1).split(";") if r.strip()]
        out[key] = np.array([[float(v) for v in r.split(",")] for r in rows])
    return out


def mag(M, omegas):
    A, B, C, D = M["A"], M["B"], M["C"], M["D"]
    n = A.shape[0]
    return np.array([abs((C @ np.linalg.solve(1j * w * np.eye(n) - A, B) + D)[0, 0])
                     for w in np.atleast_1d(omegas)])


wn, zeta = 99.03, 0.5426
omegas = np.array([10.0, 62.83185307179586, 300.0, 1000.0])
ref = np.abs(PassiveSDOF().transmissibility(omegas, (wn, zeta)))

print(line)
print("linearized transfer against the L0 frequency-domain transmissibility")
print(line)
rows = []
for tag, fn in (("exact = true (constraint)", "linearized_model_exact.mo"),
                ("exact = false (Bessel filter)", "linearized_model.mo")):
    p = WORK / fn
    if not p.exists():
        print("  " + tag + " : dump absent")
        continue
    M = parse(p)
    got = mag(M, omegas)
    print()
    print("  " + tag + "   states = " + str(M["n"]))
    print("    " + "omega".rjust(12) + "L0".rjust(18) + "linearized".rjust(18)
          + "ratio".rjust(12))
    for w, a, b in zip(omegas, ref, got):
        rows.append({"case": tag, "omega": float(w), "L0": float(a),
                     "linearized": float(b), "ratio": float(b / a) if a else float("nan")})
        print("    " + format(w, ".6g").rjust(12) + format(a, ".10e").rjust(18)
              + format(b, ".10e").rjust(18) + format(b / a if a else float("nan"), ".8f").rjust(12))

print()
print(line)
print("VERDICT")
print(line)
filt = [r for r in rows if "false" in r["case"]]
if filt:
    err = np.array([abs(r["ratio"] - 1.0) for r in filt])
    print("  filtered case, ratio error across the band")
    print("    median : " + format(float(np.median(err)), ".3e"))
    print("    worst  : " + format(float(err.max()), ".3e"))
    print()
    if err.max() < 1e-4:
        print("  The linearized emitted model reproduces L0 across three decades.  It needs")
        print("  no settling time, so L2-Modelica becomes usable for an ensemble sweep -")
        print("  which the time-domain route could not be, at thousands of periods per point.")
    else:
        print("  The filter is not negligible over this band; raise f_crit or divide it out.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
(out / "linearize_check.json").write_text(json.dumps({"rows": rows}, indent=1), encoding="utf-8")
print()
print("wrote runs/linearize_check.json")
