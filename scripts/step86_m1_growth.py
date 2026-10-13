"""Step 86 - M1 close-out: g(N) for the LIBRARY, measured size by size.

Roadmap section 9, milestone M1:

    one certificate that is sound, cheap, class-level, with an explicit domain tag
    and g(N) -> infinity
    falsified if: the direction of approach cannot be pinned down (where Lambda_2 died),
                  or g(N) turns out bounded

Finding 050 settled the FIRST member: the modal certificate C1 rules out every structure with
fewer than m modes, so g(N) = sum over k < m of N(k), which does not contain N at all.  It landed in
section 5.4's row 1 - "no crossing ever; decoration" - and its coverage was measured falling from
1.25e-01 to 1.13e-16.

**But section 5.4's library argument needs a different object.**  It says k = O(log N/log(1/(1-f)))
certificates suffice when each covers a fraction f of what REMAINS, and that k grows additively
while N grows multiplicatively.  That is a claim about the LIBRARY, and it holds only if f is
bounded below by a constant at every N.

**That is measurable and has never been measured.**  The four-certificate coverage in Findings 023 to
025 came from one ensemble spanning n = 2..8; a fraction of that ensemble is not a fraction of the
space at a given n.  This samples structures with EXACTLY n masses, uniformly from the space at that
n, and measures each certificate's coverage as n grows.

    if coverage stays bounded below  ->  g(N) = Theta(N) -> infinity, and M1 is satisfied
    if coverage falls like N(n-1)/N(n)  ->  only C1 is being measured, and M1 is not satisfied
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.structure import ensemble
from ecdr.structure.counting import space_size

line = "=" * 104
OUT = pathlib.Path(__file__).resolve().parents[1] / "runs"
NS = list(range(3, 9))
PER_N = 400


def cuts(s):
    """The four certificates, each as the quantity it compares to a threshold."""
    M, C, K, f, g = s.matrices()
    masses = np.asarray(s.masses, dtype=float)
    # C3 slow: Rayleigh with the trial vector 1, omega_1^2 <= sum k_ground / sum m
    c3 = float(sum(s.ground_k.values()) / masses.sum()) if s.ground_k else np.inf
    # C4 fast: omega_n^2 <= max_i (K_ii + sum_{j!=i} |K_ij|) / m_i
    diag = np.diag(K).copy()
    off = np.abs(K).sum(axis=1) - np.abs(diag)
    c4 = float(np.max((diag + off) / masses))
    return {"modal_n": s.n, "slow": c3, "fast": c4}


print(line)
print("EACH CERTIFICATE'S COVERAGE, sampled uniformly from the space at each n")
print(line)
print("  " + "n".rjust(3) + "N(n)".rjust(24) + "m-modal covers".rjust(16)
      + "slow <= tau covers".rjust(19) + "fast <= tau covers".rjust(19)
      + "  tau used".rjust(10))
rows = []
for n in NS:
    ens = ensemble(seed=900 + n, count=PER_N, n_lo=n, n_hi=n)
    cs = [cuts(s) for s in ens]
    N = space_size(n)
    # modal: a FIXED requirement of m = 4 harmonics, so the coverage is the fraction with n < 4
    m_req = 4
    f_modal = float(np.mean([c["modal_n"] < m_req for c in cs]))
    # the covering certificates: pick tau so that at the SMALLEST n the coverage is about a half,
    # then hold tau FIXED and see what happens to the coverage as n grows
    rows.append({"n": n, "N": int(N), "f_modal": f_modal,
                 "slow_vals": [c["slow"] for c in cs],
                 "fast_vals": [c["fast"] for c in cs]})

# calibrate tau once, at n = 3, to a target coverage of about one half
TARGET = 0.5
tau_slow = float(np.quantile(rows[0]["slow_vals"], TARGET))
tau_fast = float(np.quantile(rows[0]["fast_vals"], TARGET))
print("  tau_slow and tau_fast calibrated at n = 3 to cover " + format(TARGET, ".0%")
      + ", then HELD FIXED:")
print("    tau_slow = " + format(tau_slow, ".6e") + "   tau_fast = " + format(tau_fast, ".6e"))
print()
print("  " + "n".rjust(3) + "N(n)".rjust(24) + "C1 modal".rjust(12) + "C3 slow".rjust(12)
      + "C4 fast".rjust(12) + "C3 or C4".rjust(12) + "g_C3".rjust(22) + "g_C4".rjust(22))
for r in rows:
    f3 = float(np.mean([v <= tau_slow for v in r["slow_vals"]]))
    f4 = float(np.mean([v <= tau_fast for v in r["fast_vals"]]))
    both = float(np.mean([(a <= tau_slow) or (b <= tau_fast)
                          for a, b in zip(r["slow_vals"], r["fast_vals"])]))
    r.update({"f_slow": f3, "f_fast": f4, "f_either": both,
              "g_slow": f3 * r["N"], "g_fast": f4 * r["N"]})
    print("  " + str(r["n"]).rjust(3) + format(r["N"], ".4e").rjust(24)
          + format(r["f_modal"], ".4f").rjust(12) + format(f3, ".4f").rjust(12)
          + format(f4, ".4f").rjust(12) + format(both, ".4f").rjust(12)
          + format(r["g_slow"], ".3e").rjust(22) + format(r["g_fast"], ".3e").rjust(22))

print()
print(line)
print("VERDICT - which certificate carries g(N) -> infinity, if any")
print(line)
first, last = rows[0], rows[-1]
print("  C1 modal coverage : " + format(first["f_modal"], ".4f") + " at n=" + str(first["n"])
      + "  ->  " + format(last["f_modal"], ".4f") + " at n=" + str(last["n"]))
print("  C3 slow coverage  : " + format(first["f_slow"], ".4f") + " at n=" + str(first["n"])
      + "  ->  " + format(last["f_slow"], ".4f") + " at n=" + str(last["n"]))
print("  C4 fast coverage  : " + format(first["f_fast"], ".4f") + " at n=" + str(first["n"])
      + "  ->  " + format(last["f_fast"], ".4f") + " at n=" + str(last["n"]))
print()
survives3 = all(r["f_slow"] > 0.05 for r in rows)
survives4 = all(r["f_fast"] > 0.05 for r in rows)
print("  C3 coverage stays above 0.05 at every n : " + str(survives3))
print("  C4 coverage stays above 0.05 at every n : " + str(survives4))
print()
if survives3 or survives4:
    which = []
    if survives3:
        which.append("C3 (slow)")
    if survives4:
        which.append("C4 (fast)")
    print("  ** " + " and ".join(which) + " has coverage bounded below by a constant as n grows. **")
    print()
    print("  So g(N) = coverage * N(n) is Theta(N(n)) -> infinity for THAT certificate, and the")
    print("  library condition of section 5.4 - each cut covering a constant fraction of what")
    print("  remains - is satisfiable by a scale-free invariant rather than by the modal count.")
    print("  ** M1's falsifier - 'g(N) turns out bounded' - is not triggered for these members. **")
else:
    print("  ** No certificate here has coverage bounded below. ** Then every member is C1-shaped,")
    print("  the library argument of section 5.4 has no member to stand on, and M1's falsifier")
    print("  'g(N) turns out bounded' IS triggered. That is the honest outcome and it would mean")
    print("  the crossing in section 8 rests on the certificate being cheap, not on it covering.")

OUT.mkdir(exist_ok=True)
(OUT / "m1_growth.json").write_text(json.dumps(
    {"rows": rows, "tau_slow": tau_slow, "tau_fast": tau_fast,
     "C3_survives": survives3, "C4_survives": survives4}, indent=1), encoding="utf-8")
print()
print("wrote runs/m1_growth.json")
