"""Step 25 - structural features as sources of INDEPENDENT coverage.

Finding 013 concluded that independent coverage must come from certificates keyed to
different STRUCTURAL FEATURES rather than different performance metrics.  This tests
that prescription two ways:

  A. partition the failure set by structural features and see whether the failure rate
     actually differs across the partition
  B. derive and FALSIFY a concrete structural asymptote: the claim that T(s) at high
     frequency depends only on the payload's own ground tie, and nothing else in the
     network.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.structure import ensemble
from ecdr.structure.capability import profile, requirement_check

line = "=" * 90
N_STRUCT = 600
OMEGA = np.logspace(np.log10(0.5), np.log10(3.0e5), 900)
OMEGA_LOW = 2 * np.pi * 30.0

ens = ensemble(seed=5, count=N_STRUCT, n_lo=2, n_hi=8)
profs = [profile(s, OMEGA, OMEGA_LOW) for s in ens]

CAL = dict(delta_max=8.0e-3, a_max=8.0, t_iso=0.300)
rows = [requirement_check(p, CAL["delta_max"], CAL["a_max"], CAL["t_iso"]) for p in profs]
base_surv = sum(1 for r in rows if not any(r.values())) / N_STRUCT

print(line)
print("A. STRUCTURAL FEATURES - does the failure rate differ across them?")
print(line)
print("  calibration: sag <= 8 mm, peak <= 8, in-band <= 0.30   (base survival "
      + format(base_surv, ".4f") + ")")
print()


def feat(s):
    grounded_payload = 0 in s.ground_k or 0 in s.ground_c
    n_ground = len(set(s.ground_k) | set(s.ground_c))
    deg0 = sum(1 for (i, j) in s.springs if i == 0 or j == 0)
    return {"payload_grounded": grounded_payload, "n_ground": n_ground,
            "payload_degree": deg0, "n_nodes": s.n}


feats = [feat(s) for s in ens]
print("  " + "structural feature".rjust(28) + "bucket".rjust(14) + "count".rjust(8)
      + "survive".rjust(9) + "survival rate".rjust(15))
feat_rows = []
for name in ("payload_grounded", "n_ground", "payload_degree", "n_nodes"):
    vals = sorted({f[name] for f in feats})
    if len(vals) > 5:
        vals = [vals[0], vals[len(vals) // 2], vals[-1]]
    for v in vals:
        idx = [i for i, f in enumerate(feats) if f[name] == v]
        if not idx:
            continue
        sv = sum(1 for i in idx if not any(rows[i].values()))
        rate = sv / len(idx)
        feat_rows.append({"feature": name, "value": v, "count": len(idx),
                          "survive": sv, "rate": rate})
        print("  " + name.rjust(28) + str(v).rjust(14) + str(len(idx)).rjust(8)
              + str(sv).rjust(9) + format(rate, ".4f").rjust(15))
print()
grounded = [i for i, f in enumerate(feats) if f["payload_grounded"]]
notg = [i for i, f in enumerate(feats) if not f["payload_grounded"]]
rg = sum(1 for i in grounded if not any(rows[i].values())) / max(len(grounded), 1)
rn = sum(1 for i in notg if not any(rows[i].values())) / max(len(notg), 1)
print("  payload grounded vs not: survival " + format(rg, ".4f") + " vs " + format(rn, ".4f")
      + "   (n = " + str(len(grounded)) + " / " + str(len(notg)) + ")")
print("  a large gap means this structural feature carries information that the")
print("  performance axes do not already encode.")
print()
print("  median IN-BAND |T| by structural bucket (a lower median means better isolation):")
print("  " + "feature".rjust(18) + "bucket".rjust(12) + "count".rjust(8) + "median".rjust(12)
      + "p10".rjust(12) + "p90".rjust(12))
for name in ("payload_grounded", "n_ground"):
    vals = sorted({f[name] for f in feats})
    if len(vals) > 4:
        vals = [vals[0], vals[1], vals[-1]]
    for v in vals:
        idx = [i for i, f in enumerate(feats) if f[name] == v]
        if not idx:
            continue
        arr = np.array([profs[i]["in_band"] for i in idx])
        p10, p50, p90 = np.percentile(arr, [10, 50, 90])
        print("  " + name.rjust(18) + str(v).rjust(12) + str(len(idx)).rjust(8)
              + format(p50, ".4g").rjust(12) + format(p10, ".4g").rjust(12)
              + format(p90, ".4g").rjust(12))

print()
print(line)
print("B. FALSIFICATION TEST - the payload ground tie fixes the high-frequency law")
print(line)
print("""
  Derivation.  With M diagonal, the (0,0) cofactor of (M s^2 + C s + K) has leading
  term prod_{i != 0} m_i * s^(2n-2).  Hence

      P(s) = prod_{i != 0} m_i * (f0 + g0 s) * s^(2n-2) + O(s^(2n-3))
      Q(s) = prod_i m_i * s^(2n) + O(s^(2n-1))

  and therefore, writing f0 / g0 for the payload's OWN ground stiffness and damping,

      T(s)  ->  g0 / (m0 s)  +  f0 / (m0 s^2)      as |s| -> infinity

  independently of every other mass, spring and damper in the network.  If the payload
  has NO ground tie then f0 = g0 = 0 and T falls off at least as s^-3.

  This is a claim about a STRUCTURAL FEATURE - the payload's own tie - and it is
  falsifiable by a single structure in the ensemble that disagrees.
""")
worst_err = 0.0
worst_who = None
for i, s in enumerate(ens):
    f0 = s.ground_k.get(0, 0.0)
    g0 = s.ground_c.get(0, 0.0)
    m0 = s.masses[0]
    hi = OMEGA[-1]
    T = np.abs(s.transmissibility(np.array([hi])))[0]
    asym = float(np.hypot(g0 / (m0 * hi), f0 / (m0 * hi ** 2)))
    if asym > 0:
        rel = abs(T - asym) / asym
        if rel > worst_err:
            worst_err, worst_who = rel, i
print("  at omega = " + format(OMEGA[-1], ".3g") + " rad/s, over " + str(N_STRUCT) + " structures:")
if worst_who is None:
    print("    no structure had a non-zero payload ground tie; test inconclusive here")
else:
    print("    worst relative deviation |T| vs asymptote = " + format(worst_err, ".3e")
          + "  (structure " + str(worst_who) + ")")
    print("    -> the asymptote formula is CONFIRMED on this ensemble"
          if worst_err < 1e-3 else
          "    -> the asymptote formula FAILS; see structure " + str(worst_who))

# does the payload ground tie PREDICT the high-frequency attenuation?
print()
print("  is the payload ground tie a usable STRUCTURAL predicate?")
print("  " + "bucket".rjust(26) + "count".rjust(8) + "median in-band |T|".rjust(21))
for tag, idx in (("payload directly grounded", grounded),
                 ("payload not grounded", notg)):
    v = np.array([profs[i]["in_band"] for i in idx])
    print("  " + tag.rjust(26) + str(len(idx)).rjust(8)
          + format(float(np.median(v)), ".4g").rjust(21))

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "structural_features.json").write_text(json.dumps({
    "calibration": {k: v for k, v in CAL.items()}, "base_survival": base_surv,
    "feature_rows": feat_rows,
    "grounded_survival": rg, "ungrounded_survival": rn,
    "asymptote_worst_rel_err": worst_err,
}, indent=1, default=str), encoding="utf-8")
print()
print("wrote runs/structural_features.json")
