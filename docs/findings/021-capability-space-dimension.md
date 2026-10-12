# Finding 021 - The capability space has 4.6 axes; Finding 020 was too pessimistic

Status: Finding 020 concluded that "no two physical performance bounds will compose" and
that this threatened the library programme. That conclusion is **withdrawn**. It was drawn
from cuts all taken on ONE axis, not from a property of the space. The space has an
effective dimension of 4.62, and a sound topology-keyed bound is nearly uncorrelated with
isolation performance.
Reproduce: scripts/step44_capability_dimension.py, step45_key_pairs.py
Data: runs/capability_dimension.json, runs/key_pairs.json

## 1. The measurement

Twelve quantities over 300 networks - bounds, structural counts and measured performance -
rank-standardised, then the eigenvalue spectrum of their correlation matrix.

| component | eigenvalue | share of variance | cumulative |
|---|---|---|---|
| 1 | 4.3292 | 0.3608 | 0.3608 |
| 2 | 2.9990 | 0.2499 | 0.6107 |
| 3 | 1.2478 | 0.1040 | 0.7147 |
| 4 | 0.8436 | 0.0703 | 0.7850 |
| 5 | 0.6494 | 0.0541 | 0.8391 |
| 6 | 0.5295 | 0.0441 | 0.8832 |
| 7 | 0.4399 | 0.0367 | 0.9199 |
| 8-11 | ... | ... | 1.0000 |
| 12 | 0.0000 | 0.0000 | 1.0000 |

  * **participation ratio (effective number of axes): 4.621**
  * leading eigenvalue share: **0.3608**
  * components for 90 percent of variance: **7**

**The capability space is emphatically not one-dimensional.** A one-dimensional space would
show a leading share above 0.9; it shows 0.36.

## 2. The pairwise structure

| threshold | pairs |
|---|---|
| abs(rho) < 0.1 | **14 of 66** |
| abs(rho) < 0.2 | 28 of 66 |
| abs(rho) < 0.5 | 54 of 66 |

median abs(rho) = 0.2786.

Least correlated:

| pair | rho |
|---|---|
| n components x in-band abs T | +0.0174 |
| in-band abs T x mean degree | +0.0174 |
| in-band abs T x total damping | +0.0196 |
| W waterbed x payload degree | +0.0204 |
| g0/m0 x payload degree | -0.0034 |

Most correlated:

| pair | rho | note |
|---|---|---|
| n components x mean degree | **+1.0000** | **tautological**: a tree on n nodes has mean degree 2(n-1)/n |
| sag x in-band abs T | -0.8191 | both are isolation performance |
| n components x total mass | +0.8010 | more components, more mass |

## 3. The pairs that matter, verified

The pairs joining a SOUND, topology-keyed bound to a performance bound, across three seeds
and with a bootstrap over networks:

| pair | seed 5 | seed 17 | seed 29 | 95% CI (seed 5) | contains 0 |
|---|---|---|---|---|---|
| n components x in-band abs T | +0.0193 | -0.0572 | -0.1737 | [-0.0882, +0.1363] | yes |
| W waterbed x payload degree | +0.0278 | +0.0914 | +0.0534 | [-0.0795, +0.1306] | yes |
| g0/m0 x payload degree | -0.0214 | -0.1108 | -0.0218 | [-0.1349, +0.0812] | yes |
| sag x in-band abs T | -0.8191 | -0.8108 | -0.8111 | [-0.8567, -0.7724] | no |

Honest reading: the modal pair is **weakly** correlated, not uncorrelated. Seed 29 gives
-0.174. But that is against -0.811 for the performance pair, stable to three decimal
places across every seed. The contrast is the finding, not an exact zero.

## 4. Why Finding 020 went wrong

Finding 020's VAL family was sag, peak, in-band, g0/m0 and W. **Every one of those is a
monotone measure of how well the structure isolates.** It found them redundant with each
other, correctly, and then generalised to "every physical performance bound is such a
monotone measure, so no two certificates will compose".

That generalisation examined one axis and concluded about the space. The correct statement
is:

> **No two cuts on the SAME axis compose. Cuts on different axes do.**

and the space has about 4.6 axes to choose from.

## 5. The immediate consequence: a composing pair exists

The modal bound - a structure with n degrees of freedom has a free response of at most n
harmonics - is:

  * **sound** for every parameter assignment, by linear algebra;
  * **keyed to topology**, not to component values;
  * a ~50 percent cut when the requirement's mode count is placed at the median of the
    component-count distribution;
  * **weakly correlated with isolation performance**, abs(rho) <= 0.17 across three seeds
    against 0.81 for a competing performance bound.

So a modal certificate and a performance certificate are a **composing pair**. That is the
first such pair the programme has produced.

## 6. And it softens Finding 010

Finding 010 eliminated mode counting because g(N) = 32, constant, in the space of all
connected labelled graphs with a fixed requirement of 4 frequencies. That measurement
stands, but its generality does not: the space there was dominated by the largest graphs,
so a fixed threshold on n covers a vanishing fraction. Finding 012 had already established
that coverage is a property of the TRIPLE (invariant, ensemble, requirement), and here the
requirement's mode count sits at the median of the component-count distribution, where the
cut is 50 percent and does not vanish.

**So mode counting is not eliminated as such.** It is eliminated when the requirement is
fixed while the space grows, which is a statement about benchmark design. The condition to
check is whether the requirement sits at the marginal point of the relevant distribution -
which is Finding 012's calibration condition, now doing real work.

## 7. The design rule, corrected for the second time

| round | rule | status |
|---|---|---|
| 013 | structural cuts compose, performance cuts do not | superseded |
| 019 | topology-keyed cuts compose, value-keyed do not | refuted by 020 |
| 020 | cuts must not be monotone in a common scalar | directionally right, over-generalised |
| **021** | **cuts must lie on different AXES of the capability space; measure the rank correlation between the BOUNDS and require abs(rho) well below the within-axis values** | current |

The operational test is unchanged from Finding 020 and is now known to be satisfiable:
compute Spearman rho between two certificates' bounds. Within-axis performance pairs sit at
0.39 to 0.82; the modal pair sits at 0.02 to 0.17.

## 8. Limits

  * **The correlation matrix has an exact rank deficiency**: n components and mean degree
    are algebraically dependent for trees, giving eigenvalue 12 = 0 and rho = 1.0000. The
    participation ratio is computed on a rank-11 matrix and is slightly distorted by it.
    The conclusion of multiple axes does not depend on this, since the top two eigenvalues
    hold only 61 percent of variance between them.
  * Twelve quantities chosen by hand. A different list would give a different spectrum, and
    no attempt was made to choose them to maximise or minimise the dimension.
  * One ensemble family, one physical domain, one calibration. The 4.6 axes are axes of
    THIS ensemble.
  * "Weakly correlated" for the modal pair rests on abs(rho) <= 0.17 over three seeds; the
    seed-29 value of -0.174 leaves the pair correlated in the loosest sense.
  * The composing pair in section 5 is a composing pair **by correlation**. The library
    argument of Finding 011 also needs each cut to take a constant fraction of what
    REMAINS, which has not been measured for this pair.
