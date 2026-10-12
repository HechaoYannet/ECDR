# Finding 030 - Modelica L2 works, and it checks the MODELLING

Status: OpenModelica 1.27.1 is running in Docker and the L2 rung now provides what Finding
026 said was missing - a check on whether the equations of motion are right, not merely on
whether they are solved right. First result: a model containing no equations of motion
reproduces the L0 transmissibility to **8.3e-06**.
Reproduce: scripts/step58_modelica_smoke.py.
Model: ecdr/l2/modelica/smoke/SdofIso.mo

## 1. What had to be got right first

**Installation.** Docker Desktop was started by the user. The image is pinned:

| | |
|---|---|
| image | `openmodelica/openmodelica:v1.27.1-minimal` |
| digest | `sha256:ac9a0223e69b8055d444b42f58ccb9680342b56848c68b81385bf83d7c0ba824` |
| omc | OpenModelica 1.27.1 |
| MSL | `4.1.0+maint.om`, pinned via `installPackage(Modelica, "4.1.0+maint.om", exactMatch=true)` |
| library volume | named volume `ecdr-oml` mounted at `/root/.openmodelica`, so the library installs once and persists |

This satisfies docs/decisions/002's requirement that the toolchain version be pinned and
recorded.

**Two API corrections, both from asking omc rather than guessing.** The minimal image does
**not** bundle the Modelica Standard Library at all - the first run failed with "Failed to
load package Modelica". And `Translational.Sources.PrescribedPosition` does not
exist in MSL 4.1; `getClassNames` returns
`{Position, Speed, Accelerate, Move, Force, Force2, ...}`. The class is
`Sources.Position`.

## 2. Why this model is different from everything before it

    model SdofIso
      Translational.Sources.Position gnd(exact = true);
      Translational.Components.Mass payload(m = m_p, ...);
      Translational.Components.Spring spring(c = k_s, s_rel0 = 0);
      Translational.Components.Damper damper(d = c_s);
    equation
      gnd.s_ref = A * sin(w * time);
      connect(gnd.flange, spring.flange_a);
      connect(gnd.flange, damper.flange_a);
      connect(spring.flange_b, payload.flange_a);
      connect(damper.flange_b, payload.flange_a);
    end SdofIso;

**There are no equations of motion in this file.** It declares components and connections.
The tool assembles the equations from the component definitions.

L0 and L1 solve equations I derived by hand. The Julia rung of Finding 026 integrates the
same equations by a different route, so it can catch an error in the algebra or the
assembly of M, C, K but **not** an error in the equations themselves. This model can: if I
had written the wrong equation - a sign on the damping, a missing term, the wrong coupling
to the ground - the declared components would assemble the CORRECT equations and the
numbers would disagree.

## 3. The result

L0, frequency domain, at omega = 62.83185307179586 rad/s with omega_n = 99.03, zeta = 0.5426:

| | value |
|---|---|
| L0 abs T(j omega) | 1.3318510554e+00 |
| Modelica last-period amplitude | 1.3318399924e+00 |
| **relative difference** | **8.306e-06** |

**And it is converged**, which the Julia rung was not without care:

| periods kept | t_start | max abs x_payload | ratio to abs T |
|---|---|---|---|
| 1 | 7.9000 | 1.3318399924 | 0.99999169 |
| 2 | 7.8000 | 1.3318399933 | 0.99999169 |
| 4 | 7.6000 | 1.3318399933 | 0.99999169 |
| 8 | 7.2000 | 1.3318399933 | 0.99999169 |
| 20 | 6.0000 | 1.3318399934 | 0.99999169 |

The ratio is identical to eight significant figures whether one period or twenty is used.
The steady state was reached long before the record ends, so the 8.3e-06 residual is not an
unconverged transient - unlike the two outliers of Finding 026, which needed 1280 periods
to settle at resonance.

## 4. What the ladder now is

| rung | kernel | what it checks |
|---|---|---|
| L0 | Python/SciPy, frequency domain | the reference |
| L1 | Python/SciPy, frequency domain + robustness | adds constraints; closed forms confirmed by simulation in Finding 027 |
| L2-Julia | Julia + DifferentialEquations, time domain | **the numerics** - assembly of M, C, K, the algebra, the sign of the ground coupling |
| **L2-Modelica** | **OpenModelica + MSL, acausal component model** | **the modelling** - whether the equations of motion are the right ones |

The last row is the one docs/decisions/001 and 002 were written for, and until now it was
empty.

## 5. Limits

  * **One structure, one frequency.** The SDOF smoke test. The general emitter for arbitrary
    networks from ecdr/structure, and the ensemble sweep, are the next step.
  * **The physical assumptions are unchanged**: linear springs, linear dampers, no friction,
    no nonlinearity, no gravity. What changed is that they are now DECLARED as MSL
    components rather than encoded in my equations - so a wrong component choice or a wrong
    connection would show, but an assumption shared by both formulations would not.
  * **Gravity is absent from the model.** It shifts the equilibrium and does not affect the
    transmissibility of a linear system, so the comparison is unaffected; but a static-sag
    check would need it, and the sag constraint is one of the four L0 requirements.
  * The 8.3e-06 residual is not explained. It is consistent with the CSV output resolution
    (8000 intervals over 8 s) rather than with a modelling discrepancy, but that was not
    tested by refining the output interval.
  * The comparison is one-directional: the Modelica amplitude is compared against L0's
    analytic expression, which was itself only checked against the Julia integration.
