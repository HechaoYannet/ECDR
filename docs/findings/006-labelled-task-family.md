# Finding 006 - A labelled escape-task family with known ground truth

Status: built and verified. Code: ecdr/bench/. Reproduce:
.venv/Scripts/python.exe scripts/step9_task_family.py and scripts/step10_thresholds.py

This is the benchmark the objective calls for: a task family in which, for each
task, it is known WHICH mechanism class is the smallest one that can solve it, and
HOW that is known.

## 1. Family definition

Fixed across the family, varying only the band edge f_low:

    isolation   |T| <= 0.1 (-20 dB) for all f >= f_low
    peak        |T| <= 1.4125 (+3 dB) at all frequencies
    static sag  <= 1.0 mm
    actuator    |U/X_g| <= 2 * wn_min^2   (only binds on M3)

## 2. The two escape-depth thresholds

| transition | value | how |
|---|---|---|
| M1 -> M2 | **172.237063 Hz** | EXACT, from the certificate (Lambda crosses 1) |
| M2 -> M3 | **132.4253 Hz** | numerical, from 12,182 peak-feasible passive designs |

Three regimes:

    f_low <  132.43 Hz   depth 3   only the active mechanism escapes
    132.43 .. 172.24 Hz  depth 2   the passive chain suffices
    f_low >  172.24 Hz   depth 1   the initial passive SDOF already suffices

The M2 threshold came from a single scan.  For every peak-feasible design the whole
suffix-maximum curve of |T| is kept, and the running minimum

    G(omega_low) = min over designs of max over w >= omega_low of |T|

is accumulated.  M2 is feasible at a band edge exactly when G <= T_iso, so one pass
answers every band edge and the crossing is located by bisection.  The full curve is
in runs/thresholds.json.

## 3. The ladder as built

| f_low (Hz) | M1 | M2 | M3 | smallest solvable |
|---|---|---|---|---|
| 20 | proved infeasible | no witness | feasible | M3 |
| 40 | proved infeasible | no witness | feasible | M3 |
| 60 | proved infeasible | no witness | feasible | M3 |
| 80 | proved infeasible | no witness | feasible | M3 |
| 100 | proved infeasible | no witness | feasible | M3 |
| 120 | proved infeasible | no witness | feasible | M3 |
| 140 | proved infeasible | feasible | feasible | M2 |
| 160 | proved infeasible | feasible | feasible | M2 |
| 180 | feasible | feasible | feasible | M1 |
| 200 | feasible | feasible | feasible | M1 |
| 220 | feasible | feasible | feasible | M1 |

Every label carries its epistemic status.  M1 and M3 are decided by EXACT
procedures in both directions; M2 is only ever decided by a witness, and the absence
of one is recorded as no_witness_found, never as infeasible.  44688 designs were
examined for M2, of which 12182 are peak-feasible.

The M3 decision procedure is semi-analytic, which is why the family is cheap.  For
the sky-hook, omega_n = wn_min is optimal (a smaller omega_n raises r_low, lowering
both the in-band transmissibility and the actuator force), the band constraint
improves with damping while actuator force worsens with it, so the best admissible
design sits at the largest zeta the actuator budget allows.  Feasibility is then two
inequalities, and the whole family is decided exactly and instantly.

## 4. The baseline interface

ecdr/bench/problem.py adopts BOCoDe's canonical form exactly:

    evaluate(x) -> (obj, cons)          objective MAXIMISED, cons <= 0 feasible
    sample(n, seed)
    metadata()                          dim, param_names, bounds, constraints

and adds the two fields BOCoDe has no notion of:

    mechanism_class                     which design space x lives in
    evidence                            what is known about solvability, and how

Adopting the interface rather than reimplementing is what makes the strong baselines
comparable: same optimiser, same budget accounting, same problem object.  The only
thing that varies is the mechanism class, i.e. the inventory the agent may reach for.

## 5. Demonstrated: local refinement fails exactly where the certificate says it must

Running the identical differential-evolution budget inside each mechanism on the
depth-3 task at f_low = 60 Hz:

| mechanism | best in-band |T| found | peak/sag/force | verdict |
|---|---|---|---|---|
| M1 passive SDOF | 0.300455 | satisfied | fails the isolation target |
| M2 tuned mass damper | 0.211870 | satisfied | fails the isolation target |
| M3 sky-hook active | **0.048979** | satisfied | **meets the target** |

Two things to notice.  First, the local search inside M1 reports its *constraints*
as satisfied while never reaching the isolation target: a score-driven agent sees a
plausible design at 0.30 against a target of 0.1, which is a factor of three, not an
obvious impossibility.  The certificate says no amount of further search will help.
Second, the escape to M3 wins by a factor of six at the same budget.  That gap, on
tasks whose ground truth is known, is the quantity the headline experiment measures.

## 6. Deliberate asymmetry between the cheap signal and the sound signal

evaluate() scores on a 4000-point frequency grid because it is the agent inner loop
and must be cheap.  A grid can miss a sharp resonance - in Finding 004 one was
under-reported by a factor of 178386.  Therefore **evaluate() is not evidence of
feasibility**, and solve_within_mechanism reports a separate feasible_by_grid flag
rather than claiming verification.  Only the certificate (M1, M3) or an explicit
witness re-checked with the exact peak routine (M2) counts as evidence.  This is
integrity rule 5 of Finding 003, enforced by construction: the cheap path and the
sound path are different code.

## 7. Honest limits

  * The M2 threshold is numerical.  It is the best of 12182 scanned peak-feasible
    designs on a finite grid of dimensionless parameters; a design outside that grid
    could move it.  It is NOT a proof, and the registry says so.
  * Randomisation for the experiments has not been added yet: the family is
    deterministic in f_low.  A benchmark needs seeded variation in the constraints
    too, so that a method cannot be tuned to eleven fixed numbers.
  * L1 and L2 do not exist yet.  Everything here is L0, i.e. linear frequency-domain
    models.  The saturation, nonlinearity and perturbation the seed discussion asked
    for are not represented.
  * Cost accounting is evaluation counts, not the analytically defined simulator
    cost that SimulCost uses.  Alignment is still to do.
