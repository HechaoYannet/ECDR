# Finding 008 - The L1 rung, and the false-positive zone it opens

Status: L1 built and probed. The result resolves the degeneracy that made the L0
experiment inconclusive, and it does so quantitatively rather than rhetorically.
Code: ecdr/l1/. Reproduce: scripts/step14_l1.py, step15_l1_threshold.py,
step16_false_positive_zone.py

## 1. The design rule that makes the ladder load-bearing

Every L1 design must ALSO be a valid L0 design.  L1 only ADDS constraints.  It never
relaxes one, and it never changes what a mechanism is.  From that single property:

    L1 feasible  =>  L0 feasible
    contrapositive:  L0 infeasible  =>  L1 infeasible

So an infeasibility proof keeps its force at every fidelity ABOVE the one it was
derived at, while a witness at L0 says nothing at L1.  That asymmetry is exactly what
Finding 005 predicted from the literature - certificates prune soundly at every
level, certificates do not construct - and it is now a property of the code rather
than a claim about it.

What L1 adds:

  1. **Actuator bandwidth.**  An ideal sky-hook needs infinite-bandwidth force, which
     no actuator has.  L1 applies a first-order lag at corner omega_a:
     u = -c_sky * (omega_a / (s + omega_a)) * xdot, giving
     T(s) = k(s + omega_a) / [ (s^2 + k)(s + omega_a) + c_sky omega_a s ].
  2. **Parameter robustness.**  Band and peak constraints must hold across a relative
     perturbation box, not merely at nominal parameters.

Neither generalises the mechanism, which is why the transfer above is valid.

## 2. Verification

**Reduction check.**  As the actuator bandwidth grows, L1 must tend to L0:

| bandwidth (rad/s) | max abs difference from L0 |
|---|---|
| 1e2 | 8.29e-01 |
| 1e3 | 4.97e-02 |
| 1e4 | 4.95e-03 |
| 1e5 | 4.95e-04 |
| 1e6 | 4.95e-05 |

The error falls by exactly one decade per decade, i.e. it is O(1/omega_a), which is
what a first-order lag should give.

**Subset check, non-vacuous.**  3000 randomly sampled M1 designs on a task where M1
is L0-feasible (f_low = 220 Hz): 4 were L0-feasible and **0** were L1-feasible, and
L1 is a subset of L0.  On a task where M1 is provably L0-infeasible (f_low = 50 Hz),
both counts are zero, which is consistent but vacuous.

## 3. Actuator bandwidth does not close the escape

For the depth-3 task at f_low = 50 Hz, the best admissible lagged sky-hook:

| bandwidth (rad/s) | best in-band abs T | vs the 0.1 target |
|---|---|---|
| 3e2 | 0.069720 | meets it |
| 1e3 | 0.008992 | meets it |
| 3e3 and above | 0.00529 | meets it, converging to L0 |

So the escape to active control survives even an actuator whose corner sits at
300 rad/s, just below the band edge.  The ideal-sky-hook witness has roughly a factor
of 20 of margin.  **That is itself a finding: the passive designs near the feasibility
boundary are fragile and the active witness is robust** - the opposite of what a
reader might expect.

## 4. Robustness moves the passive threshold a long way

| requirement | passive-SDOF threshold | shift vs L0 |
|---|---|---|
| L0 (no perturbation) | **172.34 Hz** (exact) | - |
| L1, plus or minus 5 percent | 203.10 Hz | +30.76 Hz |
| L1, plus or minus 10 percent | ~~239.72 Hz~~ **258.76 Hz** | **+86.42 Hz** |

Requiring a design to hold across a 10 percent parameter perturbation moves the
threshold by 39 percent.  The L0-feasible designs near the boundary are therefore
**model artefacts**: they satisfy the equations and not the engineering requirement.

## 5. The false-positive zone, which is the point

For 172.34 < f_low < 239.72 Hz the L0 certificate declares M1 FEASIBLE and no design
survives a 10 percent perturbation.  Measured, monotonically:

| f_low | L0 certificate | L1 robust margin | relation |
|---|---|---|---|
| 160 Hz | infeasible | none admissible | agree: infeasible |
| 180 Hz | FEASIBLE | +0.1411 violated | L0 says yes, L1 says no |
| 200 Hz | FEASIBLE | +0.0783 violated | L0 says yes, L1 says no |
| 220 Hz | FEASIBLE | +0.0236 violated | L0 says yes, L1 says no |
| 240 Hz | FEASIBLE | +0.0101 violated | L0 says yes, L1 says no |
| 260 Hz | FEASIBLE | -0.0176 ok | agree: feasible |
| 300 Hz | FEASIBLE | -0.0499 ok | agree: feasible |

## 6. Why this matters more than the numbers

The L0 experiment was inconclusive for a structural reason: at L0 the certifier can
decide M1 AND M3 exactly, so the design problem collapses to "ask the certifier" and
the ablation measured very little.  The false-positive zone removes that degeneracy
in the right way:

  * the certificate is still **sound for pruning** - L0-infeasible implies
    L1-infeasible at every level, so hard pruning remains legitimate
  * the certificate's **feasibility verdict no longer holds**, so it cannot construct
    a witness and the agent must still search

That is precisely the regime where "when should the agent abandon this mechanism?"
becomes a real question with a real cost, and it is where the headline ablation
should be re-run.

It also produces the sharpest task in the family: an agent that trusts the L0
certificate delivers a design that passes every L0 check and fails under any
perturbation.  That failure is silent, checkable, and exactly the kind of thing the
seed discussion called out - here it is the reverse of the expected direction, a
**false positive** rather than a false negative.

## 7. Honest limits

  * The perturbation model is a plus-or-minus 10 percent independent multiplicative
    box.  It is a design choice, not derived from hardware.  A real stage would have
    correlated, structured uncertainty.
  * The L1 threshold 239.72 Hz is NUMERICAL: it is the best over a sampled grid of
    designs and 12 perturbation samples per design.  Only the L0 threshold 172.34 Hz
    is exact.
  * L2 does not exist yet.  Independence is the whole point of L2 and it requires a
    different toolchain, not a different setting of the same one.
  * Saturation is present only as the actuator force-per-displacement budget
    inherited from L0, not as a time-domain nonlinearity.
