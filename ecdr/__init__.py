"""ECDR - Evidence-Guided Open-Ended Engineering Design.

Fidelity ladder
---------------
L0  analytic / linear frequency-domain models (this package: ecdr.l0)
L1  nonlinear, saturating, perturbed numerical simulation
L2  independent implementation or physical test bench (never used for search)
"""

__all__ = ["l0"]
