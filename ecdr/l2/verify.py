"""L2 - steady-state transmissibility by time-domain integration in Julia.

What this rung is for
---------------------
docs/decisions/001 states the principle: a second implementation by the same author is not
independent validation.  L0 and L1 are both Python on the SciPy stack and share their
modelling, so neither can check the other.  L2 exists to put a different lineage between the
model and the number.

What this rung does and does not provide
----------------------------------------
DOES: a categorically different numerical route.  L0 and L1 solve the algebraic system
(K - w^2 M + i w C) X = (f + i w g); this integrates M x'' + C x' + K x = f x_g + g x_g'
in time until steady state and reads the amplitude.  No formula is shared, so an error in
the frequency-domain algebra, in the assembly of M/C/K, or in the sign or shape of the ground
coupling shows up as a disagreement.

DOES NOT: independent MODELLING.  The equations of motion are the same author's.  Documented
as a limitation rather than glossed.

The intended kernel was OpenModelica, for both independence and alignment with industrial
multi-domain plant modelling.  It is not obtainable in this environment - see
docs/findings/026.  Julia plus DifferentialEquations.jl is a different language, a different
compiler and a different integrator suite, which satisfies the independence requirement
though not the modelling-paradigm one.
"""
from __future__ import annotations

import pathlib

import numpy as np

_JL = None
_KERNEL = pathlib.Path(__file__).resolve().parent / "kernel_julia.jl"


def _julia():
    global _JL
    if _JL is None:
        from juliacall import Main as jl
        jl.include(str(_KERNEL))
        _JL = jl
    return _JL


def available() -> bool:
    try:
        import juliacall  # noqa: F401
        return True
    except Exception:
        return False


def state_space_amplitude(A, B1, B2, crow, omegas, **kw):
    """Steady-state amplitude of crow' y for a general first-order state space."""
    jl = _julia()
    res = jl.state_space_amplitude(
        jl.Array(np.asarray(A, dtype=float)),
        jl.Array(np.asarray(B1, dtype=float)),
        jl.Array(np.asarray(B2, dtype=float)),
        jl.Array(np.asarray(crow, dtype=float)),
        jl.Array(np.asarray(omegas, dtype=float)),
        periods=int(kw.get("periods", 120)),
        samples_per_period=int(kw.get("samples_per_period", 800)),
    )
    return np.array([float(v) for v in res])


def transmissibility_time_domain(structure, omegas, **kw):
    """Steady-state |T| at each omega, by time-domain integration."""
    jl = _julia()
    M, C, K, f, g = structure.matrices()
    om = np.asarray(omegas, dtype=float)
    # masses must go as a VECTOR: the kernel does Minv = 1 ./ Mv and broadcasts it down
    # the rows.  Passing the diagonal MATRIX makes length(Mv) = n^2 and the state
    # dimension 2n^2, which fails at the first block assignment.
    res = jl.transmissibility_time_domain(
        jl.Array(np.asarray(structure.masses, dtype=float)),
        jl.Array(np.asarray(C, dtype=float)),
        jl.Array(np.asarray(K, dtype=float)),
        jl.Array(np.asarray(f, dtype=float)),
        jl.Array(np.asarray(g, dtype=float)),
        jl.Array(om),
        periods=int(kw.get("periods", 60)),
        samples_per_period=int(kw.get("samples_per_period", 400)),
    )
    return np.array([float(v) for v in res])
