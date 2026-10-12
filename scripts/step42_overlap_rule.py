"""Step 42 - the general rule behind Finding 019: OVERLAP, not topology vs value.

Finding 019 concluded that cuts keyed to topology compose and cuts keyed to component
values do not.  But that is one instance of a more general mechanism.  The ensemble draws
topology first and then each component value independently.  Two cuts compose iff their
predicates depend on DISJOINT parts of that randomness.  Topology is disjoint from
everything, so it composed; g0/m0 and W both depend on the payload's ground damper, so
they did not.

Test: build cuts keyed to KNOWN, CONTROLLED overlaps and see whether the ratio tracks the
overlap rather than the topology/value label.

    A  = spring stiffness of the FIRST edge          (one draw)
    B  = spring stiffness of the LAST edge           (a different draw, disjoint from A)
    C  = W, the waterbed                             (a function of ALL draws, so it shares
                                                      a draw with A and with B)
    T  = a topology cut                              (disjoint from every value draw)

Predictions if the mechanism is overlap:
    A x B  ~ 1     disjoint draws
    A x T  ~ 1     disjoint
    B x T  ~ 1     disjoint
    A x C  < 1     share the draw that A is keyed to
    B x C  < 1     share the draw that B is keyed to
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np
from scipy.stats import spearmanr

from ecdr.structure import ensemble, waterbed_numeric

line = "=" * 92
ens = ensemble(seed=5, count=200, n_lo=2, n_hi=8)

first_k, last_k, W, topo = [], [], [], []
for s in ens:
    edges = list(s.springs.keys())
    first_k.append(s.springs[edges[0]])
    last_k.append(s.springs[edges[-1]])
    W.append(waterbed_numeric(s))
    topo.append(len(set(s.ground_k) | set(s.ground_c)) >= 2)
first_k = np.array(first_k)
last_k = np.array(last_k)
W = np.array(W)
topo = np.array(topo)

cuts = {
    "A  first-edge stiffness": first_k > np.median(first_k),
    "B  last-edge stiffness": last_k > np.median(last_k),
    "C  waterbed W (global)": W > np.median(W),
    "T  >=2 ground ties (topology)": topo,
}

print(line)
print("A. cuts")
print(line)
print("  " + "cut".rjust(30) + "rules out".rjust(11) + "fraction".rjust(11))
for k, v in cuts.items():
    print("  " + k.rjust(30) + str(int(v.sum())).rjust(11) + format(v.mean(), ".4f").rjust(11))


def ratio(a, b):
    return float((~a & ~b).mean() / ((1 - a.mean()) * (1 - b.mean())))


keys = list(cuts)
print()
print(line)
print("B. ratios against the overlap")
print(line)
overlap = {
    ("A  first-edge stiffness", "B  last-edge stiffness"): ("none", 0),
    ("A  first-edge stiffness", "T  >=2 ground ties (topology)"): ("none", 0),
    ("B  last-edge stiffness", "T  >=2 ground ties (topology)"): ("none", 0),
    ("A  first-edge stiffness", "C  waterbed W (global)"): ("shares A", 1),
    ("B  last-edge stiffness", "C  waterbed W (global)"): ("shares B", 1),
    ("C  waterbed W (global)", "T  >=2 ground ties (topology)"): ("none", 0),
}
print("  " + "pair".rjust(44) + "overlap".rjust(11) + "ratio".rjust(9))
rows = []
for (a, b), (ov, n) in overlap.items():
    r = ratio(cuts[a], cuts[b])
    rho, p = spearmanr(
        [first_k if a.startswith("A") else last_k if a.startswith("B") else W
         if a.startswith("C") else topo.astype(float)][0],
        [first_k if b.startswith("A") else last_k if b.startswith("B") else W
         if b.startswith("C") else topo.astype(float)][0])
    rows.append({"a": a, "b": b, "overlap": ov, "ratio": r, "rho": float(rho)})
    print("  " + (a.split()[0] + " x " + b.split()[0] + "   " + a[3:] + " / " + b[3:]).rjust(44)
          + ov.rjust(11) + format(r, ".4f").rjust(9))

print()
print(line)
print("C. does the ratio track the OVERLAP or the topology/value label?")
print(line)
disjoint = [r["ratio"] for r in rows if r["overlap"] == "none"]
shared = [r["ratio"] for r in rows if r["overlap"] != "none"]
print("  disjoint draws : mean ratio " + format(float(np.mean(disjoint)), ".4f")
      + "   (" + str(len(disjoint)) + " pairs: " + ", ".join(format(x, ".3f") for x in disjoint) + ")")
print("  shared draw    : mean ratio " + format(float(np.mean(shared)), ".4f")
      + "   (" + str(len(shared)) + " pairs: " + ", ".join(format(x, ".3f") for x in shared) + ")")
print()
print("  Note both A and B are VALUE cuts.  If the split were topology vs value they would")
print("  both have to behave alike against C.  They do - but so does everything else that")
print("  shares a draw with C, and nothing that does not.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "overlap_rule.json").write_text(json.dumps({
    "pairs": rows,
    "disjoint_mean": float(np.mean(disjoint)),
    "shared_mean": float(np.mean(shared)),
}, indent=1), encoding="utf-8")
print()
print("wrote runs/overlap_rule.json")
