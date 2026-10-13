"""Step 82 - M4: the crossing at L1 and L2, with the real cost of each fidelity.

Roadmap section 9, milestone M4:

    the crossing reproduced at L1 and L2 with OpenModelica
    falsified if: it moves out of reach, or Modelica cannot express S

Section 8 fixes the cost ladder (lines 486): "L0 -> L1 -> L2 is the cost ladder; L2 is where
independent checking happens".  The L0 curve (Findings 050 to 053, 058) measured three arms on one
cost axis in seconds.  This recomputes them with the cost of an evaluation at each fidelity:

    c_s(L0)   one frequency-domain transmissibility evaluation
    c_s(L1)   one ROBUST evaluation - the corner machinery, 2**d evaluations
    c_s(L2)   emit + OpenModelica linearize + evaluate   (measured here)

The certificate's cost does NOT scale with c_s: it is c_p + c_v, independent of the evaluation.
So the theory predicts the crossing does not merely survive, it moves EARLIER as the ladder is
climbed.  That is falsifiable and this measures it.

**The other half of M4 matters more**: section 6 Layer C says a certificate crossed by a higher
fidelity is REVOKED, not edited.  So the claim must be re-checked against the model OpenModelica
actually runs - a certificate that holds at L0 and fails at L2 is a revocation, and reporting the
cost curve without checking this would be reporting a crossing on a false premise.
"""
import _bootstrap  # noqa: F401
import json
import pathlib
import time

import numpy as np

from ecdr.l0.feasibility import SEARCH_OMEGA
from ecdr.l2.modelica.emit import emit_model
from ecdr.l2.modelica.linearize import linearize
from ecdr.structure import ensemble
from ecdr.structure.counting import space_size

line = "=" * 104
TARGET_OMEGAS = np.array([2.0, 5.0, 9.0])          # a three-harmonic target
M_HARM = len(TARGET_OMEGAS)
OUT = pathlib.Path(__file__).resolve().parents[1] / "runs"

ENS = ensemble(seed=101, count=400, n_lo=2, n_hi=8)


# ---------------------------------------------------------------- c_s at each fidelity
def timeit(fn, reps):
    t0 = time.perf_counter()
    for _ in range(reps):
        fn()
    return (time.perf_counter() - t0) / reps


print(line)
print("THE COST OF ONE EVALUATION AT EACH FIDELITY")
print(line)
s0 = ENS[0]
c_s0 = timeit(lambda: s0.transmissibility(SEARCH_OMEGA), 200)
print("  c_s(L0)  one transmissibility evaluation      : " + format(c_s0, ".6e") + " s")

# L1: the robustness machinery evaluates the corners of a parameter box.
D_PARAMS = 2
c_s1 = c_s0 * (2 ** D_PARAMS)
print("  c_s(L1)  one robust evaluation, 2**" + str(D_PARAMS) + " corners    : "
      + format(c_s1, ".6e") + " s   (measured c_s(L0) times the corner count)")

# L2: emit to Modelica, linearize through OpenModelica, evaluate.
print()
print("  c_s(L2)  measuring on real structures - this drives OpenModelica in Docker")
l2_costs, l2_rows = [], []
for idx in range(8):
    s = ENS[idx]
    name = "M4_" + str(idx)
    t0 = time.perf_counter()
    model = emit_model(s, 1.0, name=name)
    M = linearize(model, name=name)
    dt = time.perf_counter() - t0
    if not M["ok"]:
        print("    structure " + str(idx) + " FAILED: " + M["log"][-200:])
        continue
    A, B, C, D = M["A"], M["B"], M["C"], M["D"]
    mags = []
    for w in TARGET_OMEGAS:
        r = C @ np.linalg.solve(1j * w * np.eye(A.shape[0]) - A, B) + D
        mags.append(float(abs(r[0, 0])))
    ref = np.abs(s.transmissibility(TARGET_OMEGAS))
    rel = float(np.max(np.abs(np.array(mags) - ref) / np.maximum(ref, 1e-300)))
    # THE MODEL OPENMODELICA ACTUALLY BUILT: its own poles, read off the A matrix it dumped.
    # This, not the forced-response magnitude, is what C1 is about.
    ev = np.linalg.eigvals(A)
    pairs = int(np.sum(ev.imag > 1e-9 * max(1.0, float(np.max(np.abs(ev))))))
    l2_costs.append(dt)
    l2_rows.append({"idx": idx, "n": s.n, "seconds": dt, "mags": mags,
                    "rel_to_L0": rel, "l2_poles": int(A.shape[0]),
                    "l2_oscillatory_pairs": pairs})
    print("    structure " + str(idx) + "  n=" + str(s.n).rjust(2)
          + "  " + format(dt, ".4f") + " s   max rel to L0 " + format(rel, ".2e"))

c_s2 = float(np.mean(l2_costs))
print()
print("  c_s(L2)  mean over " + str(len(l2_costs)) + " structures           : "
      + format(c_s2, ".6e") + " s")
print("  c_s(L2) / c_s(L0) = " + format(c_s2 / c_s0, ".1f"))

# ------------------------------------------------------------------ certificate soundness
print()
print(line)
print("SOUNDNESS AT L2: does the certificate's verdict survive the higher fidelity?")
print(line)
print("  C1's claim: an n-degree-of-freedom LTI structure produces at most n harmonics,")
print("  so a target with " + str(M_HARM) + " harmonics is impossible when n < " + str(M_HARM) + ".")
print()
print("  ** THE FIRST VERSION OF THIS SECTION WAS INVALID AND IS REPLACED. ** It compared C1")
print("  against the FORCED-response magnitude |T(omega)| of a base-excited model. C1 is a")
print("  statement about the FREE response - an n-mode structure has at most n harmonics - and a")
print("  base-excited transfer of order 1 at a frequency says nothing whatever about how many")
print("  harmonics the structure can produce. It printed '7 of 8 agreement' from a test that")
print("  could not fail for any reason connected to C1. That is the fifth verdict in this")
print("  project not computed from meaningful data, and it is replaced below.")
print()
print("  What is actually checkable at L2: the POLES of the model OpenModelica built. An LTI")
print("  structure with p oscillatory pole pairs can produce at most p harmonics, so C1 - which")
print("  asserts 'at most n' - is confirmed at L2 iff the dumped A matrix has at most n pairs.")
print()
print("  " + "idx".rjust(4) + "n".rjust(3) + "C1 says".rjust(10) + "L2 poles".rjust(10)
      + "L2 osc pairs".rjust(13) + "C1 holds at L2?".rjust(18) + "  max rel to L0".rjust(15))
agree, checked = 0, 0
for row in l2_rows:
    ruled_out = row["n"] < M_HARM
    holds = row["l2_oscillatory_pairs"] <= row["n"]
    ok = holds and ((row["l2_oscillatory_pairs"] < M_HARM) == ruled_out)
    agree += int(ok)
    checked += 1
    print("  " + str(row["idx"]).rjust(4) + str(row["n"]).rjust(3)
          + ("at most " + str(row["n"])).rjust(10)
          + str(row["l2_poles"]).rjust(10) + str(row["l2_oscillatory_pairs"]).rjust(13)
          + ("YES" if holds else "NO").rjust(18)
          + format(row["rel_to_L0"], ".2e").rjust(15))
print()
print("  C1 holds at L2 on " + str(agree) + " of " + str(checked) + " structures, judged from the")
print("  poles of the model OpenModelica built rather than from this project's equations.")
print("  And the forced responses agree with L0 to at worst "
      + format(max(r["rel_to_L0"] for r in l2_rows), ".2e") + ".")

# ------------------------------------------------------------------ the arms at each fidelity
print()
print(line)
print("THE THREE ARMS AT EACH FIDELITY - the L0 curve recomputed on the ladder")
print(line)
C_CERT = c_s0                       # the certificate's cost, charged one full L0 evaluation
F = 0.65
SURV = 1.0 - F
rows = []
print("  " + "n".rjust(3) + "N(n)".rjust(24) + "k".rjust(5)
      + "(a) L0".rjust(14) + "(a) L1".rjust(14) + "(a) L2".rjust(14)
      + "(b) hybrid L0".rjust(16) + "(b) hybrid L2".rjust(16) + "(a)L2/(b)L2".rjust(13))
for n in range(3, 11):
    N = space_size(n)
    k = max(1, int(np.ceil(np.log(N) / np.log(1.0 / SURV))))
    rem = max(1.0, N * SURV ** k)
    arm_a0, arm_a1, arm_a2 = N * c_s0, N * c_s1, N * c_s2
    arm_b0 = k * C_CERT + rem * c_s0
    arm_b2 = k * C_CERT + rem * c_s2
    rows.append({"n": n, "N": int(N), "k": k, "a_L0": arm_a0, "a_L1": arm_a1,
                 "a_L2": arm_a2, "b_L0": arm_b0, "b_L2": arm_b2,
                 "sep_L0": arm_a0 / arm_b0, "sep_L1": arm_a1 / (k * C_CERT + rem * c_s1),
                 "sep_L2": arm_a2 / arm_b2})
    print("  " + str(n).rjust(3) + format(N, ".4e").rjust(24) + str(k).rjust(5)
          + format(arm_a0, ".3e").rjust(14) + format(arm_a1, ".3e").rjust(14)
          + format(arm_a2, ".3e").rjust(14) + format(arm_b0, ".3e").rjust(16)
          + format(arm_b2, ".3e").rjust(16) + format(arm_a2 / arm_b2, ".3e").rjust(13))

print()
print(line)
print("VERDICT")
print(line)
f, l = rows[0], rows[-1]
print("  c_s(L0) = " + format(c_s0, ".4e") + " s   c_s(L1) = " + format(c_s1, ".4e")
      + " s   c_s(L2) = " + format(c_s2, ".4e") + " s")
print("  the ladder multiplies an evaluation by " + format(c_s2 / c_s0, ".0f")
      + " from L0 to L2")
print()
print("  separation (a)/(b), certificate over evaluation, at n = " + str(l["n"]) + ":")
print("    L0 : " + format(l["sep_L0"], ".3e"))
print("    L1 : " + format(l["sep_L1"], ".3e"))
print("    L2 : " + format(l["sep_L2"], ".3e"))
print()
if l["sep_L2"] > l["sep_L0"]:
    print("  ** The crossing SURVIVES the ladder and moves EARLIER. ** The certificate's cost")
    print("  is c_p + c_v and does not contain c_s, so raising the price of an evaluation can")
    print("  only help it. This is what section 8's cost ladder predicts and it is now measured")
    print("  with a real OpenModelica evaluation on the expensive end.")
    print()
    print("  ** What this does NOT establish, and must be said plainly: the certificate's claim")
    print("  is not re-derived at L2. ** C1's rule-out depends on n, an integer every fidelity")
    print("  agrees on, so it cannot be crossed - but a certificate whose claim depends on the")
    print("  EQUATIONS would need its argument re-read against the model OpenModelica runs. That")
    print("  revocation path exists (section 6 Layer C) and this experiment does not exercise it.")
else:
    print("  ** The crossing MOVED OUT OF REACH, which is M4's falsifier. **")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "m4_ladder.json").write_text(json.dumps({
    "c_s_L0": c_s0, "c_s_L1": c_s1, "c_s_L2": c_s2, "d_params": D_PARAMS,
    "l2_rows": l2_rows, "agreement": [agree, checked], "rows": rows,
}, indent=1), encoding="utf-8")
print()
print("wrote runs/m4_ladder.json")
