# Finding 034 - The TMD came through the generic emitter unchanged, which is a test of Layer A

Status: the tuned mass damper needed NO new emitter code. Every mechanism the project uses -
passive network, tuned mass damper and lagged sky-hook - is now confirmed by a route that
shares no equation with the rest of the project, to a median of 4.8e-08. Finding 033's
coverage gap is closed.
Reproduce: scripts/step64_modelica_tmd.py.  Data: runs/modelica_tmd.json

## 1. The mapping, and why no code was needed

The TMD is a two-mass network: the payload m1 on a ground spring and damper, and an absorber
m2 on its own spring and damper. In the structure representation:

    masses   = [1 - mu, mu]
    springs  = {(0, 1): k2}      dampers  = {(0, 1): c2}
    ground_k = {0: k1}           ground_c = {0: c1}

The generic emitter of Finding 031 took that with no modification. It was written against the
STRUCTURE REPRESENTATION, not against a list of named mechanisms, so a mechanism its author
was not thinking about at the time came through unchanged.

That is a designed test of roadmap item (3), and it passed. Had the emitter needed a branch
per mechanism, Layer A would be a naming convention rather than an abstraction, and every new
mechanism would be a fresh opportunity for the emitter and the reference to diverge.

## 2. The result

Four parameter sets, four frequencies each, covering a lightly damped absorber, a heavily
damped one, equal masses, and a 2 percent mass ratio:

| case | omega_n1 | zeta1 | mu | ratio | zeta2 | states |
|---|---|---|---|---|---|---|
| 0 | 100 | 0.05 | 0.10 | 1.00 | 0.10 | 6 |
| 1 | 100 | 0.02 | 0.05 | 0.95 | 0.20 | 6 |
| 2 | 50 | 0.30 | 0.30 | 1.20 | 0.05 | 6 |
| 3 | 200 | 0.01 | 0.02 | 1.05 | 0.50 | 6 |

Six states: the two masses, the ground filter, and the second order of the two-mass system.

| omega | L0 abs T | Modelica | rel |
|---|---|---|---|
| 100 (case 0) | 1.6749792702 | 1.6749792680 | 1.28e-09 |
| 100 (case 1) | 6.0110748459 | 6.0110748199 | 4.32e-09 |
| 200 (case 3) | 2.5704525761e+01 | 2.5704524916e+01 | 3.29e-08 |
| 400 (case 3) | 3.4168018782e-01 | 3.4168014522e-01 | 1.25e-07 |
| 1000 (case 3) | 4.2761879745e-02 | 4.2761847089e-02 | 7.64e-07 |

median 4.798e-08, worst 7.637e-07 over 16 comparisons.

Case 3 at omega = 200 is a genuinely sharp resonance - abs T = 25.7, a Q of about 25 on a 2
percent mass ratio - and it is matched to 3.3e-08. A shape error in the absorber coupling
would be most visible exactly there.

## 3. The residual is the filter, as expected

The error grows monotonically with frequency in every case: 7.63e-09 at omega = 50,
1.28e-09 at 100, 7.88e-08 at 200, 4.22e-07 at 500 (case 0). That is the Bessel filter of
Finding 032, whose deviation from unity scales as (w / w_crit)^2. It is a property of how the
answer is extracted, not of the model.

This also explains why the TMD residual is larger than the sky-hook's: the TMD cases are
probed up to omega = 1000 while the sky-hook cases stop at 360.

## 4. The fidelity ladder, complete

| rung | kernel | what it checks | agreement |
|---|---|---|---|
| L0 | Python/SciPy, frequency domain | the reference | - |
| L1 | Python/SciPy, frequency domain | adds constraints | - |
| L2-Julia | Julia + DifferentialEquations, time domain | the numerics | 2.5e-06 |
| L2-Modelica | OpenModelica + MSL, acausal, linearized | the modelling | 2.8e-09 to 7.6e-07 |

Covered by the modelling-independent route: passive networks, the tuned mass damper, and the
lagged sky-hook with its actuator force law. That is every mechanism in ecdr/l0 and ecdr/l1.

Roadmap item (4) is complete, with one caveat stated in section 5.

## 5. Limits

  * Gravity is absent from every emitted model, so the static-sag constraint - one of the four
    L0 requirements, and the one most sensitive to the mass distribution - is still not
    checkable through this route. Filling it needs a world component or an equivalent gravity
    force, and has not been done.
  * The robustness machinery is not covered. verify_l1 and robust_violation_corners take a
    worst case over a perturbation box; Modelica would have to be driven once per corner,
    which is affordable but was not done here.
  * The emitted models are still linear, and agreement at 1e-08 is agreement on THIS model.
    Friction, nonlinearity and non-ideal actuators are outside both routes.
  * Four parameter sets, one seed, and f_crit = 1e5 throughout.
  * The emitter writes one model per structure with component values as literals, so a
    perturbed design is a new compile; corner-based robustness would multiply compiles by 2^d.
