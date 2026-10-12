# Finding 007 - Headline ablation: what the evidence actually supports

Status: experiment built and run (231 episodes). Result is **partial support with a
serious methodological caveat**, reported in full rather than trimmed to the good
part. Code: ecdr/agent/. Reproduce: scripts/step12_ablation.py then step12b_analyse.py

## 1. Design

Everything is held fixed except the abandonment signal:

  * the mechanism inventory and its order (M1 -> M2 -> M3)
  * the searcher: the same (mu+lambda) evolution strategy, same seeds
  * the total budget: 2500 objective evaluations, shared across mechanisms
  * the objective and constraints

11 tasks (band edges 20 to 220 Hz) x 7 arms x 3 seeds = 231 episodes.  Success is
decided by the EXACT peak routine, never by the grid the searcher optimises.

## 2. The metric had to be changed, and the reason matters

The obvious endpoint is escape rate.  It is CONFOUNDED here, and the oracle proves
it: an oracle knows which mechanisms can work, so it can never legitimately lose on
decision quality, yet it scores 66.7 percent escape against 90.9 percent for the
plateau heuristic.

The cause: on a depth-2 task the smallest feasible class is M2, but M3 also solves
it and is much easier to search.  An arm that WRONGLY abandons M2 lands on M3 and
succeeds.  A wrong decision is rewarded.

| arm | depth-2 escape | solved by |
|---|---|---|
| oracle | 0% | (nothing) |
| certificate_hybrid | 100% | M3 x6 |
| surrogate | 100% | M3 x6 |
| streak | 100% | M3 x6 |

So escape rate is replaced as the primary endpoint by **wasted budget**: evaluations
spent on mechanisms whose ground-truth label says they cannot work.  That isolates
the DECISION from the strength of the inner search, and the oracle reaches exactly
zero on it, which confirms the calibration.

## 3. Decision quality (median wasted evaluations, lower is better)

| arm | all | depth1 | depth2 | depth3 |
|---|---|---|---|---|
| never (pure local refinement) | 2512 | 0 | 2512 | 2512 |
| streak | 224 | 0 | 112 | 224 |
| plateau | 288 | 0 | 144 | 288 |
| surrogate | 352 | 0 | 184 | 352 |
| certificate_pure (no fallback) | 2512 | 0 | **0** | 2512 |
| **certificate_hybrid** | **176** | 0 | **0** | **176** |
| oracle | **0** | 0 | 0 | 0 |

## 4. What this supports, and what it does not

**Supported.** Where an infeasibility certificate exists, the certificate arm spends
**exactly zero** budget on the dead mechanism, at every depth, matching the oracle.
The hybrid beats every heuristic: 176 against 224 (streak), 288 (plateau), 352
(surrogate).

**Not supported, and this is the honest headline.** The margin over the best
heuristic is only **21 percent**.  That is far from the "certificates dominate"
story the thesis would like.  The reason is visible in the table: at depth 3 the
hybrid still wastes 176, essentially all of it on M2, for which no certificate
exists.  **The certificate's value is bounded by its coverage**, exactly as Finding
005 predicted, and right now its coverage is one mechanism class out of three.

**Also supported, negatively.** certificate_pure, which prunes on proof and never
otherwise, scores 2512 - identical to never escaping at all.  Sound pruning WITHOUT
a soft fallback is worthless on tasks whose intermediate class is uncertified.  This
is direct experimental confirmation of CORE's three-tier discipline: hard cores only
where certified, soft guidance everywhere else.

## 5. Two implementation errors, both understating the effect

Both were in the episode loop, and both charged budget to the certificate arm before
the certificate was allowed to act:

  1. the policy was consulted only AFTER a generation: 32 wasted evaluations
  2. then after constructing the searcher, whose initial population costs 16

Only after moving the check ahead of the searcher entirely did the measured waste
fall to its true value.  Worth stating plainly: each fix moved the result TOWARD the
hypothesis.  That is the direction in which a bug should be suspected, so both fixes
are documented rather than quietly applied, and the intermediate numbers are in the
git history.

## 6. The methodological warning, which generalises

**An escape-rate benchmark can reward the wrong decision when mechanisms differ in
how easy they are to search.**  Any comparison of "when to abandon a design route"
must therefore either equalise searchability across mechanisms, or report a
decision metric that is insensitive to it.  The oracle-reaches-zero check is the
cheapest available test that a benchmark is properly calibrated, and it should be
run before any escape-rate claim is made.

## 7. What must change before this is publishable

  1. **Strengthen the inner search.** It currently fails to solve feasible M2 on the
     depth-2 tasks (oracle 0 percent escape there), which is what creates the
     confound.  Until a feasible mechanism is reliably solvable within budget, the
     escape-rate endpoint cannot be used at all.
  2. **Widen certificate coverage.** The whole result rests on certificates existing.
     M2 has only necessary conditions, so the hybrid falls back to a heuristic for
     the one class where the task is hardest.  Finding 003 ranked closing M2 as the
     highest-value theoretical task; this experiment shows it is also the binding
     constraint on the empirical claim.
  3. **Randomise the constraints.** The family is deterministic in f_low, so eleven
     fixed numbers can be over-fitted.
  4. **Separate decision from search in the arm design.** A cleaner experiment gives
     every arm an ORACLE-GRADE inner search, so the only thing that can differ is
     the abandonment decision.
