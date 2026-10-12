"""Ground-truth evidence for each (task, mechanism) pair.

Epistemic status is recorded per mechanism, because the three classes are not
known to the same standard:

  M1  EXACT.  A closed-form certificate decides feasibility in both directions.
  M2  NUMERICAL.  A witness proves feasibility; the absence of a witness proves
      nothing.  Reported as no_witness_found, never as infeasible.
  M3  EXACT.  The sky-hook admits a semi-analytic decision procedure: the band
      constraint improves with damping while actuator cost worsens with it, so
      feasibility reduces to a one-dimensional comparison.
"""
from __future__ import annotations

import numpy as np

from ..l0 import G, IsolationTask, certify_passive_sdof, TunedMassDamper
from ..l0.certificates import zeta_min_from_peak, peak_transmissibility_skynook
from ..l0.invariants import tf_coeffs
from ..l0.peaks import peak_of


def m1_evidence(task: IsolationTask) -> dict:
    cert = certify_passive_sdof(task)
    return {
        "mechanism": "M1_passive_sdof",
        "status": "feasible" if cert.feasible else "proved_infeasible",
        "exact": True,
        "Lambda": cert.Lambda,
        "detail": cert.verdict,
    }


def m3_max_force_per_disp(zeta: float, wn: float, n: int = 40001) -> float:
    """max over w of |U / X_g| for the sky-hook: 2*zeta*wn^2*r*|T(r)|."""
    r = np.logspace(-2.0, 2.5, n)
    T = 1.0 / np.sqrt((1.0 - r ** 2) ** 2 + (2.0 * zeta * r) ** 2)
    return float(np.max(2.0 * zeta * wn * (wn * r) * T))


def m3_inband_T(zeta: float, wn: float, omega_low: float) -> float:
    """In-band max of |T| for the sky-hook; T decreases in r, so it binds at r_low."""
    r = omega_low / wn
    return float(1.0 / np.sqrt((1.0 - r ** 2) ** 2 + (2.0 * zeta * r) ** 2))


def m3_evidence(task: IsolationTask, zeta_hi: float = 40.0) -> dict:
    """Exact decision procedure for the sky-hook.

    omega_n = wn_min is optimal: a smaller omega_n raises r_low, which lowers the
    in-band transmissibility, and it also lowers actuator force.  Damping helps the
    band and hurts the actuator, so the best admissible design sits at the largest
    zeta the actuator budget allows.
    """
    wn = float(np.sqrt(G / task.delta_max))
    z_min = zeta_min_from_peak(task.A_max, peak_transmissibility_skynook)
    if not np.isfinite(z_min):
        return {"mechanism": "M3_sky_hook_active", "status": "proved_infeasible",
                "exact": True, "detail": "peak constraint unreachable for this shape"}

    if task.force_per_disp_max is None:
        z_star = zeta_hi
    else:
        lo, hi = 1e-6, zeta_hi
        if m3_max_force_per_disp(lo, wn) > task.force_per_disp_max:
            z_star = 0.0
        else:
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if m3_max_force_per_disp(mid, wn) <= task.force_per_disp_max:
                    lo = mid
                else:
                    hi = mid
            z_star = lo

    if z_star < z_min:
        return {"mechanism": "M3_sky_hook_active", "status": "proved_infeasible",
                "exact": True, "zeta_star": float(z_star), "zeta_min": float(z_min),
                "detail": "actuator budget caps damping below the peak requirement"}

    T_band = m3_inband_T(z_star, wn, task.omega_low)
    ok = T_band <= task.T_iso
    return {
        "mechanism": "M3_sky_hook_active",
        "status": "feasible" if ok else "proved_infeasible",
        "exact": True,
        "zeta_star": float(z_star),
        "omega_n": float(wn),
        "in_band_T": float(T_band),
        "detail": "best admissible design reaches in-band |T| = " + format(T_band, ".6f")
                  + " against a limit of " + format(task.T_iso, ".6f"),
    }


def m2_scan(tasks, zetas1=None, mus=None, ratios=None, zetas2=None,
            n_grid: int = 20000, verbose: bool = True) -> dict:
    """Scan the passive chain once, then answer every task from the same pass.

    omega_n1 = wn_min is optimal: transmissibility depends on omega_n1 only through
    r = w/omega_n1, so a smaller omega_n1 raises r_low and improves the band, while
    the sag constraint forbids going lower.  Each surviving design is evaluated on a
    frequency grid once; a suffix maximum answers any band edge afterwards.
    """
    mech = TunedMassDamper()
    wn1 = float(np.sqrt(G / tasks[0].delta_max))
    A_max = tasks[0].A_max

    if zetas1 is None:
        zetas1 = np.concatenate([np.logspace(-2.5, -0.7, 10), np.linspace(0.2, 1.0, 9)])
    if mus is None:
        mus = np.concatenate([np.logspace(-3.0, -1.0, 9), np.linspace(0.1, 0.5, 5)])
    if ratios is None:
        ratios = np.logspace(-0.4, 1.0, 14)
    if zetas2 is None:
        zetas2 = np.concatenate([np.logspace(-1.5, -0.7, 6), np.linspace(0.2, 1.0, 6)])

    w = np.logspace(np.log10(0.02), np.log10(2.0e5), n_grid)
    best = {t.name: {"in_band": np.inf, "params": None} for t in tasks}
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
                    for t in tasks:
                        i = int(np.searchsorted(w, t.omega_low))
                        if i >= w.size:
                            continue
                        val = float(suffix[i])
                        if val < best[t.name]["in_band"]:
                            best[t.name] = {"in_band": val, "params": prm}

    if verbose:
        print("    examined " + str(n_examined) + ", peak-feasible " + str(n_feasible))

    out = {}
    for t in tasks:
        b = best[t.name]
        if b["params"] is None:
            out[t.name] = {"mechanism": "M2_tuned_mass_damper",
                           "status": "no_witness_found", "exact": False,
                           "detail": "no peak-feasible design found"}
            continue
        ok = b["in_band"] <= t.T_iso
        out[t.name] = {
            "mechanism": "M2_tuned_mass_damper",
            "status": "feasible" if ok else "no_witness_found",
            "exact": False,
            "best_in_band_T": float(b["in_band"]),
            "limit": float(t.T_iso),
            "shortfall_percent": float(100.0 * (b["in_band"] / t.T_iso - 1.0)),
            "params": {"omega_n1": b["params"][0], "zeta1": b["params"][1],
                       "mu": b["params"][2], "ratio": b["params"][3],
                       "zeta2": b["params"][4]},
        }
    return out
