"""L0 mechanism models for the precision-positioning vibration-isolation testbed.

Physical setting
----------------
A precision positioning stage (payload) sits on a support that connects it to a
vibrating ground.  We care about the *absolute displacement transmissibility*

    T(jw) = X_payload(jw) / X_ground(jw)

because payload motion relative to inertial space is what destroys positioning
accuracy.  All masses are normalised so that the total supported mass is 1; every
force-like quantity below is therefore "per unit total supported mass".

Mechanisms
----------
M1  PassiveSDOF       single degree of freedom: one spring + one damper
M2  TunedMassDamper   two degrees of freedom: support spring/damper plus an
                      absorber mass on its own spring/damper
M3  SkyHookActive     support spring plus an ideal actuator producing a force
                      proportional to absolute payload velocity

Why these three
---------------
M1 is the textbook starting point and, crucially, its achievable performance is
*analytically bounded* -- see certificates.py.  M2 and M3 are the two canonical
escapes: add a dynamic degree of freedom, or close a control loop.
"""
from __future__ import annotations

import abc
from typing import Sequence

import numpy as np

G = 9.80665  # standard gravity, m/s^2


class Mechanism(abc.ABC):
    """Common interface every L0 mechanism must expose."""

    name: str = "mechanism"
    param_names: tuple[str, ...] = ()
    param_bounds: tuple[tuple[float, float], ...] = ()

    @abc.abstractmethod
    def transmissibility(self, omega: np.ndarray, params: Sequence[float]) -> np.ndarray:
        """Complex absolute displacement transmissibility at angular frequency omega."""

    @abc.abstractmethod
    def static_deflection(self, params: Sequence[float]) -> float:
        """Static sag of the support spring under the full supported weight [m]."""

    def actuator_force_per_disp(self, omega: np.ndarray, params: Sequence[float]) -> np.ndarray:
        """Actuator force amplitude per unit ground displacement amplitude [1/s^2].

        Zero for purely passive mechanisms.  This is the spectrum-free way to
        state an actuator-authority constraint: it does not presume a particular
        ground-motion PSD, only a reference amplitude.
        """
        return np.zeros_like(np.asarray(omega, dtype=float))

    def n_params(self) -> int:
        return len(self.param_names)


class PassiveSDOF(Mechanism):
    """M1: one spring, one damper.

    Parameters
    ----------
    omega_n : support natural frequency [rad/s]
    zeta    : support damping ratio [-]

    Transfer function
    -----------------
        T(s) = (wn^2 + 2*zeta*wn*s) / (s^2 + 2*zeta*wn*s + wn^2)

    The numerator is non-constant exactly because the damper transmits ground
    motion directly.  That numerator term, 2*zeta*wn*s, is what makes the
    high-frequency rolloff only -20 dB/dec instead of -40 dB/dec, and it is the
    root of the fundamental trade-off encoded in the certificate.
    """

    name = "M1_passive_sdof"
    param_names = ("omega_n", "zeta")
    param_bounds = ((5.0, 400.0), (1e-3, 2.0))

    def transmissibility(self, omega, params):
        wn, z = float(params[0]), float(params[1])
        s = 1j * np.asarray(omega, dtype=float)
        return (wn**2 + 2.0 * z * wn * s) / (s**2 + 2.0 * z * wn * s + wn**2)

    def static_deflection(self, params):
        wn = float(params[0])
        return G / wn**2


class TunedMassDamper(Mechanism):
    """M2: support spring/damper plus an absorber mass on its own spring/damper.

    Parameters
    ----------
    omega_n1 : support natural frequency, sqrt(k1 / M_total) [rad/s]
    zeta1    : support damping ratio, c1 / (2*sqrt(k1*M_total)) [-]
    mu       : absorber mass / total mass, m2 / (m1 + m2) [-]
    ratio    : absorber tuning, omega_n2 / omega_n1 [-]
    zeta2    : absorber damping ratio [-]

    Equations of motion in absolute coordinates (total mass normalised to 1):

        M qdd + C qd + K q = f_b * x_g + g_b * xd_g

    with q = [x1, x2]^T.  Note that the high-frequency rolloff is still governed
    by the primary path: with zeta1 -> 0 the numerator becomes constant and the
    rolloff reaches -40 dB/dec, which is exactly the extra freedom M1 lacks.
    """

    name = "M2_tuned_mass_damper"
    param_names = ("omega_n1", "zeta1", "mu", "ratio", "zeta2")
    param_bounds = ((5.0, 400.0), (1e-4, 1.0), (1e-3, 0.5), (0.1, 5.0), (1e-4, 1.0))

    def _matrices(self, params):
        wn1, z1, mu, ratio, z2 = (float(v) for v in params)
        m_total = 1.0
        m1 = m_total * (1.0 - mu)
        m2 = m_total * mu
        wn2 = ratio * wn1

        k1 = wn1**2 * m_total
        c1 = 2.0 * z1 * np.sqrt(k1 * m_total)
        k2 = wn2**2 * m2
        c2 = 2.0 * z2 * np.sqrt(k2 * m2)

        M = np.array([[m1, 0.0], [0.0, m2]])
        K = np.array([[k1 + k2, -k2], [-k2, k2]])
        C = np.array([[c1 + c2, -c2], [-c2, c2]])
        f_b = np.array([k1, 0.0])
        g_b = np.array([c1, 0.0])
        return M, C, K, f_b, g_b, k1

    def transmissibility(self, omega, params):
        M, C, K, f_b, g_b, _ = self._matrices(params)
        omega = np.atleast_1d(np.asarray(omega, dtype=float))
        s = 1j * omega
        n = s.size

        # Stacked 2x2 systems solved in one batched call; the naive per-frequency
        # loop is what makes a five-parameter witness search infeasible.
        A = np.empty((n, 2, 2), dtype=complex)
        A[:, 0, 0] = M[0, 0] * s**2 + C[0, 0] * s + K[0, 0]
        A[:, 0, 1] = C[0, 1] * s + K[0, 1]
        A[:, 1, 0] = C[1, 0] * s + K[1, 0]
        A[:, 1, 1] = M[1, 1] * s**2 + C[1, 1] * s + K[1, 1]

        # b must carry an explicit (..., M, K) shape for the batched solve
        rhs = np.empty((n, 2, 1), dtype=complex)
        rhs[:, 0, 0] = f_b[0] + g_b[0] * s
        rhs[:, 1, 0] = f_b[1] + g_b[1] * s

        return np.linalg.solve(A, rhs)[:, 0, 0]

    def static_deflection(self, params):
        wn1 = float(params[0])
        return G / wn1**2


class SkyHookActive(Mechanism):
    """M3: support spring plus an ideal sky-hook actuator.

    Parameters
    ----------
    omega_n : support natural frequency, sqrt(k / m) [rad/s]
    zeta    : closed-loop damping ratio contributed by the actuator [-]

    The actuator force is u = -c_sky * xd_payload with c_sky = 2*zeta*wn*m, so

        T(s) = wn^2 / (s^2 + 2*zeta*wn*s + wn^2)

    A constant numerator means -40 dB/dec rolloff with *no* damping feedthrough,
    which is precisely what a passive damper cannot achieve.  The price is
    actuator force, exposed through actuator_force_per_disp.
    """

    name = "M3_sky_hook_active"
    param_names = ("omega_n", "zeta")
    param_bounds = ((5.0, 400.0), (1e-3, 2.0))

    def transmissibility(self, omega, params):
        wn, z = float(params[0]), float(params[1])
        s = 1j * np.asarray(omega, dtype=float)
        return wn**2 / (s**2 + 2.0 * z * wn * s + wn**2)

    def static_deflection(self, params):
        wn = float(params[0])
        return G / wn**2

    def actuator_force_per_disp(self, omega, params):
        wn, z = float(params[0]), float(params[1])
        omega = np.asarray(omega, dtype=float)
        T = np.abs(self.transmissibility(omega, params))
        # |U / X_g| = c_sky * w * |X_p / X_g|, with c_sky = 2*zeta*wn (m_total = 1)
        return 2.0 * z * wn * omega * T


MECHANISMS: tuple[Mechanism, ...] = (PassiveSDOF(), TunedMassDamper(), SkyHookActive())
