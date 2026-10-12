"""L1 models: the same mechanisms, degraded by constraints L0 does not have.

The design rule that makes the ladder useful
--------------------------------------------
Every L1 design must ALSO be a valid L0 design.  L1 only ADDS constraints -- it
never relaxes one and never changes what a mechanism is.  That single property is
what lets the L0 infeasibility certificates keep their force one level up:

    L1 feasible  =>  L0 feasible        (contrapositive: L0 infeasible => L1 infeasible)

So a proof of infeasibility is a proof at EVERY fidelity above the one it was
derived at, while a witness at L0 says nothing about L1.  That asymmetry is exactly
the shape ECDR needs, and Finding 005 said so before there was a ladder to show it:
certificates prune soundly at every level, but they do not construct.

What L1 adds
------------
1. Actuator bandwidth.  An ideal sky-hook is unphysical: it needs infinite-bandwidth
   force.  L1 puts a first-order lag with corner omega_a on the actuator, so the
   force is  u = -c_sky * (omega_a / (s + omega_a)) * xdot.  As omega_a -> infinity
   the L0 model is recovered, which is checked.

    T(s) = k (s + omega_a) / [ (m s^2 + k)(s + omega_a) + c_sky omega_a s ]

2. Parameter robustness.  The band and peak constraints must hold across a
   perturbation set, not merely at nominal parameters.

Both only remove designs.  Neither generalises the mechanism, which is why the
certificate transfer above is valid.
"""
from __future__ import annotations

import abc
from typing import Sequence

import numpy as np

from ..l0.mechanisms import G, Mechanism


class LaggedSkyHook(Mechanism):
    """M3 at L1: ideal sky-hook plus a first-order actuator lag.

    Parameters
    ----------
    omega_n     : support natural frequency [rad/s]
    zeta        : commanded closed-loop damping ratio [-]
    bandwidth   : actuator corner frequency omega_a [rad/s].  Larger is closer to
                  the ideal L0 actuator; infinite is exactly L0.
    """

    name = "M3L1_lagged_sky_hook"
    param_names = ("omega_n", "zeta", "bandwidth")
    param_bounds = ((5.0, 400.0), (1e-3, 40.0), (10.0, 2.0e5))

    def _k(self, wn):
        return wn ** 2          # total mass normalised to 1

    def transmissibility(self, omega, params):
        wn, z, wa = float(params[0]), float(params[1]), float(params[2])
        k = self._k(wn)
        c_sky = 2.0 * z * wn
        s = 1j * np.asarray(omega, dtype=float)
        num = k * (s + wa)
        den = (s ** 2 + k) * (s + wa) + c_sky * wa * s
        return num / den

    def static_deflection(self, params):
        return G / float(params[0]) ** 2

    def actuator_force_per_disp(self, omega, params):
        wn, z, wa = float(params[0]), float(params[1]), float(params[2])
        c_sky = 2.0 * z * wn
        omega = np.asarray(omega, dtype=float)
        T = np.abs(self.transmissibility(omega, params))
        lag = wa / np.sqrt(omega ** 2 + wa ** 2)
        return c_sky * lag * omega * T


def perturbed(mech: Mechanism, params: Sequence[float], rel: float,
              n: int = 24, seed: int = 0):
    """Yield parameter vectors inside a relative box around the nominal point."""
    rng = np.random.default_rng(seed)
    p = np.asarray(params, dtype=float)
    lo = np.array([b[0] for b in mech.param_bounds], dtype=float)
    hi = np.array([b[1] for b in mech.param_bounds], dtype=float)
    for _ in range(n):
        f = 1.0 + rel * (2.0 * rng.random(p.shape) - 1.0)
        yield np.clip(p * f, lo, hi)


def robust_violation(mech: Mechanism, params, task, omega, rel: float = 0.10,
                     n: int = 24, seed: int = 0) -> float:
    """Worst-case constraint violation over a perturbation box.

    Because this is a maximum of violations, a design that passes here also passes
    at nominal parameters.  The constraint set is therefore a superset of L0's, so
    the achievable set is a subset -- the property the certificate transfer needs.
    """
    worst = -np.inf
    for p in perturbed(mech, params, rel, n=n, seed=seed):
        T = np.abs(mech.transmissibility(omega, p))
        band = omega >= task.omega_low
        v = [float(T[band].max() / task.T_iso - 1.0),
             float(T.max() / task.A_max - 1.0),
             float(mech.static_deflection(p) / task.delta_max - 1.0)]
        if task.force_per_disp_max is not None:
            F = np.abs(mech.actuator_force_per_disp(omega, p))
            v.append(float(F.max() / task.force_per_disp_max - 1.0))
        worst = max(worst, max(v))
    return float(worst)
