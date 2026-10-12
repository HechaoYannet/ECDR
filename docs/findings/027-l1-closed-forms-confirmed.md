# Finding 027 - The L1 hand-derived expressions are confirmed by simulation

Status: the two closed forms that every L1 conclusion rests on, derived by hand and never
simulated, now have an independent numerical check. Both hold to about 1e-06.
Reproduce: scripts/step54_l1_crossvalidation.py.  Data: runs/l1_crossvalidation.json

## 1. The gap this closes

ecdr/l1/models.py states two expressions with no derivation in the file and no simulation
check anywhere:

    T(s)  =  k (s + omega_a) / [ (m s^2 + k)(s + omega_a) + c_sky omega_a s ]

    actuator force per unit ground displacement
          =  c_sky * ( omega_a / sqrt(w^2 + omega_a^2) ) * w * |T|

Everything at L1 rests on them: the actuator-bandwidth study, the 172 to 240 Hz
false-positive zone of Finding 008, and the claim that the active mechanism clears the
passive bound with a factor of 20 of margin. **If either expression were wrong, all of it
would be wrong, and nothing in the project would have noticed.**

L2 was previously used only on the passive mechanical networks, so this was the one part of
the ladder with no independent check at all.

## 2. The derivation, re-checked by hand first

Writing x for the payload displacement with unit mass, F for the force the actuator applies
TO the mass, and the command -c_sky x' through a first-order lag:

    x''  =  -k (x - x_g) + F
    F'   =  omega_a ( -c_sky x' - F )

Laplace: F (s + omega_a) = -c_sky omega_a s X, and (s^2 + k) X - k X_g = F. Substituting,

    X / X_g  =  k (s + omega_a) / [ (s^2 + k)(s + omega_a) + c_sky omega_a s ]

which is the file's expression. **The sign convention is what makes it work**: F is applied
to the mass with a plus sign, and the commanded force carries the minus. Taking F as the
force on the ground instead flips the sign of the c_sky term, which would have been a real
error - and would have left the file's expression looking almost right.

The force expression follows the same way: F / X_g = [-c_sky omega_a s / (s + omega_a)] T,
whose magnitude is c_sky * omega_a / sqrt(w^2 + omega_a^2) * w * |T|.

## 3. The verification

Four parameter sets spanning a strongly lagged actuator to a nearly ideal one
(omega_a / omega_n of 1, 10, 83 and 7.5), three frequencies each (0.25, 1 and 3 times
omega_n), integrating the ODE above and measuring the last-period amplitude:

| omega_n | zeta | omega_a | quantity | median rel diff | worst rel diff |
|---|---|---|---|---|---|
| 60 | 0.5 | 60 | abs T | | 3.09e-07 |
| 60 | 0.5 | 60 | abs F | | 1.24e-06 |
| 60 | 0.5 | 600 | abs T | | 4.64e-07 |
| 120 | 0.7 | 1e4 | abs T | | 9.22e-07 |
| 40 | 1.2 | 300 | abs T | | 5.96e-07 |

over all 12 comparisons:

| quantity | median | worst |
|---|---|---|
| abs T | **1.868e-07** | **9.221e-07** |
| actuator force per unit displacement | **9.553e-07** | **1.236e-06** |

**Both confirmed.** The force law matters as much as the transmissibility: the force
constraint is what bounds the active mechanism's escape in Finding 008, and it had never
been checked either.

## 4. A general kernel, so this does not have to be repeated

ecdr/l2/kernel_julia.jl now exposes

    state_space_amplitude(A, B1, B2, crow, omegas)

for y' = A y + B1 x_g + B2 x_g' with x_g = sin(w t), returning the steady-state amplitude of
crow' y. **Everything this project integrates reduces to that form** - the mechanical
networks through their second-order matrices, and any hand-derived model once written as an
ODE. One kernel now serves both, so the next hand-derived expression can be checked the same
way in a few lines.

## 5. What is established, and what still is not

**Established**: the L1 closed forms are correct expressions for the stated physics. The
frequency-domain algebra, the sign convention, and the actuator force law all survive an
integration that shares no formula with them.

**Not established**: that the stated physics is the right model. Both routes solve
x'' = -k(x - x_g) + F and F' = omega_a(-c_sky x' - F). The first-order lag is an assumption;
a real actuator has saturation, a second-order roll-off, and its own dynamics. **Modelling
independence is still what the Modelica decision was for, and Finding 026 records that it
remains unobtainable here.**

## 6. Limits

  * 12 comparisons, 4 parameter sets. A survey of the parameter box would need more, and the
    box runs omega_a to 2e5 while the largest tested is 1e4.
  * One mechanism (the lagged sky-hook). The passive networks were covered in Finding 026;
    the tuned mass damper at L1 and the robustness machinery of robust_violation have not
    been simulated at all - the latter takes a MAXIMUM over a perturbation set, so a
    simulated check has to reproduce the worst case rather than a single run, and that has
    not been attempted.
  * Integration quality is checked by convergence in Finding 026 but each run here relies on
    the same settings; a lightly damped case at high omega_a was not probed.
