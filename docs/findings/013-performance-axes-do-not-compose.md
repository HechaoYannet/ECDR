# Finding 013 - Performance axes do not compose independently

Status: composition across the three requirement axes is **partial, not independent**.
A methodological error in my own analysis was caught and corrected. The design
consequence is that independent coverage must come from STRUCTURAL features.
Code: ecdr/structure/capability.py. Reproduce: scripts/step23_composition.py, step24_calibration.py

## 1. The capability distribution is calibratable

Capability profiles over a random ensemble (600 structures, n uniform on 2..8,
log-uniform component values), requirement band f >= 30 Hz:

| quantity | p10 | median | p90 | spread p90/p10 |
|---|---|---|---|---|
| static deflection (mm) | 1.273 | 12.0 | 52.89 | 41.6 |
| peak abs T | 2.466 | 8.895 | 40.32 | 16.4 |
| in-band abs T | 0.009346 | 0.1892 | 2.114 | 226.2 |

All three are continuous and widely spread, so by Finding 012 each is calibratable.

## 2. An error in my own analysis, caught before it was reported

The first version of the composition test applied the three failure axes in sequence and
compared the product of the sequential survival ratios against the final survivor
fraction. It reported exact agreement and concluded the axes were independent.

**That agreement is an identity, not a measurement.** The sequential ratios telescope:

    (s1/N) * (s2/s1) * (s3/s2)  ==  s3/N     always, for any data

So the test could not have failed, whatever the ensemble. It was replaced with the
correct comparison: observed joint survival against the product of the **marginal**
survivals.

## 3. The corrected result: failures are positively correlated

At a calibration leaving 30 of 600 structures feasible (5 percent):

| step | constraint added | survivors | cut of remaining |
|---|---|---|---|
| 1 | sag | 246 | 0.590 |
| 2 | peak | 126 | 0.488 |
| 3 | in-band | 30 | 0.762 |

The cuts are all substantial, so the axes are **not nested** - each genuinely removes
structures the previous ones left. But:

| quantity | value |
|---|---|
| P(survive sag) | 0.4100 |
| P(survive peak) | 0.4700 |
| P(survive in-band) | 0.5933 |
| product of marginals | 0.1143 |
| observed joint survival | 0.0500 |
| **ratio observed / independent** | **0.4373** |

A ratio well below 1 means the FAILURES cluster: a structure that is bad on one axis
tends to be bad on the others. Composition gains **less than a factor of two** of what
independence would give.

## 4. Why, and what it implies

The three axes are all consequences of one underlying structural quality - a heavy,
softly supported, lightly damped structure is bad on all three at once. Different
PERFORMANCE metrics are therefore not different sources of information.

> **Independent coverage has to come from certificates targeting different STRUCTURAL
> FEATURES, not from different performance metrics.**

This is a direct constraint on how the certificate library must be built, and it is not
what a natural reading of "find several sound invariants" would suggest. Two invariants
that both measure, in effect, whether the support is stiff will compose to nothing
however different their proofs look.

## 5. The calibration window is narrow, and Finding 012's warning was observed

Sweeping the requirement tightness:

| scale | sag <= mm | peak <= | in-band <= | survivors | fraction |
|---|---|---|---|---|---|
| 4.00 | 32.00 | 32.00 | 1.200 | 319 | 0.5317 |
| 2.00 | 16.00 | 16.00 | 0.600 | 150 | 0.2500 |
| 1.00 | 8.00 | 8.00 | 0.300 | 30 | 0.0500 |
| 0.60 | 4.80 | 4.80 | 0.180 | **0** | 0.0000 |
| 0.25 | 2.00 | 2.00 | 0.075 | **0** | 0.0000 |
| 0.10 | 0.80 | 0.80 | 0.030 | **0** | 0.0000 |

Finding 012 section 6 warned that a mis-calibrated requirement makes coverage trivially 0
or 1 and that this is not fixable by choosing a better invariant. Here it happened: the
feasible set does not shrink gradually, it **vanishes abruptly** between scale 1.0 and
0.6 and stays empty. Step 23 had inadvertently landed at scale 0.25, where every structure
failed, and the composition there was walking toward an empty set - arithmetically correct
and completely uninformative.

**So calibration must be measured, not assumed, and the measurement must be reported.**

## 6. Honest scope

The three quantities measured here are requirement constraints evaluated directly from
the transfer function. **Evaluating a transfer function is exactly the expensive sampling
operation a certificate is supposed to avoid**, so none of them is a certificate. What
this finding establishes is a **precondition** for the certificate search:

  * the capability distribution is continuous and calibratable (so a certificate on these
    axes could in principle be tuned into the informative band);
  * but the three axes are correlated, so certificates found along them will not compose
    independently.

It does not establish that any certificate exists on any of these axes.

## 7. Next

  1. **Look for invariants keyed to distinct structural features** - for example the
     payload's own ground tie versus the absorber network versus the number of parallel
     ground paths - rather than to distinct performance metrics.
  2. **Report the independence ratio**, not just the sequential cuts, for every pair of
     candidate invariants. A pair with ratio near 1 is worth having; a pair near 0.4 is
     one certificate wearing two hats.
  3. **Fix the calibration first**, report the survivor fraction, and never measure
     composition in a regime where the feasible set is empty.

## 8. Limits

  * One ensemble family (random trees), one band edge, one batch of 600.
  * The independence ratio is a single number at a single calibration; it was not swept.
  * Positive correlation was demonstrated for these three axes and is not claimed to be
    universal.
