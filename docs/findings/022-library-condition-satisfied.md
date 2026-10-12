# Finding 022 - The library condition is satisfied, and calibration is what binds

Status: the first pair of sound certificates that satisfies Finding 011's composition
condition, tested across four space sizes. The binding constraint is the requirement's
calibration, not the certificates.
Reproduce: scripts/step46_library_composition.py.  Data: runs/library_composition.json

## 1. What was tested

Finding 021 established that the modal bound and a performance bound are weakly correlated.
Correlation is necessary but not sufficient. Finding 011 needs, for a sequence of
certificates,

    certificate i rules out a fraction f_i of the space REMAINING after 1..i-1
    and every f_i stays bounded away from zero

so the test is conditional, and it has to be swept over space size, because Finding 010
showed a resource-bound predicate covering a vanishing fraction when the requirement is
held fixed while the space grows.

Two **sound** certificates, both cheap and both holding for every parameter assignment:

| | statement | basis |
|---|---|---|
| **A modal** | a structure with n degrees of freedom has a free response of at most n harmonics, so a requirement needing m independent frequencies rules out every n < m | linear algebra |
| **B statics** | the payload sag under gravity must not exceed delta_max | equilibrium |

500 networks per space, n uniform on 2..n_max, n_max in {5, 6, 7, 8}.

## 2. The result, with the requirement calibrated

| n_max | m | f_A | f_B marginal | **f_B given not A** | product of marginals | observed joint | **ratio** |
|---|---|---|---|---|---|---|---|
| 5 | 3 | 0.2460 | 0.5000 | **0.5252** | 0.3770 | 0.3580 | **0.9496** |
| 6 | 4 | 0.3840 | 0.5000 | **0.5584** | 0.3080 | 0.2720 | **0.8831** |
| 7 | 4 | 0.3360 | 0.5000 | **0.5361** | 0.3320 | 0.3080 | **0.9277** |
| 8 | 5 | 0.4260 | 0.5000 | **0.5540** | 0.2870 | 0.2560 | **0.8920** |

  * **f_B given not A stays at 0.525 to 0.558 across every space size.** The second cut
    does take a constant fraction of what the first left.
  * **The independence ratio stays above 0.88.** The two cuts are close to independent -
    the second is not re-cutting what the first already removed.

## 3. An identity caught before it was reported

The first version of this table showed a column "product (1-f_A)(1-f_B)" and a column
"observed remaining fraction", and they matched to four decimal places. They match **by
construction**: f_B is defined as P(B | not A), so (1-f_A)(1-f_B) IS P(not A and not B).
The column could not have disagreed, and it was replaced by the product of the MARGINALS.

This is the same failure mode as Finding 013's telescoping ratio, and it is the sixth time
in this project that a check was written which could not fail. The pattern is now routine
enough that any column comparing two quantities should be checked for algebraic identity
before it is read.

## 4. With the requirement FIXED, the modal cut decays

| n_max | 5 | 6 | 7 | 8 |
|---|---|---|---|---|
| median n | 3.5 | 4.0 | 4.0 | 5.0 |
| **f_A, m = 4 fixed** | 0.5000 | 0.3840 | 0.3360 | 0.2740 |
| f_A, m calibrated | 0.2460 | 0.3840 | 0.3360 | 0.4260 |

Under a fixed requirement the ruled-out set is {n < m} and the space is uniform on
2..n_max, so f_A falls off as 2/(n_max-1), i.e. as 1/n_max. **It does not collapse over the
range tested but it does go to zero**, which is Finding 010's mechanism operating slowly
rather than abruptly.

**This is the third time the same lesson has appeared** - Finding 012 (coverage is a triple
property), Finding 021 section 6 (mode counting is eliminated only when the requirement is
fixed), and now here, measured directly.

> **Coverage is controlled by the requirement's position in the distribution, not by the
> certificate. Calibration is a benchmark-design obligation.**

## 5. The library arithmetic

Per-pair survival is (1-f_A)(1-f_B) = 0.358 at n_max = 5 and 0.256 at n_max = 8, so

    k pairs  =  log N / log( 1 / ((1-f_A)(1-f_B)) )

| N | pairs needed | certificates | evaluations for exhaustive sampling |
|---|---|---|---|
| 500 | 4.6 to 6.1 | 9 to 12 | 500 |
| 1e6 | 10.1 to 10.6 | 20 to 21 | 1,000,000 |
| 1e10 | 16.9 to 17.8 | 34 to 36 | 10,000,000,000 |

At the space sizes tested the separation is modest - a dozen certificates against five
hundred evaluations. **The separation is a statement about growth, and it only becomes
large at sizes this ensemble cannot reach.** That is the arithmetic working; it is not a
demonstration of a large practical advantage.

## 6. What this does and does not establish

**Does:** a sequence of two sound, cheap, class-level certificates can satisfy Finding 011's
composition condition, at four independent space sizes, with the second cut taking a
constant fraction of what the first left and the two being close to independent.

**Does not:**
  * the certificates here are the modal bound and the static-equilibrium bound. **Neither is
    a new result** - both are elementary. What is new is that they compose;
  * k grows like log N, so the advantage is invisible at N = 500. No claim is made that any
    practical problem is large enough for it to matter;
  * the independence ratio of 0.88 to 0.95 is **near** independent, not independent. Two
    more such pairs would leave 0.88^2 = 0.77 of the product, and the decay compounds;
  * one ensemble family, one physical domain, and calibration performed by placing the
    requirement at the median. Whether a **given** engineering requirement lands near the
    median is exactly the M6 question and is untested.

## 7. Limits

  * Four space sizes, 500 samples each, one seed per size. The f_B trend is flat but the
    four points do not establish a limit.
  * The static-equilibrium certificate was calibrated at the median sag, which cuts exactly
    half by construction. f_B near 0.5 is therefore partly a consequence of that choice,
    and a differently calibrated requirement would move it. What the sweep shows is that it
    does not DECAY with space size, which is the property that matters.
  * The modal certificate's m was set at the median n, which likewise fixes f_A near 0.35.
  * No third certificate was tested, so the compounding of near-independence is unmeasured.
