# Finding 032 - Linearization makes L2-Modelica exact and fast; and an ideal constraint silently breaks it

Status: the transient route of Finding 031 needed thousands of excitation periods per point
and was unusable for an ensemble. **Linearization replaces it** - exact, instant, and matching
L0 across three decades to 2.3e-05.  Getting there required finding that an ideal position
constraint makes omc dump a **silently wrong** linearization whose transfer function is 1 at
every frequency.
Reproduce: scripts/step61_linearize_check.py.  Data: runs/linearize_check.json

## 1. Why linearization

Finding 031 showed the emitted model is correct but that the time-domain route needs the
transient to decay: on a lightly damped structure the ratio walked 3.72 -> 1.72 -> 1.02 ->
0.999776 as the run was extended from 40 to 1080 excitation periods, and reaching 1e-06
would have needed roughly 5000 periods - nearly six minutes per comparison, which cannot be
swept over an ensemble.

omc can **linearize** a model and dump the state space.  The frequency response then follows
algebraically, with no settling time.  The model stays equation-free, so the modelling check
is preserved; only the way the answer is extracted changes.

## 2. The first attempt is wrong, and looks fine

With the ideal position source - `Position(exact = true)`, which imposes
`flange.s = s_ref` as a constraint - the dump is

    n = 2,  A = [0, 1; -9806.94, -107.47],  B = [0; 0],  C = [1, 0],  D = [1]

The states omc chose are the damper's **relative** coordinates, and in those coordinates the
input enters through its second derivative:

    x1' = x2          x2' = -(k/m) x1 - (c/m) x2 - u''

so a state space of the form x' = A x + B u **cannot represent it**, and omc leaves B at
zero rather than refusing.  The declared output `y = x1 + u` is right; the dynamics are
not, and nothing in the dump says so.  The transfer function comes out as D = 1 at every
frequency:

| omega | L0 abs T | linearized | ratio |
|---|---|---|---|
| 10 | 1.0101777924 | 1.0000000000 | 0.98992475 |
| 62.8319 | 1.3318510554 | 1.0000000000 | 0.75083471 |
| 300 | 3.8989111415e-01 | 1.0000000000 | 2.56481865 |
| 1000 | 1.0834643605e-01 | 1.0000000000 | 9.22965292 |

**T identically 1 is a plausible-looking answer** - it is what an ideal isolator with no
dynamics would give, and 0.99 at the lowest frequency is nearly right. **Accepting this dump
would have silently corrupted every L2-Modelica conclusion from here on.** The check that
caught it was comparing at a frequency where T is nowhere near 1.

## 3. The fix

MSL's `Position` has an `exact` flag and, when false, a second-order **Bessel**
filter with critical frequency `f_crit` (its Bessel coefficients `af` and `bf` are
protected constants).  With `exact = false` the input enters through STATES, so the
linearization can represent it:

    n = 4
    A = [ 0, 1, 0, 0;
         -9806.94, -107.47, 6.388e11, 1.384e6;
          0, 0, 0, 1;
          0, 0, -6.388e11, -1.384e6 ]
    B = [0; -6.388e11; 0; 6.388e11]
    C = [1, 0, 1, 0]
    D = [0]

The two extra states are the ground filter.  `C = [1, 0, 1, 0]` says the payload is the
relative displacement **plus** the ground displacement, which is the physics.

## 4. The result

`f_crit = 1e5` Hz, far above the band of interest, so the filter is unity to better than
1e-08 there:

| omega | L0 abs T | linearized | ratio |
|---|---|---|---|
| 10 | 1.0101777924 | 1.0101777872 | **0.99999999** |
| 62.8319 | 1.3318510554 | 1.3318428986 | **0.99999388** |
| 300 | 3.8989111415e-01 | 3.8989852542e-01 | **1.00001901** |
| 1000 | 1.0834643605e-01 | 1.0834896374e-01 | **1.00002333** |

**median error 1.257e-05, worst 2.333e-05 across three decades**, with no settling time and
no integration.

The residual grows with frequency, as expected: the Bessel filter's deviation from unity
scales as (w / w_crit)^2.

## 5. What this changes

**L2-Modelica becomes sweepable.** The time-domain route cost thousands of periods per
comparison; this costs one compile and no simulation time. The ensemble cross-validation that
Finding 031 could not run - and the re-run of Finding 027's twelve L1 comparisons through
Modelica, which is the modelling-independence check the project has been building toward -
are now affordable.

**And a hazard is recorded.** Any user of `linearize` on a model with an ideal position,
velocity or acceleration constraint will get B = 0 and a plausible wrong answer. The
constraint must be replaced by a filter, or the state space must be augmented by hand.

## 6. Limits

  * The filter is not removed, only pushed out of band. The residual 2.3e-05 at omega = 1000
    is the filter, not an error in the model; a wider band or a higher f_crit would be needed
    to separate them.
  * Tested on the SDOF only. The general emitter still needs to be re-run through
    linearization, and the four-state structure will differ for networks with more ground ties.
  * `f_crit = 1e5` Hz makes the filter poles very fast. That is harmless for a
    linearization, which does no integration, but it would make a time-domain simulation of
    the same model stiff.
  * The re-run of Finding 027 and the ensemble sweep are NOT done here.
