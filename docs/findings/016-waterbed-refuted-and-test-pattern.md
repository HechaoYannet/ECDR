# Finding 016 - The waterbed closed form is refuted; and a pattern in my own tests

Status: Finding 004's closed form for the waterbed integral **does not hold in general**
and is downgraded. A fourth instance of a self-confirming test was caught, and the pattern
is now named.
Code: ecdr/structure/waterbed.py.
Reproduce: scripts/step28_waterbed.py, step29_waterbed_residual.py, step30_waterbed_disagreement.py

## 1. What was being checked

Finding 015 said the second certificate must live on a structural axis. The classical
band-tradeoff object is the waterbed integral, and Finding 004 had recorded a closed form
for it:

    W = integral of ln|T(j w)| / w^2 dw  =  (pi/2) (p1/p0 - q1/q0)

If that held for an arbitrary network it would be a class-level certificate. So it was
checked two ways: the closed form from polynomial coefficients, and the integral done
numerically.

## 2. The two ways disagree, convergently

| | value |
|---|---|
| median relative difference, closed form vs integral | **572** |
| worst relative difference | 4.9e+07 |

and over 200 networks:

| threshold | networks exceeding it |
|---|---|
| abs W > 1e-9 | 198 of 200 |
| abs W > 1e-6 | 32 |
| abs W > 1e-4 | 22 |
| abs W > 1e-3 | 14 |
| abs W > 1e-2 | 2 |

median abs W = 1.354e-08, max abs W = 1.211e-02.

**The large residuals are not quadrature error.** Tripling the grid moves the ten largest
by less than 1.2e-08:

| index | n | W | change under 3x refinement |
|---|---|---|---|
| 76 | 4 | 1.21109698e-02 | 5.5e-09 |
| 199 | 6 | 1.10972437e-02 | 5.7e-09 |
| 33 | 4 | 8.78876774e-03 | 4.9e-09 |
| 47 | 8 | 6.68782150e-03 | 4.9e-09 |

## 3. The closed form is exactly zero, and that part is solid

    P(s) = e0^T adj(A) (f + g s),        A = K + C s + M s^2
    adj(X + eY)'|_0 = det(X) [ tr(X^-1 Y) X^-1 - X^-1 Y X^-1 ]
    p0 = e0^T adj(K) f = det(K),          since K^-1 f = 1
    p1/p0 - q1/q0 = -(K^-1 C 1)_0 + (K^-1 g)_0

and **C 1 = g exactly**, because C = C_internal + diag(c_i) and every row of the internal
damping Laplacian sums to zero. Verified: max abs(C 1 - g) = 2.8e-14 over 200 networks,
and the cancellation p1/p0 = q1/q0 holds to 6.9e-18.

**So the closed form predicts exactly zero for every passive network, while the integral
is non-zero and converged for about one network in ten.** The identity rests on a Laplacian
row sum and holds to roundoff; the formula does not survive.

**Finding 004's use of the waterbed closed form is therefore downgraded.** The quantity
itself is well defined and computable; the closed form is not a valid expression for it.

## 4. A pattern in my own tests, now named

This is the fourth time in four rounds that a verification I wrote could not fail:

| round | defect | what it did |
|---|---|---|
| Finding 013 | product of sequential survivor ratios | telescopes to the answer **as an identity**; reported "exact agreement" |
| Finding 014 (a) | ensemble always tied exactly one ground node | the axis under test had **zero variance**; printed a clean table |
| Finding 014 (b) | guard `if asym > 0` | excluded precisely the structures that **refute** the claim |
| Finding 016 | script's printed verdict | asserted the residual "shrinks under refinement" while its own table showed it **stable to 1e-12** |

Each time the test produced a confident, clean-looking number, and each time the number
was manufactured by the test rather than measured by it. The fourth case is the purest:
the verdict sentence was written into the script before the table was read, and the table
contradicted it.

**Standing rules adopted from this, to be applied to every verification from now on:**

  1. **Name the observation that would refute the claim, and check it is reachable.** If
     no input could produce a different answer, the test is decoration.
  2. **Never print a verdict that is not computed from the data in the same run.** A
     hardcoded conclusion cannot be contradicted by its own output.
  3. **Check the variance of every axis before testing an effect on it.**
  4. **For an asymptotic or convergence claim, test the RATE, not the residual at one
     point.**
  5. **Prefer an identity that can be verified to roundoff over a fit.** The cancellation
     result here (6.9e-18) is trustworthy; the Vandermonde route that produced 572 was not.

## 5. Consequence for the certificate layer

The waterbed was a candidate for the second certificate. Its status now:

| property | status |
|---|---|
| well defined and computable | yes |
| structural dependence | **unknown** - the closed form that would have settled it is invalid |
| usable as a certificate | **not yet** - a bound needs a valid expression |

So the second composable certificate is **still not found**, and the waterbed cannot be
pressed into service until its dependence on structure is re-derived correctly. That is a
clean next step rather than a dead end: the integral is computable, converged, and varies
across structures (max 1.2e-2 against a median of 1.4e-8), so it may yet carry structural
information.

## 6. Limits

  * Only the closed form is refuted. The integral itself was not shown to violate any
    physical law; the discrepancy may be a wrong formula rather than a wrong physics.
  * The numeric integral has a floor of about 1e-8 from truncating the range, so the 198
    of 200 above 1e-9 is not evidence that those are genuinely non-zero.
  * 200 networks, one ensemble, one seed. The 22-of-200 disagreement rate is indicative
    and not precise.
  * No attempt was made in this round to re-derive the correct formula.
