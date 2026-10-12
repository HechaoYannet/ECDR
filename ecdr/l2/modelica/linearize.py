"""Linearize an emitted Modelica model with omc and return the state space.

Finding 032: an ideal Position source (exact = true) makes omc dump B = 0 and a transfer
function of 1 at every frequency, silently.  Every model emitted here therefore uses
exact = false with f_crit far above the band of interest, and the parser refuses a dump whose
B is identically zero - the failure is plausible enough that it must be rejected by
construction rather than noticed.
"""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess

import numpy as np

IMAGE = "openmodelica/openmodelica:v1.27.1-minimal"
VOLUME = "ecdr-oml"
ROOT = pathlib.Path(__file__).resolve().parents[2] / "runs" / "modelica_work"


def _parse(path: pathlib.Path):
    txt = path.read_text(encoding="utf-8")
    out = {}
    for key in ("n", "m", "p"):
        mm = re.search(r"parameter Integer " + key + r"\s*=\s*(\d+)", txt)
        out[key] = int(mm.group(1)) if mm else None
    for key in ("A", "B", "C", "D"):
        mm = re.search(r"parameter Real " + key + r"\[[^\]]*\]\s*=\s*\[(.*?)\];", txt, re.S)
        if mm is None:
            out[key] = None
            continue
        rows = [r for r in mm.group(1).split(";") if r.strip()]
        out[key] = np.array([[float(v) for v in r.split(",")] for r in rows])
    return out


def linearize(model_text: str, name: str = "Lin") -> dict:
    """Compile, linearize and return (A, B, C, D).  Raises if the dump is degenerate."""
    work = ROOT / name
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    (work / (name + ".mo")).write_text(model_text, encoding="utf-8")
    (work / "lin.mos").write_text(
        "loadModel(Modelica);\ngetErrorString();\n"
        'loadFile("' + name + '.mo");\ngetErrorString();\n'
        "linearize(" + name + ", startTime = 0.0, stopTime = 0.0, numberOfIntervals = 1,"
        " tolerance = 1e-9);\ngetErrorString();\n", encoding="utf-8")

    cmd = ["docker", "run", "--rm",
           "-v", VOLUME + ":/root/.openmodelica",
           "-v", str(work.resolve()) + ":/work", "-w", "/work", IMAGE,
           "bash", "-lc", "omc lin.mos 2>&1 | grep -Ei 'linear model|error|failed' | head -6"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    log = proc.stdout + proc.stderr

    dump = work / "linearized_model.mo"
    if not dump.exists():
        return {"ok": False, "log": log}
    M = _parse(dump)
    # The ideal-constraint trap: B identically zero means omc dropped the input's
    # derivative terms and the transfer function is D alone.  Reject it here.
    if M["B"] is None or not np.any(np.abs(M["B"]) > 0):
        return {"ok": False, "log": log + "\nREJECTED: B is identically zero",
                "degenerate": True}
    M["ok"] = True
    M["log"] = log
    return M


def tf_complex(M, omegas, out_row: int = 0):
    """C (jw I - A)^-1 B + D, element (out_row, input 0), as a COMPLEX array."""
    A, B, C, D = M["A"], M["B"], M["C"], M["D"]
    n = A.shape[0]
    out = []
    for w in np.atleast_1d(np.asarray(omegas, dtype=float)):
        r = C @ np.linalg.solve(1j * w * np.eye(n) - A, B) + D
        out.append(complex(r[out_row, 0]))
    return np.array(out)


def tf_mag(M, omegas, out_row: int = 0):
    """MAGNITUDE of C (jw I - A)^-1 B + D.

    This function previously returned the complex value under the name tf_mag.  Above
    resonance the real part of the transmissibility is NEGATIVE, so callers that took the
    value directly got a negative number and a nonsense ratio - the same class of defect as
    the six identity traps: a name that promises one thing and returns another.
    """
    return np.abs(tf_complex(M, omegas, out_row=out_row))
