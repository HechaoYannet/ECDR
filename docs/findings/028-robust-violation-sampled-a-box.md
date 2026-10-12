# Finding 028 - robust_violation sampled a box and called it the worst case

Status: a defect in the production code, not in a test. Finding 008's robustness threshold
is **understated by 19 Hz** and its false-positive zone is **28 percent wider** than reported.
The corrected threshold is 258.76 Hz.
Reproduce: scripts/step55_robust_sampling.py, step56_robust_corners.py.
Data: runs/robust_sampling_check.json, runs/robust_corners.json

## 1. The defect

ecdr/l1/models.py computed the robust worst case by drawing n random points in a relative
box and taking the MAXIMUM violation over them:

    def robust_violation(mech, params, task, omega, rel=0.10, n=24, seed=0):
        for p in perturbed(mech, params, rel, n=n, seed=seed):
            ... worst = max(worst, ...)

**A maximum over samples is a LOWER bound on the maximum over the box.** A design can
therefore be certified robust while some un-sampled point in the box violates - and the
certification is wrong in the direction that matters.

step15 called it with **n = 12** for the plus-or-minus 10 percent case, and Finding 008's
false-positive zone was built on the result.

## 2. The test, and the direction was known in advance

If the sampled maximum understates the truth, then designs the sampling accepts must fail a
better search, and the true threshold must be HIGHER than 239.72 Hz. **The direction of the
error was predictable before the test was run**, which is what makes the test decisive.

| f_low | 12 draws | corners | difference |
|---|---|---|---|
| 250 | **-5.64266e-03** | **+1.56637e-02** | 2.13e-02 |
| 270 | **-5.64266e-03** | **+5.63045e-03** | 1.13e-02 |
| 300 | **-5.64266e-03** | **+5.63045e-03** | 1.13e-02 |

**Three of three designs the sampling certified as robust actually violate the box**, by
5.6e-03 to 1.6e-02.

## 3. The worst case is a CORNER, which makes the fix exact

| f_low | worst point | nominal |
|---|---|---|
| 250 | omega_n = 121.56111, zeta = 0.65506 | (110.51010, 0.59551) |
| 270 | omega_n = 121.56111, zeta = 0.53596 | (110.51010, 0.59551) |

121.56111 = 110.51010 x 1.1, 0.65506 = 0.59551 x 1.1, 0.53596 = 0.59551 x 0.9. **The worst
case sits exactly on a corner of the box.** A relative box has 2^d corners - four for two
parameters - and the constraints (band attenuation, peak, static deflection, actuator force)
are monotone in the parameters, so the extremes live there.

**Random sampling is the wrong instrument, and the corners are not a heuristic but the
candidate set.** ecdr/l1/models.py now provides robust_violation_corners; the old function
is kept and marked DEPRECATED for certification, so the original results stay reproducible.

## 4. The corrected numbers

| requirement | threshold |
|---|---|
| L0 certificate | 172.34 Hz |
| L1 plus-or-minus 10 percent, 12 draws (as reported) | 239.72 Hz |
| **L1 plus-or-minus 10 percent, corners** | **258.76 Hz** |

| | false-positive zone | width |
|---|---|---|
| as reported in Finding 008 | 172.34 to 239.72 Hz | 67.4 Hz |
| **corrected** | **172.34 to 258.76 Hz** | **86.4 Hz** |

**The zone is 19.04 Hz wider, a 28 percent increase.** The qualitative conclusion of
Finding 008 is unchanged and in fact strengthened - robustness moves the threshold a long
way and the fidelity ladder is load-bearing rather than decorative - but the number is not
239.72.

## 5. An error in my own test, caught before it was reported

The first run of step 55 reported a worst point of **omega_n = 400, zeta = 2.0** for a
nominal of (110.51, 0.596). Those are the mechanism's hard parameter bounds, not the
plus-or-minus 10 percent box, whose corners are (121.56, 0.655) and (99.46, 0.536).

The refinement step clipped to the GLOBAL bounds rather than the box, so it walked out of
the box and reported an out-of-box point as the worst case. With the clip corrected the
worst point moved onto the corner, and an assertion now rejects any refinement that leaves
the box.

**This is the seventh time in this project that a number was produced in a regime where it
does not mean what it says** - after six identity traps, an inverted independence ratio, and
a silent integration failure. The difference here is that the defect is in the PRODUCTION
code rather than in a check, so none of my own tests would have caught it; it took a
different instrument to expose it.

## 6. What is affected and what is not

**Affected**: Finding 008's threshold and zone width. Any later conclusion quoting 239.72 Hz.
The L1 ablation of step 17, which stratified tasks by the 172.34 to 239.72 boundary and
therefore placed the 240 Hz task at the edge rather than inside the zone.

**Not affected**: the L0 certificate at 172.34 Hz, which is exact and uses no sampling. The
certificate-transfer property. The L1 hand-derived closed forms, confirmed in Finding 027.
Findings 010 to 025, which do not use robust_violation.

## 7. Limits

  * The corrected threshold is still numerical - it is the best over a sampled grid of
    designs, now with an exact inner test. A descent over the design space would do better.
  * Corners are exact only under monotonicity, which was verified here by a dense search
    agreeing with the corner value but was not PROVED. If a constraint were non-monotone the
    corner would not suffice and a genuine box optimisation would be needed.
  * Two parameters, so four corners. In higher dimensions 2^d grows quickly, though the
    argument stays exact under monotonicity.
  * The L1 ablation at step 17 was not re-run against the corrected boundary.
