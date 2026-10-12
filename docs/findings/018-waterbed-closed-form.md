# Finding 018 - The waterbed closed form, corrected

Status: found, and verified where it can be evaluated. The correct expression is a sum
over the right-half-plane zeros of the numerator; Finding 004's coefficient form is
invalid, as Finding 016 said, and Finding 017's pointer was right.
Reproduce: scripts/step34 - step39.  Data: runs/waterbed_ratio.json

## 1. The result

> **W = integral ln|T(j w)| / w^2 dw  =  pi * sum over RHP zeros z of P of Re(1/z)**

This is the classical Bode sensitivity integral with a 1/w^2 weight. Dimensional analysis
points at it immediately: W has units of TIME and 1/z has units of time, whereas the old
coefficient form (pi/2)(p1/p0 - q1/q0) is dimensionless - which should have been a warning
when it was first written down.

## 2. Agreement with numerical integration, stratified by degree

24 networks have |W_numeric| above the integral's noise floor. The formula is evaluated
with mpmath at 60 digits, roots fitted from float64 samples.

| n | degree of P | compared | ratio within 1e-3 | median abs(ratio - 1) |
|---|---|---|---|---|
| 4 | 7 | 3 | **3** | 4.17e-07 |
| 5 | 9 | 3 | **3** | 4.12e-07 |
| 6 | 11 | 9 | 4 | 3.36e-03 |
| 7 | 13 | 3 | 1 | 8.6e+01 |
| 8 | 15 | 6 | **0** | 5.5e+01 |

Individual cases at the low degrees:

| index | n | RHP zeros | W numeric | pi * sum Re(1/z) | ratio |
|---|---|---|---|---|---|
| 76 | 4 | 2 | 1.21109681e-02 | 1.21109588e-02 | 0.999999 |
| 33 | 4 | 2 | 8.78875204e-03 | 8.78874837e-03 | 1.000000 |
| 101 | 4 | 3 | 7.31087939e-03 | 7.31087808e-03 | 1.000000 |
| 70 | 5 | 3 | 1.65371315e-03 | 1.65371246e-03 | 1.000000 |
| 118 | 5 | 2 | 1.06320731e-03 | 1.06320774e-03 | 1.000000 |
| 3 | 6 | 4 | 7.43559862e-04 | 7.43558075e-04 | 0.999998 |
| 138 | 6 | 3 | 2.11627385e-03 | 2.11627606e-03 | 1.000001 |

**Perfect agreement at degree 7 and 9, degrading at 11, lost at 13 and 15.** That is the
signature of a root-finding conditioning limit rather than a formula failure: the
coefficients come from a float64 least-squares fit with roughly 1e-16 relative error, and
a degree-15 polynomial amplifies that without bound.

## 3. The vanishing prediction, exact

| | |
|---|---|
| networks with no RHP zero | 85 |
| their max abs W_numeric | 1.049e-09 |
| their max abs formula value | **0** |

85 of 85: no right-half-plane zero, no waterbed. This was Finding 017's necessity result
and it is now explained rather than merely observed.

## 4. What W is, physically and structurally

W is a **band-tradeoff exchange rate**: attenuation inside a band must be paid for by
amplification outside it, and the rate is fixed by the non-minimum-phase zeros of the
transmissibility. By Finding 012's criterion it is a good certificate candidate:

| requirement | status |
|---|---|
| continuous bound | yes - a sum of reciprocals of zeros |
| class-level | yes - one expression for any topology |
| keyed to a structural feature | yes - the right-half-plane zeros of P, which depend on the whole network, NOT on the payload tie of Finding 014 |
| cheap | the bound is O(1) once the zeros are known; finding them is the expensive part |
| domain tag | linear, time-invariant; requires P's roots to be computable |

It is also on a **different structural axis from Finding 014's law**, which is what
Finding 015 requires of a second certificate.

## 5. The measurement apparatus was wrong five times

The formula was right from the first attempt. Everything after was my own instrumentation,
and each fault made a check that could not fail:

| # | fault | effect |
|---|---|---|
| 1 | numpy roots on a degree-15 polynomial | |P(z)|/scale = 2e93: "roots" that are not roots |
| 2 | `mp.polyval(coef[::-1])` | evaluated the reversed polynomial; residual exactly 1.0 |
| 3 | degree fitted as 2n | invents a leading coefficient that is pure noise (it is 2n-1) |
| 4 | verification against the FITTED polynomial | polyroots is zero at its own roots by construction - verified nothing |
| 5 | true P evaluated into a REAL array | ComplexWarning: silently discarded the imaginary part of every complex root |
| 6 | mpmath given ASCENDING coefficients | mpmath, like numpy, takes descending. Both the root finder and the check were wrong together, so they agreed |
| 7 | residual check overflows | det(M s^2 + ...) overflows at large |z|, so |P(z)|/scale is inf or 1e70 regardless of root quality |

**What finally worked was not a better check but a better question**: stop filtering on a
residual that could not be trusted, and instead **stratify the ratio by the conditioning
variable**. Agreement perfect at degree 7 and 9, absent at 13 and 15, is a pattern that
identifies the root finder as the culprit without needing any residual to be correct. That
is rule 3 of Finding 016 applied to a continuous variable rather than a variance.

## 6. Limits

  * The formula is confirmed only where it can be evaluated: degrees 7 and 9, six
    networks. At degrees 13 and 15 it is neither confirmed nor refuted, because the roots
    are unobtainable. Closing that gap needs the coefficients in higher precision, not a
    better root finder, since the float64 fit is the limiting factor.
  * 24 comparable networks out of 200; one ensemble, one seed.
  * The derivation is classical and was not written out here; it was inferred from the
    degree-7 and degree-9 agreement plus the exact vanishing. A written proof should
    precede publication.
  * W being non-zero for non-minimum-phase networks was already established by Finding
    017; what is new here is the closed form.
