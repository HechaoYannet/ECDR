"""Layer A, second cut: a general mechanical network, evaluated at L0.

Any structure in the graph space becomes a linear mechanical network, so an invariant
can be evaluated on the whole ensemble rather than on a hand-written mechanism.  This is
what turns the census from counting into physics.

Model
-----
  * nodes i = 0..n-1 are masses m_i, node 0 is the payload
  * each edge (i, j) is a spring k_ij in parallel with a damper c_ij
  * each grounded node i has a spring k_i and damper c_i to ground
  * ground motion x_g enters through the ground elements only

    M x'' + C x' + K x = f x_g + g x_g'

    K_ii = sum of incident spring stiffnesses + ground stiffness
    K_ij = -k_ij          C built identically          f_i = k_i^g,  g_i = c_i^g

    T(s) = e_0^T (M s^2 + C s + K)^{-1} (f + g s)

Two SOUND, topology-independent bounds are exposed, because they are the first
candidates for certificates whose predicate might be scale-free:

  static_deflection   payload sag under gravity = (K^{-1} m g)_0.  Pure statics; no
                      dynamics, no assumptions beyond linear springs and equilibrium.
  mode_count          the number of degrees of freedom, which upper-bounds the number of
                      independent harmonics in the free response.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

G = 9.80665


@dataclass
class Structure:
    """A mechanical network: masses, edges with component values, and ground ties."""

    masses: np.ndarray
    springs: dict           # (i, j) with i < j  ->  stiffness
    dampers: dict           # (i, j) with i < j  ->  damping
    ground_k: dict          # node -> stiffness
    ground_c: dict          # node -> damping

    @property
    def n(self) -> int:
        return int(self.masses.size)

    def matrices(self):
        n = self.n
        K = np.zeros((n, n))
        C = np.zeros((n, n))
        for (i, j), k in self.springs.items():
            K[i, i] += k
            K[j, j] += k
            K[i, j] -= k
            K[j, i] -= k
        for (i, j), c in self.dampers.items():
            C[i, i] += c
            C[j, j] += c
            C[i, j] -= c
            C[j, i] -= c
        f = np.zeros(n)
        g = np.zeros(n)
        for i, k in self.ground_k.items():
            K[i, i] += k
            f[i] += k
        for i, c in self.ground_c.items():
            C[i, i] += c
            g[i] += c
        return np.diag(self.masses), C, K, f, g

    def transmissibility(self, omega):
        """Batched over frequency.  A per-frequency Python loop is unusably slow for
        the 1e5-point grids the waterbed integral needs."""
        M, C, K, f, g = self.matrices()
        omega = np.atleast_1d(np.asarray(omega, dtype=float))
        s = 1j * omega
        A = (M[None, :, :] * (s ** 2)[:, None, None]
             + C[None, :, :] * s[:, None, None]
             + K[None, :, :])
        # b must be (nfreq, n, 1): numpy's batched solve takes (m,m) and (m,1), not (m,n)
        rhs = (f[None, :] + g[None, :] * s[:, None])[:, :, None]
        return np.linalg.solve(A, rhs)[:, 0, 0]

    # ---- sound, topology-independent bounds -------------------------------
    def static_deflection(self) -> float:
        """Payload sag under gravity: (K^{-1} m g)_0.  Statics only."""
        M, C, K, f, g = self.matrices()
        rhs = self.masses * G
        return float(np.linalg.solve(K, rhs)[0])

    def mode_count(self) -> int:
        """Degrees of freedom, which caps the number of free-response harmonics."""
        return self.n
