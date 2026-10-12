"""Diagnose the M2 case whose numeric integral disagrees with the closed form."""
import _bootstrap  # noqa: F401
import numpy as np
from ecdr.l0.invariants import tf_coeffs, waterbed_integral_roots

prm = (99.03, 0.457, 0.057, 0.744, 0.295)
num, den = tf_coeffs("M2_tuned_mass_damper", prm)
print("num =", num)
print("den =", den)
print("closed form:", waterbed_integral_roots(num, den))

z = np.roots(num); p = np.roots(den)
print("\nzeros:", np.sort_complex(z))
print("poles:", np.sort_complex(p))

u = np.linspace(-40, 40, 400001)
w = np.exp(u)
s = 1j * w
T = np.polyval(num, s) / np.polyval(den, s)
lnT = np.log(np.abs(T))
integrand = lnT * np.exp(-u)
print("\nmax |lnT| =", np.max(np.abs(lnT)), " at w =", w[np.argmax(np.abs(lnT))])
print("max |integrand| =", np.max(np.abs(integrand)), " at w =", w[np.argmax(np.abs(integrand))])
print("total trapz =", np.trapezoid(integrand, u))

# where does the integrand blow up?
for lo, hi in [(-40,-20),(-20,-10),(-10,-2),(-2,2),(2,6),(6,10),(10,20),(20,40)]:
    m = (u >= lo) & (u <= hi)
    print("  u in [" + str(lo) + "," + str(hi) + "]  partial = "
          + format(np.trapezoid(integrand[m], u[m]), "+.6e"))

# check conditioning: is den ~ 0 anywhere on the imaginary axis?
mag = np.abs(np.polyval(den, s))
print("\nmin |den(jw)| =", mag.min(), " relative to |den| max:", mag.max())
print("min |num(jw)| =", np.abs(np.polyval(num, s)).min())

# alternative: build T from its roots and poles directly (better conditioned)
def tf_from_roots(z, p, K):
    def f(s):
        r = np.ones_like(s, dtype=complex) * K
        for zz in z:
            r = r * (1.0 - s / zz)
        for pp in p:
            r = r / (1.0 - s / pp)
        return r
    return f

K = np.real(np.polyval(num, 0.0) / np.polyval(den, 0.0))
print("\nK (T(0)) =", K)
f = tf_from_roots(z, p, K)
T2 = f(s)
lnT2 = np.log(np.abs(T2))
print("max |lnT2| =", np.max(np.abs(lnT2)), " at w =", w[np.argmax(np.abs(lnT2))])
print("root-form integral =", np.trapezoid(lnT2 * np.exp(-u), u))

# compare the two evaluations of T
rel = np.abs(T - T2) / np.maximum(np.abs(T2), 1e-300)
print("max relative difference between polyval and root forms:", np.max(rel), " at w =", w[np.argmax(rel)])
