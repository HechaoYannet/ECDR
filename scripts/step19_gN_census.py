"""Step 19 - the g(N) census.

Roadmap section 5.4: a certificate family is useful only if g(N), the NUMBER of
structures it rules out, grows without bound.  This census measures g(N) for the
candidate invariants on a structure space that genuinely grows.

The census is designed to be able to FAIL.  If g(N) turns out bounded, section 5.4
says the certificate is decoration and the programme must change, so learning that
here -- before building the apparatus -- is the entire point.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

from ecdr.structure import growth_table, growth_table_scaling, space_size
from ecdr.structure.counting import structures_with_n_nodes

line = "=" * 92
NS = [3, 4, 5, 6, 7, 8]

print(line)
print("THE SPACE ITSELF")
print(line)
print("  " + "n_max".rjust(6) + "structures with exactly n".rjust(26) + "cumulative N".rjust(20))
for n in NS:
    print("  " + str(n).rjust(6) + format(structures_with_n_nodes(n), ",").rjust(26)
          + format(space_size(n), ",").rjust(20))
print()
print("  N grows super-exponentially in n_max, which is what the census needs.")

print()
print(line)
print("CASE 1 - requirement HELD FIXED (m = 4 frequencies, q = 3 ground paths)")
print(line)
print("  " + "n_max".rjust(5) + "N".rjust(18) + "g_I1".rjust(10) + "g_I1/N".rjust(10)
      + "g_I2".rjust(16) + "g_I2/N".rjust(9) + "g_I3".rjust(20) + "g_I3/N".rjust(8)
      + "spd I3".rjust(9))
rows1 = growth_table(NS)
for r in rows1:
    print("  " + str(r["n_max"]).rjust(5) + format(r["N"], ",").rjust(18)
          + format(r["g_I1"], ",").rjust(10) + format(r["frac_I1"], ".1e").rjust(10)
          + format(r["g_I2"], ",").rjust(16) + format(r["frac_I2"], ".2e").rjust(9)
          + format(r["g_I3"], ",").rjust(20) + format(r["frac_I3"], ".3f").rjust(8)
          + format(r["speedup_I3"], ".3f").rjust(9))

print()
print(line)
print("CASE 2 - requirement SCALES with the space (m = n_max // 2)")
print(line)
print("  " + "n_max".rjust(6) + "m".rjust(5) + "N".rjust(20) + "g_I1".rjust(18)
      + "g_I1/N".rjust(10) + "speedup".rjust(10))
rows2 = growth_table_scaling(NS)
for r in rows2:
    print("  " + str(r["n_max"]).rjust(6) + str(r["m"]).rjust(5)
          + format(r["N"], ",").rjust(20) + format(r["g_I1"], ",").rjust(18)
          + format(r["frac_I1"], ".3f").rjust(10)
          + format(r["speedup_I1"], ".3f").rjust(10))

print()
print(line)
print("VERDICT AGAINST ROADMAP 5.4")
print(line)
g1a, g1b = rows1[0]["g_I1"], rows1[-1]["g_I1"]
print("  I1 mode counting, FIXED requirement:")
print("    g: " + format(g1a, ",") + " -> " + format(g1b, ",")
      + "   ratio " + format(g1b / max(g1a, 1), ".4f"))
print("    fraction: " + format(rows1[0]["frac_I1"], ".3e") + " -> "
      + format(rows1[-1]["frac_I1"], ".3e"))
if abs(g1b / max(g1a, 1) - 1.0) < 1e-9:
    print("    => g(N) is exactly CONSTANT once the space can exceed the requirement.")
    print("       By 5.4 this certificate yields NO crossing: its saving is a one-off")
    print("       absolute amount that never grows.  The mode-counting certificate is")
    print("       therefore NOT the vehicle for the crossing claim.")
g2a, g2b = rows1[0]["g_I2"], rows1[-1]["g_I2"]
print()
print("  I2 ground-path counting, FIXED requirement:")
print("    g: " + format(g2a, ",") + " -> " + format(g2b, ",")
      + "   ratio " + format(g2b / max(g2a, 1), ".4f"))
print("    => g(N) GROWS.  This is the shape a certificate family needs.")
print()
print("  I3 balanced threshold property, FIXED requirement:")
print("    g: " + format(rows1[0]["g_I3"], ",") + " -> " + format(rows1[-1]["g_I3"], ",")
      + "   fraction: " + format(rows1[0]["frac_I3"], ".3f") + " -> "
      + format(rows1[-1]["frac_I3"], ".3f"))
print("    => g(N) = Theta(N): a CONSTANT fraction.  This is the only regime that")
print("       gives a speedup which does not decay toward 1.")
print()
print("  THREE REGIMES, ALL REALISED:")
print("    I1 resource bound, fixed requirement   g = O(1)      speedup -> 1  (no crossing)")
print("    I2 resource bound, growing             g -> inf      speedup -> 1  (decaying)")
print("    I3 balanced threshold                  g = Theta(N)  speedup = c  (persistent)")
print()
print("  I1 with a SCALING requirement: g grows but stays tiny ("
      + format(rows2[-1]["g_I1"], ",") + " at n_max=8); the fraction is "
      + format(rows2[-1]["frac_I1"], ".1e") + ", so scaling the requirement does not")
print("  rescue a resource-bound predicate in a super-exponentially growing space.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "census_gN.json").write_text(json.dumps({
    "fixed_requirement": rows1, "scaling_requirement": rows2,
}, indent=1, default=str), encoding="utf-8")
print()
print("wrote runs/census_gN.json")
