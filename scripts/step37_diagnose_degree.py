"""Step 37 - diagnostic on one network: which coefficient degree and which root set is right?

Both earlier attempts had a broken verification:
  step 35 checked polyroots against its OWN polynomial
  step 36 evaluated the true P into a REAL array, silently discarding the imaginary part
          of every complex root (ComplexWarning), so |P(z)| was |P(Re z)| - meaningless

This prints, for one network, the fitted coefficients at degree 2n-1 and 2n, both root
sets, the TRUE |P(z)| at each root (complex arithmetic), and the resulting sum.  Nothing
is assumed.
"""
import _bootstrap  # noqa: F401
import numpy as np
import mpmath as mp

from ecdr.structure import Structure, ensemble, waterbed_numeric

mp.mp.dps = 60
IDX = 76
line = "=" * 90

ens = ensemble(seed=5, count=200, n_lo=2, n_hi=8)
s = ens[IDX]
M, C, K, f, g = s.matrices()
sigma = 1.0 / float(np.sqrt(np.max(np.abs(K)) / np.max(M)))


def P_at(points):
    """P at complex points, in COMPLEX arithmetic."""
    out = np.empty(len(points), dtype=complex)
    for i, si in enumerate(points):
        A = M * si ** 2 + C * si + K
        out[i] = np.linalg.det(A) * np.linalg.solve(A, f + g * si)[0]
    return out


print(line)
print("network " + str(IDX) + ", n = " + str(s.n) + ", so 2n = " + str(2 * s.n))
print("  numerical waterbed integral W = " + format(waterbed_numeric(s), ".10e"))
print(line)

for deg in (2 * s.n - 1, 2 * s.n):
    m = 8 * deg + 20
    t = np.linspace(1.0, 8.0, m)
    vals = P_at(t / sigma).real
    coef_t = np.polynomial.polynomial.polyfit(t, vals, deg)
    coef = np.array([coef_t[k] * sigma ** k for k in range(deg + 1)])
    scale = np.max(np.abs(coef))
    print()
    print("  degree " + str(deg) + "   |coef| max " + format(float(scale), ".4e")
          + "   leading |c_" + str(deg) + "| = " + format(float(abs(coef[-1])), ".4e")
          + "   (relative " + format(float(abs(coef[-1]) / scale), ".2e") + ")")

    # numpy roots on the float coefficients
    rn = np.roots(coef[::-1])
    rn_rhp = rn[rn.real > 1e-9]
    pv_n = np.abs(P_at(rn_rhp)) / scale if rn_rhp.size else np.array([])
    sum_n = np.pi * np.sum((1.0 / rn_rhp).real) if rn_rhp.size else 0.0
    print("    numpy roots  : " + str(rn_rhp.size) + " in RHP"
          + "   pi*sum Re(1/z) = " + format(float(sum_n), ".8e"))
    if rn_rhp.size:
        print("      |P(z)|/scale at them : " + "  ".join(format(v, ".2e") for v in pv_n))

    # mpmath roots on the same coefficients
    mc = [mp.mpf(float(coef[k])) for k in range(deg + 1)]
    rm = mp.polyroots(mc, maxsteps=400, extraprec=800)
    rm_rhp = [r for r in rm if r.real > mp.mpf("1e-12")]
    if rm_rhp:
        pv_m = np.abs(P_at(np.array([complex(r) for r in rm_rhp]))) / scale
        sum_m = float(mp.pi * sum((1 / r).real for r in rm_rhp))
    else:
        pv_m, sum_m = np.array([]), 0.0
    print("    mpmath roots : " + str(len(rm_rhp)) + " in RHP"
          + "   pi*sum Re(1/z) = " + format(sum_m, ".8e"))
    if len(rm_rhp):
        print("      |P(z)|/scale at them : " + "  ".join(format(v, ".2e") for v in pv_m))
        print("      roots : " + ", ".join(format(complex(r).real, ".6g")
                                          + ("+" if complex(r).imag >= 0 else "-")
                                          + format(abs(complex(r).imag), ".4g") + "j"
                                          for r in rm_rhp))
