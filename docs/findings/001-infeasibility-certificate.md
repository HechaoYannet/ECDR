# Finding 001 - A rigorous infeasibility certificate for the passive SDOF isolator

Status: **established and independently falsified**. Code: ecdr/l0/certificates.py.
Reproduce with: .venv\Scripts\python.exe scripts\step1_certificate.py

This is the first concrete answer to Q2. It replaces "we tried N times and failed"
with "no parameter choice within this mechanism can ever work", which is the
distinction the seed discussion identified as the most valuable one to get right.

## 1. The testbed

A precision positioning stage sits on a support that connects it to vibrating
ground. What matters is the absolute displacement transmissibility
T(jw) = X_payload / X_ground. All masses are normalised so the total supported
mass is 1; forces are quoted per unit mass.

A task fixes three things:
  * |T| <= T_iso for every frequency at or above f_low
  * the peak of |T| never exceeds A_max
  * the static sag of the support spring never exceeds delta_max

The sag constraint is what gives the problem teeth: a soft spring is good for
isolation and bad for sag, and the two requirements pull in opposite directions.

## 2. Two second-order shapes that differ in one term, and why it decides everything

A passive isolator transmits ground motion through the damper as well as the
spring, so its transmissibility carries damping in the numerator:

    T_passive(r)^2 = (1 + (2 zeta r)^2) / ((1 - r^2)^2 + (2 zeta r)^2)          (P)

An ideal sky-hook actuator applies force with no parallel path to ground:

    T_skyhook(r)^2 = 1 / ((1 - r^2)^2 + (2 zeta r)^2)                           (S)

with r = w / omega_n. Maximising each gives closed forms, and they are different:

    peak(S) = 1 / (2 zeta sqrt(1 - zeta^2))   for zeta < 1/sqrt(2),  else 1
    peak(P) = (D + 1) / sqrt((D - 1)(D + 3))  with D = sqrt(1 + 8 zeta^2)

Two consequences, both of which matter more than they look:

  * **peak(P) > 1 for every finite zeta**, tending to 1 only as zeta -> infinity.
    A passive SDOF isolator ALWAYS amplifies somewhere, however heavily damped.
    A sky-hook does not: push zeta past 1/sqrt(2) and its peak sits at 1.
  * For a fixed peak budget the passive mechanism therefore needs *more* damping,
    and more damping makes its high-frequency isolation strictly worse.

Note: the familiar formula 1/(2 zeta sqrt(1 - zeta^2)) is the peak of the
magnification factor, i.e. of (S), not of (P). Using it for the passive case
understates the peak and silently weakens the certificate. This was a real bug
in the first version of the code, caught by the falsification test in section 4.

## 3. The certificate

Three monotonicity facts about (P), all checked numerically (section 4):
  F1  for zeta < 1/sqrt(2) the peak is attained at r^2 = 2/(D+1)
  F2  beyond that r, T decreases strictly to 0
  F3  for r > sqrt(2), T increases strictly with zeta

Peak constraint. T_max is decreasing in zeta, so T_max <= A_max is equivalent to
zeta >= zeta_min, found by a bracketed root solve. If A_max <= 1 the mechanism is
infeasible outright, because peak(P) > 1 always.

Band constraint. By F2 the binding frequency is the lowest one in the band; by F3
the most favourable admissible damping is zeta = zeta_min. So the best achievable
in-band transmissibility is T(r_low; zeta_min), and requiring it to stay under
T_iso bounds r_low from below:

    omega_n <= omega_low / r*(zeta_min, T_iso)

where, substituting u = r^2 into (P), r* comes from a quadratic with exactly one
positive root whenever T_iso < 1:

    u^2 - (2 + A) u + (1 - 1/T_iso^2) = 0,   A = 4 zeta^2 (1 - T_iso^2) / T_iso^2

Sag constraint. The support carries the full weight, so delta = g/omega_n^2 gives

    omega_n >= omega_n_min = sqrt(g / delta_max)

Combining: the mechanism is feasible **if and only if**

    Lambda := (omega_low / r*(zeta_min, T_iso)) / sqrt(g / delta_max) >= 1

Lambda is a dimensionless escape-difficulty index, and 1/Lambda is the factor by
which the two bounds contradict each other.

## 4. Independent falsification

| Check | Result |
|---|---|
| F1 peak formula is an upper bound (80 random zeta) | max excess 0.0 |
| F1b peak formula is attained (400k-point sweep, 9 zeta) | max error 1.6e-09 |
| F2 monotone decrease beyond the peak | max rise 0.0 |
| F3 monotone increase in zeta for r > sqrt(2) | max drop 0.0 |
| closed-form r* vs numerical root of T(r) = T_iso, 15 combinations | worst diff 5.5e-14 |
| brute-force (omega_n, zeta) grid, 7 tasks, 260 x 180 points | all 7 agree with the certificate |
| when the certificate says FEASIBLE, its own witness is evaluated | all constraints satisfied |

## 5. The reference escape task

    task T_base
      isolation: |T| <= 0.1000 (-20 dB) for f >= 50 Hz   (omega >= 314.16 rad/s)
      peak:      |T| <= 1.4125 (+3 dB) at all frequencies
      sag:       <= 1.000 mm

    zeta_min = 0.542616   (passive, with feedthrough)
    zeta_min = 0.383232   (sky-hook, without)
    r*       = 10.9281
    omega_n >= 99.0285 rad/s   from sag            (LOWER bound)
    omega_n <= 28.7477 rad/s   from the band       (UPPER bound)
    Lambda   = 0.290298
    INFEASIBLE: the bounds are incompatible by a factor 3.445

At the same peak budget the passive mechanism needs 42 percent more damping than
the sky-hook would, and that extra damping is exactly what pushes its high-frequency
isolation out of reach. The mechanism difference is not cosmetic; it is the reason
the task cannot be solved passively.

The band edge at which Lambda crosses 1, i.e. where M1 stops being infeasible:
**f_low = 172.24 Hz**.

## 6. The escape ladder

| Mechanism | Verdict | Evidence |
|---|---|---|
| M1 passive SDOF | **provably infeasible**, Lambda = 0.2903 | exact certificate |
| M2 tuned mass damper | **not feasible** in the scanned family; best peak-feasible in-band |T| = 0.3044 vs limit 0.1 (+204 percent) | numerical, 331,776 combinations |
| M3 sky-hook active | **feasible**, explicit witness | omega_n = 113.06, zeta = 2, in-band |T| = 0.0770, peak 1.0000, sag 0.767 mm, actuator 12781 vs budget 19613 |

So the task is a genuine Design-Space Escape Task: the initial mechanism is
provably inadequate, adding a passive degree of freedom does not rescue it, and
closing a control loop does.

### Why M2 fails, quantitatively

Two necessary conditions, both rigorous for the passive chain:

    Lambda2 = delta_max * omega_low^2 * T_iso / g = 1.006420
      -> the absorber mass fraction must satisfy mu <= 1 - 1/Lambda2 = 0.006379
    zeta1 <= T_iso * omega_low / (2 omega_n1) = 0.158621   (at mu = 0)

Both are extremely tight. Meanwhile the scan shows the peak-feasible members sit
around mu = 0.32 and zeta1 = 0.25: a heavy absorber is needed to hold the peak
down, and a heavy absorber is exactly what the asymptote forbids. The squeeze is
the finding.

**Honesty boundary.** The two ceilings above are proofs. The step from "mu and
zeta1 are capped this tightly" to "the peak must therefore exceed A_max" is
currently numerical evidence, not a proof. Closing it is a well-defined research
task (a fixed-point or Den-Hartog-style lower bound on the peak of the passive
chain under the sag constraint). Until then M2 is reported as "no witness found",
never as "proved infeasible".

## 7. Task difficulty steers the escape depth

Scanning the passive 2-DOF family across band edges with the same constraints:

| f_low | passive 2-DOF best in-band |T| vs limit 0.1 | verdict |
|---|---|---|---|
| 50 Hz | 0.3044 (+204 percent) | not feasible |
| 90 Hz | 0.1409 (+41 percent) | not feasible |
| 110 Hz | 0.1119 (+12 percent) | not feasible |
| 160 Hz | 0.0745 (-25 percent) | feasible |

M1 becomes feasible at 172.24 Hz. So the escape depth is tunable: below roughly
110-160 Hz the passive family cannot do it and only an active mechanism can. This
is the knob that turns one task into a benchmark family with known ground-truth
labels, which is also the answer to the diagnostic-ground-truth problem.

## 8. What this buys, and what it does not

Buys:
  * a sound, non-heuristic pruning signal for one mechanism class
  * ground truth for a benchmark: which mechanism is the minimal one that works
  * a demonstration that "mechanism class" is a real, decision-relevant unit, not
    a narrative device: the passive and active shapes differ by one numerator term

Does not buy:
  * a certificate for M2 or M3. For those we have witnesses (feasibility proofs)
    but no infeasibility proofs.
  * any claim that Lambda generalises beyond second-order passive isolation.
  * anything yet about the agent. This is the physics substrate the agent will act on.
