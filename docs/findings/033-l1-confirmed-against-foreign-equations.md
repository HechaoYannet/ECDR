# Finding 033 - The L1 closed forms confirmed against equations this project did not write

Status: the modelling-independence check is real. The L1 transmissibility and actuator force
law are confirmed against a model containing **no equations of motion**, to a median relative
difference of **2.8e-09** - four orders tighter than the Julia rung, and instant rather than
1080 excitation periods.
Reproduce: scripts/step62_modelica_skyhook.py, step63_modelica_l1_full.py.
Data: runs/modelica_skyhook.json, runs/modelica_l1_full.json

## 1. What was already known, and what was not

Finding 027 confirmed the L1 closed forms

    T(s) = k (s + omega_a) / [ (s^2 + k)(s + omega_a) + c_sky omega_a s ]
    actuator force per unit displacement = c_sky * omega_a / sqrt(w^2 + omega_a^2) * w * |T|

against a time-domain integration, to about 1e-06. That check was real but bounded: **both
routes solve the same equations of motion**, the ones written in ecdr/l1/models.py. It
establishes that the algebra, the sign convention and the force law are right. **It cannot
establish that the equations are the right model**, because an error common to both would
cancel.

Finding 030 said exactly this and named Modelica as the remedy.

## 2. The Modelica model of the lagged sky-hook

emit_skyhook_model declares:

    Translational.Components.Mass payload
    Translational.Components.Spring support
    Modelica.Blocks.Math.Gain gain(k = -c_sky)
    Modelica.Blocks.Continuous.FirstOrder lag(k = 1, T = 1 / w_a)
    Translational.Sources.Force actuator
    Translational.Sources.Position gnd(exact = false, f_crit = 1e5)

wired by
    gain.u = payload.v;  connect(gain.y, lag.u);  actuator.f = lag.y;

**No equation of motion and no differentiator appears.** The commanded force is the payload
velocity through a gain, a first-order lag and a force source - declared, not derived. The
payload velocity is a state of the translational domain, which is why the sky-hook can be
expressed without differentiating anything.

## 3. The result

Twelve comparisons, four parameter sets, three frequencies each, compared through omc's
linearization:

| omega_n | zeta | omega_a | omega | abs T (L1) | abs T (Modelica) | rel |
|---|---|---|---|---|---|---|
| 60 | 0.5 | 60 | 15 | 9.768196945e-01 | 9.768196944e-01 | **1.76e-10** |
| 60 | 0.5 | 60 | 60 | 1.414213562e+00 | 1.414213558e+00 | **2.82e-09** |
| 60 | 0.5 | 60 | 180 | 1.407195089e-01 | 1.407195054e-01 | **2.54e-08** |
| 60 | 0.5 | 600 | 15 | 1.024319950e+00 | 1.024319950e+00 | **1.76e-10** |
| 60 | 0.5 | 600 | 180 | 1.301383306e-01 | 1.301383273e-01 | **2.54e-08** |
| 120 | 0.7 | 1e4 | 30 | 9.983173168e-01 | 9.983173161e-01 | **7.05e-10** |
| 120 | 0.7 | 1e4 | 360 | 1.123658639e-01 | 1.123658525e-01 | **1.01e-07** |
| 40 | 1.2 | 300 | 10 | 8.852799057e-01 | 8.852799056e-01 | **7.83e-11** |
| 40 | 1.2 | 300 | 120 | 1.204159458e-01 | 1.204159444e-01 | **1.13e-08** |

| quantity | median | worst |
|---|---|---|
| abs T | **2.819e-09** | **1.015e-07** |
| **actuator force per unit displacement** | **2.819e-09** | **1.015e-07** |

The force law matters as much as the transmissibility: the force constraint is what bounds
the active mechanism's escape in Finding 008, and it is now confirmed against an
independently assembled model.

**Finding 027 was about whether the expressions are right. This is about whether the
equations they solve are the right equations. Both now hold.**

## 4. And the passive networks, where the time domain could not reach

| structure | n | ground ties | omega | L0 | Modelica | rel |
|---|---|---|---|---|---|---|
| 0 | 5 | 3 | 26.222 | 1.113727028 | 1.113727057 | **2.59e-08** |
| 0 | 5 | 3 | 109.26 | 2.641049795 | 2.641049766 | **1.10e-08** |
| 1 | 3 | 1 | 22.024 | 1.545945227 | 1.545945210 | **1.10e-08** |
| **1** | **3** | **1** | **91.768** | **1.033724063e-01** | **1.033723924e-01** | **1.35e-07** |
| 2 | 4 | 2 | 18.934 | 1.522155026 | 1.522155005 | **1.42e-08** |
| 2 | 4 | 2 | 78.891 | 5.119482866e-02 | 5.119482141e-02 | **1.42e-07** |
| 3 | 2 | 1 | 50.245 | 1.586275896 | 1.586275902 | **3.66e-09** |
| 3 | 2 | 1 | 209.35 | 2.644812644e-01 | 2.644812550e-01 | **3.57e-08** |

**median 2.008e-08, worst 1.415e-07.**

Structure 1 at omega = 91.768 is the case Finding 031 could only bring to **2.2e-04 after
1080 excitation periods and 108,000 output intervals**. It is now **1.35e-07, instantly** -
**six orders of magnitude better for a fraction of the cost.**

## 5. Three defects caught, and how

  * **emit_model still used `Position(exact = true)`** - the Finding 032 trap. The guard
    added to `linearize.py[[/B]] in that same round rejected the dump outright: *"REJECTED: B is
    identically zero"*. **The guard paid for itself on its first use.** Without it the passive
    networks would have come back as T identically 1 and looked like a modelling error.
  * **`payload.v[[/B]] is a variable, not a connector.** `connect(payload.v, gain.u)[[/B]] fails with
    "payload.v is not a valid connector"; it must be an equation, `gain.u = payload.v[[/B]].
  * **`tf_mag[[/B]] returned the complex value, not the magnitude.** The name promised one thing
    and the function did another. Above resonance the real part of the transmissibility is
    NEGATIVE, so callers received negative numbers and ratios of 1.20, 2.00, 1.76 and 1.99 -
    apparently a total disagreement with L0, actually a naming defect. Split into
    `tf_complex[[/B]] and `tf_mag[[/B]].

The third is the same class as the six identity traps and the inverted independence ratio: a
number produced in a regime where it does not mean what its name says.

## 6. What the ladder now is

| rung | kernel | what it checks | agreement |
|---|---|---|---|
| L0 | Python/SciPy, frequency domain | the reference | - |
| L1 | Python/SciPy, frequency domain | adds constraints | - |
| L2-Julia | Julia + DifferentialEquations, time domain | the **numerics** | 2.5e-06 |
| **L2-Modelica** | **OpenModelica + MSL, acausal, linearized** | **the modelling** | **2.8e-09** |

Both L1 closed forms and the passive networks are now confirmed by a route that shares no
equation with the rest of the project. **The last row is the one decisions/001 and 002 were
written for, and it now covers every mechanism the project uses except the tuned mass damper
at L1.**

## 7. Limits

  * **The tuned mass damper at L1 is not emitted.** Only the lagged sky-hook and the passive
    networks are. That is the remaining gap in mechanism coverage.
  * **Gravity is absent** from every emitted model, so the static-sag constraint - one of the
    four L0 requirements - is still not checkable through this route.
  * The Position filter is not removed, only pushed out of band; the growth of the residual
    with frequency in Finding 032 is the filter, and the same applies here.
  * The networks are four structures from one ensemble family at two frequencies each, all
    with `f_crit = 1e5[[/B]] and one seed. Not a survey.
  * Agreement at 1e-08 is agreement on THIS model. That the model is the right one for a real
    isolator - no friction, no nonlinearity, linear springs and dampers - is a separate claim
    neither route tests.
