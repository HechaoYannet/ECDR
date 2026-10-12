# Finding 023 - The independence ratio's direction was inverted; and a three-certificate library

Status: an interpretation error running from Finding 013 to Finding 022 is **corrected**. The
underlying numbers are unaffected; the verbal reading of the ratio flips, and two
conclusions flip with it. A third sound certificate is added and the library condition now
holds **better** than independence.
Reproduce: scripts/step47_rayleigh_bound.py, step48_three_certificate.py, step49_conditionals.py
Data: runs/rayleigh_bound.json, runs/three_certificate.json, runs/conditionals.json

## 1. The error

Since Finding 013 the quantity

    ratio  =  P(not A and not B) / ( P(not A) * P(not B) )

has been described as "above 1 means complementary, below 1 means redundant". **That is
backwards.** Take two cuts with f_A = f_B = 0.5 and look at the extremes:

| rule-out sets | P(not A and not B) | product of marginals | ratio |
|---|---|---|---|
| **identical** | 0.50 | 0.25 | **2.0** |
| independent | 0.25 | 0.25 | 1.0 |
| **disjoint** | 0.00 | 0.25 | **0.0** |

**Identical cuts give the maximum ratio.** The scale runs from 0 (perfectly complementary,
disjoint rule-outs) through 1 (independent) to 2 (identical). Higher means MORE redundant.

The check that exposes it takes one line and was never run: two cuts that rule out exactly
the same structures cannot be "complementary", and they produce the largest value.

## 2. What is unaffected

The damage is confined to the interpretation, not the measurements:

  * **Every conclusion resting on a CONDITIONAL stands**, because conditionals were computed
    directly. Finding 022's load-bearing number, f_B given not A = 0.53, is a conditional.
  * **Every conclusion resting on Spearman rho stands**, because rho is direction-free.
    Finding 021's effective dimension of 4.62 and its near-zero pairwise correlations are
    rank properties and are untouched.
  * Finding 014's asymptote, Finding 018's waterbed closed form, Finding 010's census: all
    unaffected.

## 3. What flips

| finding | stated | corrected |
|---|---|---|
| 013 | performance cuts at 0.821 are **redundant**, failures cluster | 0.821 is **below** 1, so they are weakly **complementary** |
| 015 | structural cuts at 1.111 **compose better** than performance cuts | 1.111 is **above** 1, so structural cuts are the **more redundant** family. The claim was backwards |
| 019 | value-value 0.827 redundant, topology-topology 1.133 complementary | the reverse: value cuts more complementary, topology cuts more redundant |
| 020 | "common-scalar redundancy" as a reason cuts fail to compose | the Spearman evidence stands; the ratio language flips |

So the performance axes were never the redundant family; they were mildly complementary. And
the "structural cuts compose better" headline of Finding 015 is withdrawn.

## 4. A third sound certificate: the time scale

Rayleigh's principle applied to the trial vector 1, which is admissible because K 1 = f:

    omega_1^2  <=  (sum of ground stiffnesses) / (sum of masses)

A requirement that the structure respond slowly, omega_1 <= omega_max, is refuted cheaply
whenever the ratio exceeds omega_max^2. Verified:

| check | value |
|---|---|
| structures tested | 300 |
| max ratio true omega_1^2 / bound | **0.998631** |
| **violations (ratio > 1)** | **0** |
| median tightness (bound / true) | 2.730 |
| rank correlation of the bound with n components | **-0.0064** |

Sound for every parameter assignment, O(n) to evaluate, keyed to the mass-to-stiffness ratio
rather than to the component count, and uncorrelated with the modal count.

## 5. Three certificates, composed

C1 modal (n < m), C2 statics (sag > delta_max), C3 time scale (ratio > omega_max^2), each
threshold at its own marginal median, 600 networks per space:

| n_max | f1 | **f2 given 1** | **f3 given 1,2** | remaining | product of marginals | ratio |
|---|---|---|---|---|---|---|
| 5 | 0.2517 | **0.5367** | **0.7596** | 0.0833 | 0.1871 | 0.4454 |
| 6 | 0.3883 | **0.5504** | **0.8061** | 0.0533 | 0.1529 | 0.3488 |
| 7 | 0.3400 | **0.5354** | **0.7772** | 0.0683 | 0.1650 | 0.4141 |
| 8 | 0.4217 | **0.5504** | **0.8013** | 0.0517 | 0.1446 | 0.3573 |

The conditionals are the quantity the library needs, and they are stable and large:

    f2 given 1      in [0.535, 0.550]
    f3 given 1,2    in [0.760, 0.806]

Each successive cut takes a **larger** fraction of what remains than the previous one, which
is exactly the signature of complementary cuts: the ratio is well below 1 at every size. The
three-certificate round leaves 5.2 to 8.3 percent of the space.

**Finding 022's caution was itself inverted.** It warned that 0.88 was "near independent, not
independent, so the correction compounds: 0.88^2 = 0.77 and worse with more members". With the
direction corrected, a ratio below 1 compounds in the **favourable** direction, and the third
cut takes 0.80 rather than decaying.

## 6. Library arithmetic

| n_max | per-round survival | rounds for N = 1e10 | certificates |
|---|---|---|---|
| 5 | 0.0833 | 9.3 | 28 |
| 6 | 0.0533 | 7.9 | 24 |
| 7 | 0.0683 | 8.6 | 26 |
| 8 | 0.0517 | 7.8 | 23 |

**About 24 sound certificates against 1e10 evaluations.** At the space sizes this ensemble
can actually reach the count is a handful against a few hundred, so the separation remains a
statement about growth; but the mechanism now has three sound members and its composition
ratio holds across four independent space sizes.

## 7. Limits

  * The direction error stood for ten rounds. The one-line check in section 1 should have been
    run when the ratio was introduced, and its absence is the same class of failure as the six
    identity traps already recorded: **a quantity was used before an extreme case was
    computed for it.**
  * Three certificates, four space sizes, 600 samples each, one seed per size.
  * All three thresholds sit at their own marginal medians, so each marginal cut is about half
    by construction. What the sweep shows is that the CONDITIONALS do not decay with space
    size, which is the property that matters; the absolute values are set by the calibration.
  * The third certificate is a loose bound, exceeding the true value by a factor of 2.73 at the
    median. A tighter bound would cut more.
  * One physical domain and one ensemble family.
  * No fourth certificate was tested, so whether the favourable compounding continues past
    three is unmeasured.
