# Finding 029 - The L1 labels inherit the sampling defect, and the zone was measured at the wrong radius

Status: MechanismProblemL1 and verify_l1 sampled the perturbation box exactly as
robust_violation did. **33 designs certified robust across the task sweep actually fail** -
6 of 7 at one setting. Both now take **use_corners=True**. Two further corrections fall out:
the task stratification moves, and the L1 ablation turns out to have been run at a
different perturbation radius from the zone it claims to measure.
Reproduce: scripts/step57_l1_labels_corrected.py.  Data: runs/l1_labels_corrected.json

## 1. The defect, second instance

Finding 028 found that robust_violation drew n random points in a perturbation box and
returned their maximum - a LOWER bound on the true worst case. MechanismProblemL1 built its
perturbation directions the same way

    self._dirs = 1.0 + rel * (2.0 * np.random.default_rng(12345 + seed).random(
        (n_pert, self.dim)) - 1.0)

and verify_l1 drew n_pert fresh random directions per call. **So every L1 label in the
project inherits the same optimism**, including the feasibility labels of the L1 ablation at
step 17 and the "M1 = Y at 240 Hz" row of Finding 008.

Both now accept **use_corners=True**, evaluating the 2^d corners of the box. That is exact
under monotonicity and costs at most 8 points for the three-parameter lagged sky-hook and 32
for the five-parameter tuned mass damper. The sampled path is kept so the original results
stay reproducible.

## 2. How bad it is

M1 swept over 2400 designs per task, six task frequencies, two perturbation radii:

| f_low | rel | sampled ok | corners ok | **FALSE ROBUST** |
|---|---|---|---|---|
| 150 | 0.06 | 0 | 0 | 0 |
| 150 | 0.10 | 0 | 0 | 0 |
| 180 | 0.06 | 0 | 0 | 0 |
| 180 | 0.10 | 0 | 0 | 0 |
| 210 | 0.06 | 0 | 0 | 0 |
| 210 | 0.10 | 0 | 0 | 0 |
| **240** | **0.06** | 4 | 3 | **1** |
| 240 | 0.10 | 0 | 0 | 0 |
| 280 | 0.06 | 24 | 21 | 3 |
| **280** | **0.10** | **7** | **1** | **6** |
| 320 | 0.06 | 60 | 52 | 8 |
| **320** | **0.10** | **28** | **13** | **15** |

**33 false-robust designs in total.** At f_low = 280 Hz and rel = 0.10 the sampled test
certifies 7 designs and **6 of them fail the corner test** - an 86 percent false
certification rate. The rate grows with the perturbation radius and near the feasibility
boundary, which is exactly where the L1 conclusions live.

## 3. The task stratification moves

The corrected zone at rel = 0.10 is 172.34 to 258.76 Hz, so

| band | tasks |
|---|---|
| below the zone | 150 |
| **inside the zone** | **180, 210, 240** |
| above the zone | 280, 320 |

**step 17 stratified by 172.34 to 239.72, which put 240 Hz ABOVE the zone.** Under the
corrected boundary it is inside it. The published stratification of the L1 ablation is
therefore wrong by one task: "in zone" gains 240 Hz and "above zone" loses it.

## 4. And a conceptual error, not a bug

This is the more serious of the two, because no fix to the code addresses it.

**The false-positive zone is a statement at rel = 0.10.** It says: the L0 certificate calls
M1 feasible, but no design survives a plus-or-minus 10 percent perturbation.

**The L1 ablation at step 17 ran its tasks at rel = 0.06.** Look at the table in section 2:
at 240 Hz, rel = 0.06 admits 3 corner-robust designs while rel = 0.10 admits **none**. The
two settings give different feasibility verdicts at the same frequency.

> **So the ablation was not measuring the zone it claimed to measure.** Its labels correspond
> to a 6 percent robustness requirement; the zone is drawn at 10 percent. A task cannot be
> "inside the false-positive zone" and simultaneously have a feasible design, and at 240 Hz
> that is exactly the situation the two settings produce.

The fix is to choose one radius and use it everywhere. It has not been chosen yet, and the
choice matters: 0.06 keeps M1 alive at 240 Hz and 0.10 kills it.

## 5. What is affected

  * Finding 008's "M1 = Y at 240 Hz" row, and the stratification of step 17.
  * Any L1 label in step 17's ablation table, since all were produced at rel = 0.06 with
    sampled directions.
  * The claim in Finding 008 that the active mechanism escapes with "a factor of 20 of
    margin" - that number came from verify_l1's sampled worst case.

**Not affected**: the L0 certificate, exact and sampling-free. The certificate-transfer
property, which is a statement about constraint sets rather than about how a worst case is
computed. The L1 closed forms, confirmed in Finding 027 by simulation. Findings 010 to 026.

## 6. What was not done

**The L1 ablation was not re-run.** Step 17's 126 episodes, its labels and its stratified
table stand as published but are now known to rest on an unreliable inner test and a
mismatched radius. Re-running it is the next step and needs a decision first: at which
perturbation radius.

## 7. Limits

  * The corner argument is exact only under monotonicity, verified here by agreement with a
    dense search but not proved. For the five-parameter tuned mass damper it was not checked
    against a dense search at all.
  * The design grid is 2400 M1 designs per setting, not a continuous search, so the counts
    are lower bounds on the number of false certifications.
  * Only M1 was swept. The lagged sky-hook and the tuned mass damper were not.
  * The radius question in section 4 is raised but not resolved; no evidence is offered for
    which radius is the right engineering choice.
