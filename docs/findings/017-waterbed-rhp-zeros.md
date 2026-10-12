# Finding 017 - Why the waterbed is not zero: right-half-plane zeros

Status: Finding 016's **conclusion** stands (the closed form is not valid), but its
**assessment of which side was broken was wrong**. Both numerical routes it compared were
suspect, and only a third, soundly formulated one settles it. The hole in the contour
argument is now located: right-half-plane zeros of the numerator.
Code: ecdr/structure/waterbed.py.
Reproduce: scripts/step31_waterbed_quadcheck.py, step32_waterbed_stable.py, step33_rhp_zeros.py

## 1. Two numerical routes were both broken

Finding 016 compared a trapezoid rule against scipy.quad and found a converged 572-fold
disagreement, then concluded the closed form was refuted. The comparison was between two
bad measurements.

Both used the substitution u = ln w, which makes the integrand ln|T| * exp(-u). Near
w -> 0, ln|T| = O(w^2) is obtained by subtracting 1 from |T| - catastrophic cancellation -
and is then multiplied by exp(-u), which diverges. **A tail that is genuinely zero gets
turned into a large spurious number by a tiny relative error amplified by a huge factor.**

The signature is unmistakable in the quad column:

| index | trapezoid | quad | quad error estimate |
|---|---|---|---|
| 76 | 1.21109698e-02 | -7.839e+01 | 4.4e-10 |
| 199 | 1.10972437e-02 | 1.045e+02 | 6.9e-10 |
| 33 | 8.78876774e-03 | 3.136e+02 | 2.2e-09 |
| 47 | 6.68782150e-03 | -5.22593408e+01 | 5.2e-10 |
| 185 | 5.01511190e-03 | -5.22610135e+01 | 3.9e-10 |

A quadrature reporting an error of 1e-10 while returning +104 for a quantity of order
1e-2, and returning the SAME -52.26 for two different structures, is failing rather than
measuring. It also raised IntegrationWarning, which was not acted on.

## 2. The sound formulation settles it

Integrate in w directly, which keeps the weight bounded, and add both tails analytically:
near zero the integrand tends to a finite constant c, at infinity ln|T| ~ ln(A/w).

| control / structure | value |
|---|---|
| SDOF (known zero) | **1.66e-12** |
| index 76 | 1.211097e-02 |
| index 199 | 1.109724e-02 |
| index 33 | 8.788752e-03 |
| index 47 | 6.687819e-03 |
| index 90 | 4.357743e-03 |

**All ten flagged structures reproduce the trapezoid to five or six significant figures.**
So the trapezoid in u was usable at its range and quad was the broken side - and,
critically, **W is genuinely non-zero**: median abs W = 9.99e-10, max 1.211e-02, with
23 of 200 above 1e-4.

## 3. The hole in the contour argument

The argument was: close the imaginary axis in the right half plane; the arc at infinity
vanishes, the indentation at the origin vanishes because T'(0)/T(0) = 0 (proved in Finding
016), and an indentation around an interior zero vanishes as O(eps log eps); no poles
inside; therefore W = 0.

Every step is correct and the conclusion is still false, because it accounts for the
branch POINT and not the branch CUT. When P has a zero z with Re z > 0, ln T has a branch
point there, and the cut attached to it contributes to the contour integral. The
indentation around the point is indeed O(eps log eps), which is exactly why the argument
looked airtight.

The prediction is then sharp and testable:

    W != 0   implies   T has a right-half-plane zero

## 4. The test

P(s) = det(A) [A^-1 (f + g s)]_0 with A = M s^2 + C s + K, fitted in a scaled variable.
The fit is verified against its own sample points before any root is trusted: **max
relative residual 1.16e-14 over 40 networks.**

| index | W | RHP zeros of P |
|---|---|---|
| 76 | 1.2111e-02 | 2 |
| 199 | 1.1097e-02 | 3 |
| 33 | 8.7888e-03 | 3 |
| 47 | 6.6878e-03 | 10 |
| 185 | 5.0151e-03 | 10 |
| 90 | 4.3577e-03 | 6 |
| 134 | 2.8536e-03 | 5 |
| 0 | 7.5765e-09 | 1 |
| 2 | 5.4988e-09 | 0 |

Contingency over the ensemble:

| | W != 0 | W == 0 |
|---|---|---|
| RHP zero present | 22 | 158 |
| no RHP zero | **0** | 20 |

## 5. What is established, and what is not

  * **Necessary condition holds with no counterexamples**: of the 20 networks with no
    right-half-plane zero, **none** has a non-zero W. 0 of 200 structures violate it.
  * **It is not sufficient**: 158 of 180 networks with an RHP zero have W below 1e-4.
    Concordance is only 0.21, so the existence of a zero is not the whole story - the
    zero LOCATIONS must enter.
  * So the correct formula is a Bode-type integral with a sum over right-half-plane zeros,
    and the naive "always zero" is false.
  * **The closed form W = (pi/2)(p1/p0 - q1/q0) remains invalid** - it predicts exactly
    zero for every passive network, and W is not zero. Finding 016 reached the right
    verdict from a comparison it could not trust.

## 6. Limits

  * "W == 0" uses a threshold of 1e-4. W is continuous, so 22-versus-158 is a statement
    about a threshold, not about exact zeros. At 1e-9 the count is 97 of 200, but the
    integral has a floor near 1e-9 from range truncation.
  * The root count comes from a polynomial fit. The fit is excellent at its sample points,
    but polynomial roots can still be ill-conditioned; the 20-of-20 necessary-condition
    result is consistent, and 158 counterexamples to sufficiency is a large margin, so
    neither conclusion turns on a marginal case.
  * 200 networks, one ensemble, one seed.
  * The correct closed form was NOT derived this round. The pointer is now specific:
    a sum over right-half-plane zeros.
