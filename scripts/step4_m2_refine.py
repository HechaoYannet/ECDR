"""Step 4 - refined Pareto scan of the passive 2-DOF family.

omega_n1 is pinned at omega_n_min for a reason worth stating: transmissibility
depends on omega_n1 only through r = w / omega_n1, so the band constraint is
monotone decreasing in omega_n1 while the peak value does not depend on it at
all.  The sag constraint is monotone increasing.  Hence omega_n1 = omega_n_min
dominates every other choice and the search is exact in that dimension.

The scan records, for every parameter combination, both the in-band maximum and
the peak, then reports the Pareto front.  Only points that satisfy the peak
constraint may be quoted for the band.
"""
import _bootstrap  # noqa: F401
import json
import numpy as np

from ecdr.l0 import G, IsolationTask, TunedMassDamper
from ecdr.l0.feasibility import SEARCH_OMEGA, DEFAULT_OMEGA

line = "=" * 78
omega = np.logspace(np.log10(0.05), np.log10(5.0e4), 1500)


def make_task(name, f_low, T_iso_db=-20.0, A_max_db=3.0, delta_mm=1.0):
    return IsolationTask(name, f_low, T_iso_db, A_max_db, delta_mm / 1e3)


def refined_scan(task, mech=None, verbose=True):
    mech = mech or TunedMassDamper()
    wn_min = float(np.sqrt(G / task.delta_max))
    band = omega >= task.omega_low
    om_band = omega[band]

    zetas1 = np.logspace(-3.2, -0.1, 32)
    mus = np.logspace(-4.5, -0.5, 24)
    ratios = np.logspace(-0.4, 1.0, 24)
    zetas2 = np.logspace(-3.0, -0.1, 18)

    best = (np.inf, None)
    pareto = []
    total = zetas1.size * mus.size * ratios.size * zetas2.size

    for z1 in zetas1:
        for mu in mus:
            for ratio in ratios:
                for z2 in zetas2:
                    T = np.abs(mech.transmissibility(omega, (wn_min, z1, mu, ratio, z2)))
                    in_band = float(T[band].max())
                    pk = float(T.max())
                    pareto.append((pk, in_band, float(z1), float(mu), float(ratio), float(z2)))
                    if pk <= task.A_max and in_band < best[0]:
                        best = (in_band, (float(z1), float(mu), float(ratio), float(z2), pk))

    pareto.sort(key=lambda t: (t[0], t[1]))
    if verbose:
        print(f"    scanned {total:,} combinations")

    # verify the winner on the fine grid
    if best[1] is not None:
        z1, mu, ratio, z2, pk = best[1]
        T = np.abs(mech.transmissibility(DEFAULT_OMEGA, (wn_min, z1, mu, ratio, z2)))
        b = DEFAULT_OMEGA >= task.omega_low
        best = (float(T[b].max()), (z1, mu, ratio, z2, float(T.max())))

    return best, pareto


results = {}
for name, f_low in [("T_base", 50.0), ("T_mid", 90.0), ("T_easy", 110.0), ("T_veryeasy", 160.0)]:
    task = make_task(name, f_low)
    print(line)
    print(f"{name}: f_low = {f_low:g} Hz   |T| <= {task.T_iso:.3f} for f >= {f_low:g} Hz, "
          f"peak <= {task.A_max:.4f}, sag <= {task.delta_max * 1e3:.2f} mm")
    print(line)
    best, _ = refined_scan(task)
    if best[1] is None:
        print("    no peak-feasible member found")
        results[name] = {"f_low": f_low, "feasible_any": False}
        continue
    in_band, (z1, mu, ratio, z2, pk) = best
    ok = in_band <= task.T_iso
    print(f"    best peak-feasible member: zeta1={z1:.5g} mu={mu:.5g} ratio={ratio:.5g} zeta2={z2:.5g}")
    print(f"      in-band max |T| = {in_band:.6f} vs {task.T_iso:.6f}   "
          f"({100 * (in_band / task.T_iso - 1):+.2f} %)")
    print(f"      peak |T|        = {pk:.6f} vs {task.A_max:.6f}")
    print(f"    => passive 2-DOF {'FEASIBLE' if ok else 'NOT feasible'}")
    results[name] = {"f_low": f_low, "feasible_any": bool(ok), "best_in_band": in_band,
                     "T_iso": float(task.T_iso), "params": {"zeta1": z1, "mu": mu, "ratio": ratio, "zeta2": z2}}
    print()

import pathlib
out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "step4_m2_refine.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"wrote {out / 'step4_m2_refine.json'}")
