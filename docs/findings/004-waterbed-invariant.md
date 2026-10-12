# Finding 004 - The waterbed invariant, and three numerical traps it exposed

Status: invariant established (exact). M1 gains a second independent certificate.
M2 is NOT closable by this route. Code: ecdr/l0/invariants.py, ecdr/l0/peaks.py.

## 1. The invariant

For a stable minimum-phase T with T(0) = 1, the classical Poisson/Bode integral gives

    integral_0^inf  ln|T(jw)| / w^2  dw  =  (pi/2) * ( n1/n0 - d1/d0 )

where n_k and d_k are the coefficients of s^k in numerator and denominator. This is
obtained by applying Vieta to each polynomial separately, so it is exact algebra and
needs no root finding, no quadrature and no numerical analysis of any kind.

Evaluating it for the three mechanism classes:

| mechanism | n1/n0 | d1/d0 | integral |
|---|---|---|---|
| M1 passive SDOF | 2 zeta / wn | 2 zeta / wn | **0** |
| M2 tuned mass damper | c2 / k2 | c2 / k2 | **0** |
| M3 sky-hook active | 0 | 2 zeta / wn | **- pi zeta / wn** |

The passive classes cancel term by term: the same damping appears in the numerator of
T and as the s coefficient of det(A). The sky-hook has no zeros, so nothing cancels,
and its integral is strictly negative.

Verification:
  * Vieta against the closed-form physics: worst difference 1.4e-17, 11 cases
  * independent 40-digit mpmath quadrature: passive cases 2e-11 to 5e-11 (quadrature
    error around a true zero); M3 matches -pi zeta / wn to 8 significant figures
  * a sanity identity: M2 with the absorber switched off (mu = 1e-7) reproduces M1
    to 5e-8 relative, which is the check that the 2-DOF model is not silently wrong

Interpretation: log-isolation weighted by 1/w^2 must be paid for exactly by
log-amplification. A passive mechanism has zero budget; the sky-hook has a negative
one, i.e. it is allowed net isolation. At zeta = 2, wn = wn_min the sky-hook budget
is -0.0634, which is 8.66x what the band demands.

## 2. Three numerical traps, all caught by cross-checking

Each of these silently produced a WRONG scientific conclusion before it was caught.

**Trap 1 - grid peak checks.** A 2000-point log grid under-reported the peak of a
light, lightly damped absorber by a factor of **178386** (reported 1.243, true
221745). The resonance width was smaller than the grid spacing, so the grid stepped
over it and designs that grossly violate the peak constraint looked feasible.
Fix: candidate frequencies from the roots of d/dx(|N|^2/|D|^2) = 0, which were
verified correct; evaluation by the caller transfer function.

**Trap 2 - evaluating |D|^2 from the expanded polynomial.** The determinant expansion
of the 2-DOF chain has coefficients spanning ~1e10. Near a resonance the true value is
many orders below the individual terms, and the computed |D|^2 came out **negative**,
so the candidate root was discarded and the real peak was never evaluated.
Fix: never evaluate the transfer function through the expansion; use the 2x2 solve.

**Trap 3 - computing the invariant integral through the expansion.** The same
ill-conditioning inflated the low-frequency log-area by more than 2x (0.0136 instead
of the true value), which flipped the M2 verdict from "short" to "reaches".
Fix: the same callable-based evaluation everywhere.

The general lesson, now written into the code: **polynomial coefficients are for
generating candidates; magnitudes are always evaluated with the well-conditioned
representation.**

## 3. What it gives for M1: a second, independent certificate

The band constraint forces the low-frequency amplification integral up to a floor:

    W_amp >= |ln T_iso| / omega_low = 0.00732936          (T_base)

Scaling reduction: T depends on omega_n only through r = w/omega_n, so
W_amp = (1/omega_n) * H(omega_low/omega_n; zeta), which is decreasing in omega_n.
The sag constraint gives omega_n >= wn_min, so **the maximum sits exactly at
omega_n = wn_min** and the problem collapses to ONE variable.

Result: over all peak-feasible zeta, the largest achievable W_amp is **0.00650818**,
short of the floor by **0.00082118, or 11.20 percent**.

So a passive SDOF isolator cannot even raise enough amplification budget to buy the
isolation the band demands, let alone shape it. This is a different argument from
Lambda = 0.2903 in Finding 001: the first is about two incompatible bounds on
omega_n, this one is a conservation law. They agree, which is reassuring, and the
reduction to one variable makes this route close to a proof.

## 4. What it does NOT give for M2

| | best peak-feasible W_amp | vs floor 0.00732936 |
|---|---|---|
| M1 passive SDOF | 0.00650818 | short by 11.20 percent |
| M2 passive chain | 0.00818667 | **reaches the floor** |

Over 45,696 designs examined with verified exact peaks, 13,914 were peak-feasible and
their W_amp ranged from 0.0027 (min) through 0.0051 (median) to 0.0082 (max).

So the passive chain has **ample amplification budget**. The invariant does not
obstruct M2. The obstruction for M2 must therefore live in the SHAPE of |T| - where
the amplification and the isolation sit in frequency - not in the weighted integral.
The waterbed route is closed for M2, and closing M2 needs a different tool.

That is a negative result, but a clean and useful one: it eliminates a whole class of
arguments and says precisely where the next attempt must look.

## 5. Where this leaves the certificate layer

| mechanism | infeasibility evidence | status |
|---|---|---|
| M1 passive SDOF | Lambda = 0.2903 (two incompatible bounds) AND waterbed short by 11.20 percent | **proved twice, by independent arguments** |
| M2 passive chain | none; waterbed budget is satisfied; best peak-feasible in-band |T| remains far above the limit | **open** |
| M3 sky-hook | feasible with an explicit witness | **witnessed** |

M2 remains the highest-value theoretical target, and Finding 003's estimate stands:
closing it converts "no witness found" into a theorem.
