# Finding 024 - A fourth certificate, and the composition replicates on a new family

Status: the sequential conditionals of Finding 023 reproduce essentially unchanged on a
different topology family, a different value distribution and a different component range.
A fourth sound certificate is added. One calibration is shown to deplete the space, and the
reading of that case is flagged as vacuous rather than reported as a result.
Reproduce: scripts/step50_fourth_certificate.py.  Data: runs/fourth_certificate.json

## 1. The fourth certificate: the FAST time scale

Finding 023 bounded the slowest natural frequency from above (Rayleigh with the trial vector
1). The other side comes from the infinity norm, which dominates the spectral radius:

    omega_n^2 = lambda_max(M^-1 K)  <=  max_i ( K_ii + sum_{j != i} |K_ij| ) / m_i
                                   =  max_i ( 2 sum_{j != i} k_ij + k_i^ground ) / m_i

A requirement needing a response FASTER than the structure can deliver is refuted whenever
the bound falls below the required frequency. Verified:

| check | value |
|---|---|
| structures tested | 300 |
| max ratio true omega_n^2 / bound | **0.997831** |
| **violations (ratio > 1)** | **0** |
| median tightness (bound / true) | **1.333** |

Sound for every parameter assignment, O(n^2) to evaluate, and the **tightest** of the four
bounds.

The certificate set is now four members covering four different mechanisms:

| | statement | basis | median tightness |
|---|---|---|---|
| C1 modal | n degrees of freedom gives at most n harmonics | linear algebra | exact |
| C2 statics | sag under gravity <= delta_max | equilibrium | exact |
| C3 slow | omega_1^2 <= (sum ground k) / (sum m) | Rayleigh | 2.73 |
| C4 fast | omega_n^2 <= max_i (K_ii + sum abs K_ij) / m_i | infinity norm | 1.33 |

C3 and C4 are the two sides of a two-sided time-scale constraint, and they are separate
predicates: one refutes structures that are too fast, the other those that are too slow.

## 2. The replication

A genuinely different ensemble: **random tree plus two extra edges** (so the graphs have
loops), **uniform** component values instead of log-uniform, and **n in 2..7** instead of
2..8. Sequential conditionals with all thresholds at the 50th percentile, 600 networks:

| cut | original family marginal | conditional | NEW family marginal | conditional |
|---|---|---|---|---|
| C1 modal | 0.4267 | 0.4267 | 0.3233 | 0.3233 |
| C2 statics | 0.5000 | **0.5640** | 0.5000 | **0.5468** |
| C3 slow | 0.5000 | **0.7600** | 0.5000 | **0.7935** |
| C4 fast | 0.5000 | **0.3889** | 0.5000 | **0.3684** |
| **round survival** | | **0.0367** | | **0.0400** |

**The conditionals agree to within 0.035 across the two families.** Round survival 0.0367
against 0.0400; rounds for N = 1e10 are 7.0 and 7.2, i.e. **28 and 29 certificates**.

This is the replication Finding 024 was written to obtain. The conditionals are a property of
the certificates and the requirement, not of the ensemble that produced them.

## 3. One calibration depletes the space, and the reading there is vacuous

The same run at the 30th percentile, which tightens every threshold and so cuts 70 percent
marginally:

| cut | marginal | given previous | remaining |
|---|---|---|---|
| C1 modal | 0.1583 | 0.1583 | 0.8417 |
| C2 statics | 0.7000 | 0.7089 | 0.2450 |
| C3 slow | 0.7000 | **0.9932** | 0.0017 |
| C4 fast | 0.7000 | **0.0000** | 0.0017 |

**C4 records a conditional of 0.0000, and that number is meaningless.** After C3 the
remaining set is 0.0017 of 600 - about one structure - and a conditional computed on one
point is noise. Reporting "C4 cuts nothing" here would be the same class of error as the six
identity traps and the inverted ratio: a number produced by a degenerate configuration and
read as a finding.

What the row does show is real but different: **tight calibrations deplete the space before
the library gets through its members**, so the ordering of cuts matters and late cuts can
find nothing left to cut. That is a genuine design constraint on how certificates are
ordered and how the requirement is calibrated, and it is not the same statement as "C4 is
weak".

## 4. C4 is the weakest member at a working calibration

At the 50th percentile C4's conditional is 0.389 and 0.368 against C2's 0.564 and C3's 0.760.
Since its marginal is 0.5, a conditional below 0.5 means C4 is **mildly redundant** with what
C1 to C3 already removed - the ratio is above 1 - while C3 at 0.760 is strongly complementary.
So the four members are not of equal value, and C3 carries the round.

## 5. Library arithmetic

| family | round survival | rounds for 1e10 | certificates |
|---|---|---|---|
| original, 50th pct | 0.0367 | 7.0 | **28** |
| new, 50th pct | 0.0400 | 7.2 | **29** |

At the space sizes this ensemble reaches the count is still about four rounds against a few
hundred structures, so the separation remains a statement about growth.

## 6. Limits

  * One calibration depletes; only two working calibrations were run, and both at the 50th
    percentile. The conditionals' dependence on the calibration is therefore unmeasured
    except by the degenerate 30th-percentile case.
  * The two ensembles differ in three ways at once, so the replication does not isolate which
    of topology, value distribution or n range the agreement is robust to.
  * C4 is the weakest member and was measured on the same 600 networks as the others; no
    independent sample for it.
  * All bounds remain elementary. Four work, but the tightest is still loose by 1.33 and the
    loosest by 2.73, so the cuts are smaller than perfect bounds would give.
  * One physical domain. Nothing here says the same four mechanisms exist elsewhere, which is
    the M6 question.
