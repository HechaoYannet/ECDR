"""Step 5 - the waterbed invariant, verified stably and at high precision."""
import _bootstrap  # noqa: F401
import numpy as np

from ecdr.l0 import G, IsolationTask
from ecdr.l0.invariants import (check_identity, tf_coeffs,
                                waterbed_integral_vieta, waterbed_integral_numeric)

line = "=" * 78
print(line)
print("A. Vieta closed form vs the exact physical value (should be machine zero)")
print(line)
cases = [
    ("M1_passive_sdof", (99.03, 0.5426)), ("M1_passive_sdof", (40.0, 0.05)),
    ("M1_passive_sdof", (314.16, 0.9)),   ("M1_passive_sdof", (10.0, 0.001)),
    ("M3_sky_hook_active", (99.03, 0.3832)), ("M3_sky_hook_active", (99.03, 2.0)),
    ("M3_sky_hook_active", (150.0, 0.1)),
    ("M2_tuned_mass_damper", (99.03, 0.1, 0.05, 1.0, 0.2)),
    ("M2_tuned_mass_damper", (99.03, 0.457, 0.057, 0.744, 0.295)),
    ("M2_tuned_mass_damper", (99.03, 0.0, 0.3, 2.0, 0.5)),
    ("M2_tuned_mass_damper", (120.0, 0.25, 0.4, 3.0, 0.9)),
]
worst = 0.0
for name, prm in cases:
    r = check_identity(name, prm)
    worst = max(worst, r["vieta_vs_exact"])
    print("  " + name.ljust(22) + " vieta=" + format(r["vieta"], "+.12e")
          + "  exact=" + format(r["exact"], "+.12e")
          + "  |diff|=" + format(r["vieta_vs_exact"], ".2e"))
print("  worst |vieta - exact| = " + format(worst, ".3e"))

print()
print(line)
print("B. the invariant as a function of the mechanism")
print(line)
print("  integral_0^inf ln|T(jw)|/w^2 dw = (pi/2) * ( n1/n0 - d1/d0 )")
print()
print("  M1 passive SDOF      n1/n0 = 2*zeta/wn   and   d1/d0 = 2*zeta/wn   ->  0  for ALL parameters")
print("  M2 tuned mass damper n1/n0 = c2/k2       and   d1/d0 = c2/k2       ->  0  for ALL parameters")
print("  M3 sky-hook active   n1/n0 = 0           and   d1/d0 = 2*zeta/wn   -> -pi*zeta/wn  < 0")
print()
print("  So the passive classes have ZERO weighted log-area: every decibel of")
print("  isolation is paid for, exactly, by a decibel of amplification.  The sky-hook")
print("  has a strictly negative budget, i.e. it is allowed net isolation, and the")
print("  budget grows with damping and with softness (small wn).")

print()
print(line)
print("C. high-precision check of the integral itself (mpmath, 40 digits)")
print(line)
try:
    from mpmath import mp, mpf, quad, log, sqrt, mpc
    mp.dps = 40

    def hp_integral(num, den):
        nc = [mpf(str(c)) for c in num]
        dc = [mpf(str(c)) for c in den]

        def f(w):
            s = mpc(0, w)
            n = sum(nc[i] * s ** (len(nc) - 1 - i) for i in range(len(nc)))
            d = sum(dc[i] * s ** (len(dc) - 1 - i) for i in range(len(dc)))
            return log(abs(n / d)) / (w * w)

        total = mpf(0)
        edges = [mpf("1e-12"), mpf("1e-6"), mpf("1e-3"), mpf("1e-1"), mpf(1),
                 mpf(10), mpf("1e2"), mpf("1e4"), mpf("1e6"), mpf("1e12")]
        for a, b in zip(edges[:-1], edges[1:]):
            total += quad(f, [a, b])
        return total

    tests = [
        ("M1_passive_sdof", (99.03, 0.5426), 0.0),
        ("M3_sky_hook_active", (99.03, 0.3832), -np.pi * 0.3832 / 99.03),
        ("M2_tuned_mass_damper", (99.03, 0.457, 0.057, 0.744, 0.295), 0.0),
        ("M2_tuned_mass_damper", (120.0, 0.25, 0.4, 3.0, 0.9), 0.0),
    ]
    for name, prm, expect in tests:
        num, den = tf_coeffs(name, prm)
        got = hp_integral(num, den)
        print("  " + name.ljust(22) + " hp=" + mp.nstr(got, 12).ljust(18)
              + " expected=" + mp.nstr(mpf(str(expect)), 12))
except ImportError:
    print("  (mpmath not installed; skipped)")
