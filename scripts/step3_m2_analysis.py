"""Step 3 - settle whether the passive TWO-degree-of-freedom mechanism can escape.

Why a structured scan rather than a black-box optimiser
------------------------------------------------------
The differential-evolution run in step 2 returned a point that violated the sag
constraint, so it failed for a boring reason and told us nothing.  Two facts
collapse the search enough to scan it exhaustively.

  1. Transmissibility depends on omega_n1 only through r = w / omega_n1.  For
     fixed dimensionless parameters the band constraint is monotone in omega_n1
     (smaller is better) and so is the sag constraint (larger is better), so the
     optimum sits exactly at omega_n1 = omega_n_min and a dimension disappears.

  2. With zeta1 -> 0 the model has the best possible high-frequency behaviour a
     passive chain can have (-40 dB/dec).

The scan below reports a *Pareto* statement, not a single number: the smallest
in-band transmissibility reachable by any member that also respects the peak
constraint.  Reporting an in-band value from a point that violates the peak
would be meaningless, which is exactly the mistake the first version made.
"""
import _bootstrap  # noqa: F401
import numpy as np

from ecdr.l0 import G, IsolationTask, TunedMassDamper
from ecdr.l0.feasibility import SEARCH_OMEGA

line = "=" * 78
np.set_printoptions(precision=6, suppress=True)
omega = SEARCH_OMEGA


def make_task(name, f_low, T_iso_db=-20.0, A_max_db=3.0, delta_mm=1.0):
    return IsolationTask(name, f_low, T_iso_db, A_max_db, delta_mm / 1e3)


def scan_family(task, mech=TunedMassDamper()):
    """Return the Pareto-best points of the passive 2-DOF family for this task."""
    wn_min = np.sqrt(G / task.delta_max)
    band = omega >= task.omega_low

    zetas1 = np.logspace(-3.0, -0.15, 16)
    mus = np.logspace(-4.5, -0.7, 22)
    ratios = np.logspace(-0.3, 0.9, 22)
    zetas2 = np.logspace(-3.0, -0.15, 16)

    best_feasible = (np.inf, None)      # min in-band T among peak-feasible points
    best_any = (np.inf, None)           # min combined violation, for reference
    n = 0
    for z1 in zetas1:
        for mu in mus:
            for ratio in ratios:
                for z2 in zetas2:
                    params = (wn_min, z1, mu, ratio, z2)
                    T = np.abs(mech.transmissibility(omega, params))
                    in_band = float(T[band].max())
                    peak = float(T.max())
                    n += 1
                    if peak <= task.A_max and in_band < best_feasible[0]:
                        best_feasible = (in_band, (z1, mu, ratio, z2, peak))
                    v = max(in_band / task.T_iso - 1.0, peak / task.A_max - 1.0)
                    if v < best_any[0]:
                        best_any = (v, (z1, mu, ratio, z2, in_band, peak))
    return best_feasible, best_any, n


def report(task):
    print(line)
    print(f"TASK {task.name}:  f_low = {task.f_low:g} Hz, T_iso = {task.T_iso_db:+.0f} dB, "
          f"A_max = {task.A_max_db:+.0f} dB, sag <= {task.delta_max * 1e3:.2f} mm")
    print(line)
    wn_min = np.sqrt(G / task.delta_max)

    # --- necessary condition 1: high-frequency asymptote vs sag -------------
    Lambda2 = task.delta_max * task.omega_low**2 * task.T_iso / G
    mu_ceiling = 1.0 - 1.0 / Lambda2

    # --- necessary condition 2: the asymptote also caps the primary damping --
    # With zeta1 > 0 the rolloff degrades to -20 dB/dec, |T| -> 2 zeta1 wn1/((1-mu) w).
    zeta1_ceiling = task.T_iso * task.omega_low / (2.0 * wn_min)   # at mu = 0, the most generous case

    print(f"  necessary condition 1 (asymptote vs sag): Lambda2 = {Lambda2:.6f}")
    if Lambda2 <= 1.0:
        print("     -> Lambda2 <= 1: PROVABLY INFEASIBLE for the whole passive chain family")
        return
    print(f"     -> requires absorber mass fraction mu <= {mu_ceiling:.6f}")
    print(f"  necessary condition 2 (asymptote vs primary damping): zeta1 <= {zeta1_ceiling:.6f} (at mu = 0)")

    best_feasible, best_any, n = scan_family(task)
    print(f"  scanned {n:,} parameter combinations at omega_n1 = omega_n_min = {wn_min:.3f} rad/s")

    print()
    if best_feasible[1] is None:
        print("  no peak-feasible member found anywhere in the family.")
    else:
        in_band, (z1, mu, ratio, z2, peak) = best_feasible
        print("  best peak-feasible member of the passive 2-DOF family:")
        print(f"     zeta1 = {z1:.6g}, mu = {mu:.6g}, ratio = {ratio:.6f}, zeta2 = {z2:.6g}")
        print(f"     in-band max |T| = {in_band:.6f}   vs limit {task.T_iso:.6f}"
              f"   ({100 * (in_band / task.T_iso - 1):+.3f} %)")
        print(f"     peak |T|        = {peak:.6f}   vs limit {task.A_max:.6f}")
        print(f"     note: mu = {mu:.4g} against a ceiling of {mu_ceiling:.4g}; "
              f"zeta1 = {z1:.4g} against a ceiling of {zeta1_ceiling:.4g}")

    print()
    print("  reference (unconstrained in peak, for context only):")
    v, (z1, mu, ratio, z2, in_band, peak) = best_any
    print(f"     combined violation {v:+.5f} at zeta1 = {z1:.4g}, mu = {mu:.4g}, "
          f"in-band {in_band:.5f}, peak {peak:.5f}")


report(make_task("T_base", 50.0))
print()
report(make_task("T_easy", 110.0))
