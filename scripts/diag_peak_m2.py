"""Why does the exact-peak routine miss the sharp primary resonance?"""
import _bootstrap  # noqa: F401
import numpy as np
from ecdr.l0.invariants import tf_coeffs
from ecdr.l0.peaks import peak_transmissibility, _abs_sq_poly
from ecdr.l0 import TunedMassDamper

wn_min = 99.0285
prm = (wn_min, 0.001, 0.000316228, 10.0, 0.0196023)
num, den = tf_coeffs("M2_tuned_mass_damper", prm)
print("num =", num)
print("den =", den)

pk, wp = peak_transmissibility(num, den)
print("routine says peak =", pk, " at w =", wp)

# dense local scan around the primary natural frequency
w = np.linspace(95.0, 105.0, 2000001)
T = np.abs(TunedMassDamper().transmissibility(w, prm))
i = int(np.argmax(T))
print("dense scan [95,105] peak =", T[i], " at w =", w[i])

# wide scan
w2 = np.logspace(np.log10(0.1), np.log10(1e5), 2000001)
T2 = np.abs(TunedMassDamper().transmissibility(w2, prm))
j = int(np.argmax(T2))
print("wide scan peak =", T2[j], " at w =", w2[j])

P = _abs_sq_poly(num)
Q = _abs_sq_poly(den)
print("\nP (asc) =", P)
print("Q (asc) =", Q)
dP = np.polyder(P[::-1])[::-1]
dQ = np.polyder(Q[::-1])[::-1]
a = np.convolve(dP, Q); b = np.convolve(P, dQ)
n = max(a.size, b.size)
aa = np.zeros(n); aa[:a.size] = a
bb = np.zeros(n); bb[:b.size] = b
crit = aa - bb
print("critical poly (asc) =", crit)
print("cond-ish: max/min |coef| =", np.max(np.abs(crit)) / max(np.min(np.abs(crit[crit != 0])), 1e-300))
print("numpy roots (x):", np.sort_complex(np.roots(crit[::-1])))

try:
    from mpmath import mp, polyroots, mpf, mpc
    mp.dps = 60
    roots = polyroots([mpf(str(c)) for c in crit[::-1]], maxsteps=200, extraprec=400)
    print("\nmpmath roots (x), 60 dps:")
    for r in roots:
        print("   ", mp.nstr(r, 12), "   -> w =", mp.nstr(mp.sqrt(abs(r)), 10) if abs(mp.im(r)) < mpf("1e-20") else "-")
except ImportError:
    print("mpmath missing")
