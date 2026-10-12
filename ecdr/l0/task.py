"""Escape-task specification for the L0 precision-positioning testbed."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class IsolationTask:
    """A design requirement the engineer must satisfy.

    Attributes
    ----------
    name : human-readable task id
    f_low : Hz, start of the isolation band.  The requirement is
        |T| <= T_iso for *every* frequency at or above f_low.
    T_iso_db : allowed transmissibility inside the band [dB].  Negative.
    A_max_db : allowed transmissibility *peak* anywhere [dB].  Positive;
        this is what forbids simply making the support arbitrarily soft.
    delta_max : m, maximum static sag of the support spring.  Combined with
        A_max_db this is the heart of the passive fundamental limit.
    force_per_disp_max : optional actuator authority limit [1/s^2, per unit
        total mass].  None means unconstrained (passive mechanisms ignore it).
    """

    name: str
    f_low: float
    T_iso_db: float
    A_max_db: float
    delta_max: float
    force_per_disp_max: float | None = None

    # ---- derived, linear units (what the physics actually uses) ----
    @property
    def omega_low(self) -> float:
        return 2.0 * np.pi * self.f_low

    @property
    def T_iso(self) -> float:
        return 10.0 ** (self.T_iso_db / 20.0)

    @property
    def A_max(self) -> float:
        return 10.0 ** (self.A_max_db / 20.0)

    def describe(self) -> str:
        parts = [
            f"task {self.name}",
            f"  isolation: |T| <= {self.T_iso:.4f} ({self.T_iso_db:+.0f} dB) for f >= {self.f_low:g} Hz"
            f"  (omega >= {self.omega_low:.2f} rad/s)",
            f"  peak:      |T| <= {self.A_max:.4f} ({self.A_max_db:+.0f} dB) at all frequencies",
            f"  sag:       static deflection <= {self.delta_max * 1e3:.3f} mm",
        ]
        if self.force_per_disp_max is not None:
            parts.append(f"  actuator:  |U/X_g| <= {self.force_per_disp_max:.3e} 1/s^2")
        return "\n".join(parts)
