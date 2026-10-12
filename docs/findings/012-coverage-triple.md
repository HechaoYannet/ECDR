# Finding 012 - Coverage is a property of the triple, and continuity is what matters

Status: Finding 011's "shape is a property of the predicate" is **corrected**. The
practical rule is now sharper and, importantly, **easier to satisfy** than 011 implied.
Code: ecdr/structure/network.py, ecdr/structure/ensemble.py.
Reproduce: scripts/step21_network_verify.py, scripts/step22_coverage_ensemble.py

## 1. A general evaluator, verified before use

ecdr/structure/network.py turns ANY structure in the graph space into a linear mechanical
network and evaluates it:

    M x'' + C x' + K x = f x_g + g x_g',   T(s) = e_0^T (M s^2 + C s + K)^{-1} (f + g s)

Verified against the hand-written L0 mechanisms before anything was built on it:

| check | result |
|---|---|
| M1 transmissibility, max abs difference | 4.97e-16 |
| M2 transmissibility, max abs difference | 0.0 |
| M1 static deflection | exact to 0.0 |
| M2 static deflection | exact to 0.0 |

## 2. The correction to Finding 011

011 claimed robustness is a property of the predicate **shape**. That is incomplete.
Coverage also depends on how structures are **distributed**. Two ensembles were drawn that
differ ONLY in how the number of components is drawn:

| ensemble | static deflection median | distinct deflection values | mode counts |
|---|---|---|---|
| n uniform on 2..8 | 13.05 mm | 3000 of 3000 | spread over 2..8 |
| n fixed at 8 | 31.17 mm | 3000 of 3000 | **8 for all 3000** |

## 3. Continuous bound vs discrete bound

**B1, static deflection - a CONTINUOUS bound.** The invariant is sound (payload sag under
gravity; pure statics). Coverage against the requirement:

| delta_max (mm) | 0.5 | 1.0 | 2.0 | 5.0 | 10.0 | 20.0 | 50.0 |
|---|---|---|---|---|---|---|---|
| spread ensemble | 0.9713 | 0.9290 | 0.8593 | 0.7237 | 0.5740 | 0.3843 | 0.1377 |
| concentrated | 1.0000 | 0.9960 | 0.9747 | 0.9070 | 0.8117 | 0.6453 | 0.3337 |

Coverage sweeps **continuously through (0, 1) in both ensembles**.

**B2, mode count - a DISCRETE bound.** Over the same requirement grid:

| m | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|
| spread ensemble | 0.1493 | 0.2870 | 0.4317 | 0.5763 | 0.7210 | 0.8573 |
| concentrated | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

Same invariant, same grid. In the concentrated ensemble the coverage is 0 everywhere and
would jump to 1 at m = 9. **Nothing in between is reachable.**

## 4. The rule that replaces 011's

> **Prefer invariants whose bound is a CONTINUOUS physical quantity.**

A continuous bound has a coverage that varies continuously with the requirement, so it is
always calibratable. A discrete or combinatorial bound has a coverage that jumps unless the
ensemble happens to spread that discrete attribute, which is a fragile coincidence.

**This is a relaxation, not a tightening.** Physical bounds - sag, bandwidth, time
constant, energy, settling time - are naturally continuous. Finding 011 was pessimistic
because it was looking at combinatorial predicates (counts of nodes, counts of ground
paths), which is exactly where discreteness lives. The problem was the choice of bound,
not the method.

It also re-reads Finding 010 correctly: mode counting failed **not because it was not
scale-free** but because its bound is a small integer. The census measured the symptom.

## 5. The first invariant that passes on shape

The static-deflection bound is the first candidate that satisfies everything checked so far:

| requirement | status |
|---|---|
| sound | yes - statics, no dynamics, no assumption beyond linear springs and equilibrium |
| class-level | yes - any topology, any number of components |
| domain tag | linear springs, static equilibrium, gravity; crossed by any nonlinear or preloaded support |
| cost c_p | O(n^3) for one solve, independent of the SIZE OF THE FAMILY it rules out |
| bound continuous | yes |
| names a remedy | yes - increase the static stiffness of the ground path |

## 6. The honest limit: calibration is not free

Coverage being *tunable* by choosing the requirement is nearly circular. **In a real
problem the requirement is given.** The question that actually matters is:

> Given the problem's requirement, does the ensemble's capability distribution put that
> requirement in the marginal region?

If the requirement is far above what every structure can do, coverage is 1 and the answer
is trivially "impossible". If far below, coverage is 0 and the certificate never fires.
**Neither is informative, and neither is fixable by choosing a better invariant.**

So calibration is a constraint on the BENCHMARK, not on the certificate layer, and it must
be checked when the benchmark is chosen rather than discovered after the fact. The
deflection numbers above show the effect plainly: the same invariant gives coverage 0.93
or 0.14 depending only on where the requirement is placed, and the two ensembles differ by
a factor of two in the median sag for no reason other than the component-value scales.

## 7. What this changes about the next step

The critical path is no longer "find a scale-free predicate". It is:

  1. **collect sound invariants with continuous bounds** - the deflection bound is one;
     achievable-bandwidth, time-constant and energy bounds are the next candidates;
  2. **check they compose**: after the first cuts a fraction, the second must cut a
     constant fraction of what REMAINS. Two invariants that both essentially measure sag
     will not compose;
  3. **fix the benchmark so the requirement lands in the marginal region**, and report
     where it lands rather than assuming.

## 8. Limits

  * The static-deflection invariant is shallow. It is a statics constraint and says nothing
    about dynamics, which is where the interesting capability gaps live. Its value here is
    that it is a fully worked specimen of the right SHAPE, not that it is deep.
  * The ensembles are random trees with log-uniform component values. They are physically
    plausible but arbitrary, and the absolute coverage numbers depend on those scales.
  * Only two bounds were measured. The continuous-vs-discrete claim is supported by one
    example of each and should be checked against the remaining candidate families.
