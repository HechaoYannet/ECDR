"""Step 20 - the library composition argument, and the sparse-space census."""
import _bootstrap  # noqa: F401
import json
import pathlib
from math import comb

from ecdr.structure.library import certificates_needed, separation

line = "=" * 88
print(line)
print("A. COMPOSITION: how many constant-coverage certificates exhaust a space?")
print(line)
print("  k = log(N) / log(1/(1-f)); library cost k*c_p against N*c_s for sampling")
print()
print("  " + "coverage f".rjust(11) + "N=1e3".rjust(10) + "1e6".rjust(9) + "1e9".rjust(9)
      + "1e12".rjust(9) + "1e18".rjust(9) + "   <- certificates needed")
for f in (0.5, 0.1, 0.01, 0.001):
    row = [format(certificates_needed(int(10 ** e), f), ".1f") for e in (3, 6, 9, 12, 18)]
    print("  " + format(f, ".3f").rjust(11) + "".join(r.rjust(10) for r in row))
print()
print("  Note the logarithm: at fixed f the count grows ADDITIVELY per decade of N,")
print("  while exhaustive sampling grows MULTIPLICATIVELY.  That is the separation.")

N = 64383610994
print()
print(line)
print("B. SEPARATION against exhaustive sampling, N = 6.44e10 (census n_max = 8)")
print(line)
print("  " + "coverage f".rjust(11) + "certificates".rjust(14) + "library cost".rjust(16)
      + "sampling cost".rjust(18) + "separation".rjust(14))
for f in (0.635, 0.5, 0.1, 0.01, 0.001):
    s = separation(N, f)
    print("  " + format(f, ".3f").rjust(11) + format(s["certificates_needed"], ",.1f").rjust(14)
          + format(s["library_cost_in_c_s"], ",.0f").rjust(16)
          + format(s["sampling_cost_in_c_s"], ",.0f").rjust(18)
          + format(s["separation"], ".3e").rjust(14))

print()
print(line)
print("C. SPARSE SPACE: trees instead of all connected graphs")
print(line)
print("  The dense space is dominated by near-complete graphs, which no mechanical")
print("  structure resembles.  Recomputed on trees (Cayley n^(n-2) x ground subsets):")


def tree_structures(n):
    if n <= 2:
        return 1
    return n ** (n - 2)


def tree_space(n_max):
    return sum(tree_structures(n) * (2 ** n - 1) for n in range(1, n_max + 1))


def tree_balanced_ground(n_max):
    tot = 0
    for n in range(1, n_max + 1):
        c = tree_structures(n)
        tot += c * sum(comb(n, j) for j in range(1, n // 2 + 1))
    return tot


print("  " + "n_max".rjust(6) + "N (trees)".rjust(22) + "g_balanced".rjust(22)
      + "fraction".rjust(11))
rows = []
for n in range(3, 11):
    Nn = tree_space(n)
    g = tree_balanced_ground(n)
    rows.append({"n_max": n, "N": Nn, "g": g, "fraction": g / Nn})
    print("  " + str(n).rjust(6) + format(Nn, ",").rjust(22) + format(g, ",").rjust(22)
          + format(g / Nn, ".4f").rjust(11))
print()
print("  The balanced-threshold fraction is stable across BOTH spaces, while the")
print("  resource-bound fraction was not.  Robustness is a property of the PREDICATE")
print("  SHAPE, not of the space.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "library.json").write_text(json.dumps({
    "separation_N": N,
    "examples": [separation(N, f) for f in (0.5, 0.1, 0.01, 0.001)],
    "tree_space": rows,
}, indent=1, default=str), encoding="utf-8")
print()
print("wrote runs/library.json")
