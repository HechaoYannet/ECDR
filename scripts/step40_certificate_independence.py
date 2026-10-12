"""Step 40 - do the two candidate certificates live on independent axes?

Finding 014 produced a structural law keyed to the payload's OWN ground tie.
Finding 018 produced a band-tradeoff law keyed to the right-half-plane zeros of P.
Finding 015 says a library composes only if successive cuts stay independent, and that a
pair with ratio near 0.4 is one certificate wearing two hats.

This measures the pair.  W is taken from the NUMERICAL integral, which is reliable for
every network, so the root-finding limitation of Finding 018 does not enter here.

Both quantities are structural, so what is being asked is whether the two STRUCTURAL
FEATURES carry distinct information - not whether two performance metrics do, which
Finding 013 already answered in the negative.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np
from scipy.stats import spearmanr

from ecdr.structure import ensemble, waterbed_numeric
from ecdr.structure.capability import profile

line = "=" * 90
OMEGA = np.logspace(np.log10(0.5), np.log10(3.0e5), 900)
OMEGA_LOW = 2 * np.pi * 30.0

ens = ensemble(seed=5, count=200, n_lo=2, n_hi=8)
profs = [profile(s, OMEGA, OMEGA_LOW) for s in ens]

g_over_m = np.array([s.ground_c.get(0, 0.0) / s.masses[0] for s in ens])
W = np.array([waterbed_numeric(s) for s in ens])
sag = np.array([p["sag"] for p in profs])
inband = np.array([p["in_band"] for p in profs])
peak = np.array([p["peak"] for p in profs])
nrhp = np.array([len([1 for _ in range(0)]) for _ in ens])  # placeholder

print(line)
print("A. the two structural quantities")
print(line)
print("  " + "quantity".rjust(26) + "p10".rjust(13) + "median".rjust(13) + "p90".rjust(13))
for tag, v in (("payload ground damping / mass", g_over_m),
               ("waterbed W (numeric)", W),
               ("sag (mm)", sag * 1e3),
               ("in-band |T|", inband)):
    p10, p50, p90 = np.percentile(v, [10, 50, 90])
    print("  " + tag.rjust(26) + format(p10, ".4g").rjust(13) + format(p50, ".4g").rjust(13)
          + format(p90, ".4g").rjust(13))

print()
print(line)
print("B. rank correlation between the axes")
print(line)
pairs = [("g0/m0", g_over_m, "W", W), ("g0/m0", g_over_m, "sag", sag),
         ("g0/m0", g_over_m, "in-band", inband), ("W", W, "sag", sag),
         ("W", W, "in-band", inband), ("sag", sag, "in-band", inband),
         ("sag", sag, "peak", peak)]
print("  " + "pair".rjust(24) + "spearman rho".rjust(15) + "p value".rjust(12))
corr = {}
for na, a, nb, b in pairs:
    rho, p = spearmanr(a, b)
    corr[na + " vs " + nb] = {"rho": float(rho), "p": float(p)}
    print("  " + (na + "  vs  " + nb).rjust(24) + format(float(rho), ".4f").rjust(15)
          + format(float(p), ".2e").rjust(12))
print()
print("  A rho near 0 means the two structural features carry different information.")

print()
print(line)
print("C. independence ratio on median splits")
print(line)
cuts = {
    "g0/m0": g_over_m > np.median(g_over_m),
    "W": W > np.median(W),
    "sag": sag > np.median(sag),
    "in-band": inband > np.median(inband),
}
print("  " + "cut".rjust(18) + "rules out".rjust(11) + "fraction".rjust(11))
for k, v in cuts.items():
    print("  " + k.rjust(18) + str(int(v.sum())).rjust(11) + format(v.mean(), ".4f").rjust(11))


def ratio(a, b):
    both = (~a & ~b).mean()
    return both / ((1 - a.mean()) * (1 - b.mean()))


print()
print("  " + "pair".rjust(24) + "independence ratio".rjust(20) + "  reading".rjust(14))
rows = []
keys = list(cuts)
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        a, b = keys[i], keys[j]
        r = ratio(cuts[a], cuts[b])
        if r > 1.15:
            read = "complementary"
        elif r < 0.85:
            read = "redundant"
        else:
            read = "near independent"
        rows.append({"a": a, "b": b, "ratio": float(r), "reading": read})
        print("  " + (a + "  x  " + b).rjust(24) + format(r, ".4f").rjust(20)
              + "  " + read.rjust(14))

print()
print(line)
print("D. THE PAIR THAT MATTERS")
print(line)
key = "g0/m0  x  W"
hit = [r for r in rows if r["a"] == "g0/m0" and r["b"] == "W"]
rho = corr.get("g0/m0 vs W", {})
if hit:
    r = hit[0]["ratio"]
    print("  payload-tie law  vs  waterbed law")
    print("    independence ratio : " + format(r, ".4f"))
    print("    spearman rho       : " + format(rho.get("rho", float("nan")), ".4f")
          + "   (p = " + format(rho.get("p", float("nan")), ".2e") + ")")
    print()
    if r > 1.15:
        print("    -> COMPLEMENTARY.  A network ruled out by the payload-tie law is less")
        print("       likely to be ruled out by the waterbed law.  These are two")
        print("       certificates, not one wearing two hats.")
    elif r < 0.85:
        print("    -> REDUNDANT.  The two laws overlap more than chance; the second adds")
        print("       little and the library does not compose them usefully.")
    else:
        print("    -> NEAR INDEPENDENT.  Usable as two cuts, though not complementary.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "certificate_independence.json").write_text(json.dumps({
    "correlations": corr,
    "cut_sizes": {k: int(v.sum()) for k, v in cuts.items()},
    "ratios": rows,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/certificate_independence.json")
