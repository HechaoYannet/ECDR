"""Run a Modelica model in the pinned OpenModelica container and read the result back."""
from __future__ import annotations

import csv
import pathlib
import subprocess

import numpy as np

IMAGE = "openmodelica/openmodelica:v1.27.1-minimal"
VOLUME = "ecdr-oml"
# parents[3] is the repository root: ecdr/l2/modelica/run.py -> ecdr/l2/modelica -> ecdr/l2 -> ecdr
# -> repo.  parents[2] resolved to ecdr/, which put the OpenModelica scratch INSIDE the package: one
# reconstruction of the L2 ladder wrote 697.6 MB and 2522 files into ecdr/runs/modelica_work.  The
# top-level runs/ is the intended location and is already gitignored.
WORK = pathlib.Path(__file__).resolve().parents[3] / "runs" / "modelica_work"


def simulate(model_text: str, mos_text: str, name: str = "Net") -> dict:
    """Write, compile and simulate; return the time series of x_payload."""
    WORK.mkdir(parents=True, exist_ok=True)
    for old in WORK.glob(name + "*"):
        old.unlink()
    (WORK / (name + ".mo")).write_text(model_text, encoding="utf-8")
    (WORK / (name + ".mos")).write_text(mos_text, encoding="utf-8")

    win = str(WORK.resolve())
    cmd = ["docker", "run", "--rm",
           "-v", VOLUME + ":/root/.openmodelica",
           "-v", win + ":/work", "-w", "/work", IMAGE,
           "bash", "-lc", "omc " + name + ".mos 2>&1 | tail -30"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    out = proc.stdout + proc.stderr

    csv_path = WORK / (name + "_res.csv")
    if not csv_path.exists():
        return {"ok": False, "log": out, "t": None, "x": None}
    with csv_path.open() as fh:
        rows = list(csv.DictReader(fh))
    t = np.array([float(r["time"]) for r in rows])
    x = np.array([float(r["x_payload"]) for r in rows])
    return {"ok": True, "log": out, "t": t, "x": x}


def steady_amplitude(t, x, omega, periods_kept: float = 3.0) -> float:
    """Largest absolute x over the last few excitation periods."""
    T = 2.0 * np.pi / omega
    m = t >= (t[-1] - periods_kept * T)
    return float(np.abs(x[m]).max()) if m.any() else float("nan")
