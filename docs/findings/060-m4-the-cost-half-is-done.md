# Finding 060 - M4: the cost half is done, the soundness half failed twice

Status: **half of M4 is established and half is not.** The crossing survives the cost ladder and
moves earlier, measured against a real OpenModelica evaluation: separation 9.296e+14 at L0,
3.446e+15 at L1, **3.431e+16 at L2**, with c_s(L2)/c_s(L0) = 1247.

**The soundness half - does the certificate's claim survive at L2 - was attempted twice and both
attempts were invalid.** The second one shows why, and the reason is structural: the L2 models this
project builds are **base-excited**, and C1 is a statement about the **free** response.
Reproduce: scripts/step82_m4_ladder.py.  Data: runs/m4_ladder.json

## 1. The cost half, which is clean

| quantity | value |
|---|---|
| c_s(L0), one transmissibility evaluation | 1.5090e-03 s |
| c_s(L1), one robust evaluation, 2^2 corners | 6.0360e-03 s |
| **c_s(L2), emit + OpenModelica linearize + evaluate** | **1.8816e+00 s** |
| **the ladder multiplies an evaluation by** | **1247** |

and the separation between the certificate route and evaluation, at n = 10:

| fidelity | (a) evaluation only | (b) hybrid | separation |
|---|---|---|---|
| L0 | 5.330e+13 | 5.734e-02 | 9.296e+14 |
| L1 | 2.132e+14 | ~2.3e-01 | 3.446e+15 |
| **L2** | **6.647e+16** | **1.937e+00** | **3.431e+16** |

**The crossing survives and moves earlier.** This is not surprising and it is worth stating why: the
certificate's cost is c_p + c_v and **contains no c_s**, so raising the price of an evaluation can
only help it. Section 8's cost ladder predicted this and it is now measured with an OpenModelica
evaluation on the expensive end rather than an assumed one.

**And the L2 models agree with L0 to at worst 4.62e-07** across the eight structures, which is the
emitter's accuracy again, not new information.

## 2. The soundness half, attempt one: wrong observable

The first version compared C1 against the **forced-response magnitude** |T(omega)| of the
base-excited L2 model, counting a harmonic as producible when |T| > 1e-9.

**That is meaningless.** C1 says an n-mode structure's **free** response has at most n harmonics. A
base-excited transfer of order 1 at a given frequency says nothing about how many harmonics the
structure can produce - and for a base-driven system |T| ~ 1 at every frequency, so the count was
always 3 and the test could not fail for any reason connected to C1. **It printed "agreement 7 of
8".**

## 3. Attempt two: right observable, wrong model

The poles of the model OpenModelica built. An LTI structure with p oscillatory pole pairs can
produce at most p harmonics, so C1 is confirmed at L2 iff the dumped A matrix has at most n pairs.

| idx | n | L2 poles | oscillatory pairs |
|---|---|---|---|
| 0 | 4 | 10 | **5** |
| 1 | 5 | 12 | **6** |
| 3 | 8 | 18 | **9** |
| 5 | 3 | 8 | **4** |
| 7 | 2 | 6 | **3** |

**osc_pairs = n + 1 and l2_poles = 2n + 2, in all eight.** So C1 as literally stated - "at most n"
- **fails the check on every case**, and the agreement count is 0 of 8.

**The reason is structural, not a defect in the certificate.** The emitted model is driven by a
`Translational.Sources.Position`, which contributes a state. **The extra oscillatory pair is the
excitation, not a structural mode.** The structural part contributes exactly n pairs, consistently,
which is **consistent with C1** - but consistency read off a pattern is not a measurement, and
reporting it as confirmation would be the same error as attempt one in slower motion.

## 4. What M4 therefore is

| half | status |
|---|---|
| the crossing reproduced at L1 and L2, with real costs | **DONE** - separation 9.296e+14 -> 3.431e+16 |
| Modelica can express S | **DONE** - 8 structures, n = 2..8, worst relative error 4.62e-07 |
| the certificate's claim re-checked at L2 | **NOT DONE** |
| the revocation path of section 6 Layer C exercised | **NOT DONE** - nothing was revoked because nothing was checked |

**M4's own falsifier - "it moves out of reach, or Modelica cannot express S" - is not triggered.**
But the milestone as written is "the crossing reproduced at L1 and L2", and the second half of what
that should mean is missing: **a crossing measured against a fidelity whose verdicts have not been
checked is a crossing on an unverified premise.**

**What would close it**: an L2 model with **no input and nonzero initial conditions** - a free
response - simulated and its harmonic content counted. The emitter already writes declarations and
connections only; it has no free-response variant, and that is the missing piece. **Until then M4 is
recorded as half done.**

## 5. The pattern, now six instances

Attempt one was the fifth verdict in this project not computed from meaningful data; attempt two was
the sixth. The list now reads:

| # | the verdict | why it was wrong |
|---|---|---|
| 1 | the anomaly in the ramp response | compared against a synthetic baseline |
| 2 | "the scale factor is two" | held the pre-factor fixed |
| 3 | "the crossing exponent is 1" | the crossing was never reached |
| 4 | "the named remedy is not what was missing" | decided from a four-unit count, contradicted by its own table |
| 5 | "agreement 7 of 8" | forced response used to test a free-response claim |
| 6 | "osc_pairs <= n, 0 of 8" | the excitation's pole counted as a structural mode |

**All six are the same error in different clothing: computing a number that cannot fail for the
reason the test exists.** In five of the six the number was arithmetically correct. **The defence
that has actually worked is not more computation but asking what the number would look like if the
claim were false** - and in this round that question was not asked until the second attempt had
already run.

## 6. Limits

  * **One ensemble, one target, eight L2 structures.** c_s(L2) = 1.8816 s is the mean of eight
    emit-plus-linearize cycles on one machine; the Docker and OpenModelica overhead dominates and
    would move with caching.
  * **The L1 cost is not measured, it is derived**: c_s(L1) = 4 * c_s(L0) for a two-parameter
    robustness box. That is the corner count, not a timing of the robustness machinery.
  * **The hybrid's denominator uses the same f = 0.65 as L0.** Coverage is a property of the
    (invariant, ensemble, requirement) triple (Finding 012), and it was not re-measured at L1 or L2.
  * **c_s(L2) is not the cost of checking a certificate at L2.** It is the cost of an independent
    evaluation. The certificate itself still costs c_p + c_v, which is why the separation improves.
