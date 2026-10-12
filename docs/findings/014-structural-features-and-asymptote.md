# Finding 014 - Structural features carry information; a derived law partly survives

Status: the ground-coupling structural feature family shows large, monotone effects on
capability. A derived high-frequency law is **confirmed at leading order and refuted at
the next order**. Two failures in my own tests were caught.
Code: ecdr/structure/ensemble.py.
Reproduce: scripts/step25_structural_features.py, scripts/step26_asymptote_rate.py

## 1. A defect that made a test silently vacuous

Finding 013 prescribed looking for certificates keyed to different STRUCTURAL features.
The first run of that test included "number of ground ties" as an axis - and reported
`n_ground = 1, count 600`, i.e. **zero variance**. The ensemble generator always
tied exactly one node to ground, so the axis could not be tested. The test was not wrong,
it was **vacuous**, and it printed a clean-looking table.

Fixed: `random_structure` now draws the number of ground ties uniformly on
1..ceil(n/2).

## 2. Structural features do carry information

With variance restored (600 structures, calibration sag <= 8 mm, peak <= 8,
in-band <= 0.30, base survival 0.085):

| structural feature | bucket | count | survival rate |
|---|---|---|---|
| payload directly grounded | no | 350 | 0.0943 |
| | yes | 250 | 0.0720 |
| number of ground ties | 1 | 277 | 0.0469 |
| | 2 | 187 | 0.1123 |
| | 3 | 107 | 0.1308 |
| | 4 | 29 | 0.1034 |

and the sharper measure, median in-band abs T (lower means better isolation):

| structural feature | bucket | count | median | p10 | p90 |
|---|---|---|---|---|---|
| payload directly grounded | no | 350 | **0.1689** | 0.006161 | 1.221 |
| | yes | 250 | **0.7743** | 0.09767 | 5.621 |
| number of ground ties | 1 | 277 | **0.1779** | 0.005906 | 2.541 |
| | 2 | 187 | **0.3997** | 0.03115 | 2.938 |
| | 3 | 107 | **0.5488** | 0.06167 | 3.706 |
| | 4 | 29 | 0.5477 | 0.1163 | 3.621 |

Two large, monotone effects:

  * grounding the payload **directly** costs a factor of **4.6** in median in-band
    transmissibility;
  * each additional ground tie degrades isolation, 0.178 -> 0.400 -> 0.549, a factor of 3
    across the range.

Both are physically sensible - more and stiffer coupling to ground means more of the
ground's motion reaches the payload - and both are keyed to the **ground coupling
structure**, a feature distinct from the performance axes of Finding 013.

## 3. A derived structural law

Writing m0, f0, g0 for the payload's mass and its OWN ground stiffness and damping, and
expanding the cofactor,

    P(s) = sum_j cofactor_{j0}(s) * (f_j + g_j s)

and for j >= 1 the submatrix deleting row j and column 0 of the DIAGONAL mass matrix has
a zero column, so its determinant vanishes at leading order. **Only j = 0 survives at
order s^(2n-2).** Hence

    T(s) = g0/(m0 s) + (f0 + beta)/(m0 s^2) + O(s^-3)

with beta collecting the j >= 1 cofactors at order s^(2n-3).

**Confirmed at leading order** (600 structures, no exclusions):

| case | omega | 1e3 | 1e4 | 1e5 | 1e6 | 1e7 | 1e8 | target g0/m0 |
|---|---|---|---|---|---|---|---|---|
| payload grounded | omega*abs T | 34.36 | 12.22 | 11.842 | 11.839 | 11.839 | 11.839 | **11.839** |
| no payload tie | omega*abs T | 0.0620 | 2.51e-4 | 1.45e-5 | 1.44e-6 | 1.44e-7 | 1.44e-8 | **0** |

> **omega * T(j omega) -> g0 / m0**, involving only the payload's own ground damping and
> its mass, and nothing else in the network.

**Refuted at the next order.** The claim "if the payload has no ground tie then
T = O(s^-3)" is **false**. Scaling by omega^2 for such a structure:

| omega | 1e3 | 1e4 | 1e5 | 1e6 | 1e7 | 1e8 |
|---|---|---|---|---|---|---|
| abs T * omega^2 | 61.97 | 2.505 | 1.4515 | 1.43814 | 1.438003 | **1.438002** |

A non-zero plateau at 1.438002. **beta is not zero**: the omega^-2 term is carried by the
OTHER ground ties, not by the payload's. The falloff is s^-2, not s^-3.

## 4. The two test failures, both mine

Each made a test that could not fail.

**(a) A guard that excluded the counterexamples.** Step 25 computed the asymptote error
only for structures with `asym > 0`, i.e. those WITH a payload ground tie -
precisely the structures the claim is most likely to hold for. It reported a worst
relative deviation of 1.64e-04 and called the formula confirmed. Removing the guard
immediately produced a structure with f0 = g0 = 0 where the measured falloff was omega^-2
against the claimed omega^-3.

**(b) An asymptotic claim tested at a single frequency.** Even without the guard, "the
error is small at omega = 3e5" is not evidence for an asymptotic statement. The correct
test is the RATE: scale the residual by the predicted power and look for a plateau. That
is what section 3 reports.

A third, smaller artefact: the corrected test prints a "worst relative error 1.64e+08",
which is division by a target of zero when g0 = 0. The right measure there is absolute
error, which is 1.4e-8 - the law holds in that case too.

## 5. Why this matters for the certificate layer

The confirmed law is a **structural predicate on a distinct structural feature**. It says
the payload's own ground damping sets the leading high-frequency behaviour, so a structure
that ties the payload to ground with a damper cannot roll off faster than -20 dB/dec
there, whatever else the network contains.

| requirement | status |
|---|---|
| sound | yes at leading order, verified over 600 structures with no exclusions |
| class-level | yes - the coefficient depends on no other component |
| keyed to a structural feature | yes - the payload's own coupling, not a performance metric |
| cost | O(1) given (m0, g0) |
| continuous bound | yes - g0/m0 is continuous in the component values |
| domain tag | linear, time-invariant; with no payload tie the leading term vanishes and the next order governs, which is NOT characterised |

By Finding 013's criterion this is the right KIND of object: keyed to the ground coupling
structure, which produces a factor-of-4.6 effect, rather than to another performance
metric.

## 6. Limits

  * The refutation means the law as originally stated is **not** usable as a certificate in
    the "no payload tie" case; beta is uncharacterised. Only the leading term is safe.
  * Survival-rate gaps in the first table rest on 13 to 21 surviving structures per bucket
    and are noisy. The median-transmissibility gaps, on 29 to 350 structures per bucket,
    are the credible evidence.
  * One ensemble family, one band edge, one calibration.
  * The 4.6 factor is measured on random trees with log-uniform component values and is not
    claimed to be universal.
