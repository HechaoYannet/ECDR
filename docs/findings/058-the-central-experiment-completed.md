# Finding 058 - The central experiment, completed: all three arms, and the exponents

Status: section 8's central experiment now has **all three arms** - (a) evaluation only,
(b) evaluation + certificates, (c) certificates only - with the exponents measured. (b) had never
been built. **The mathematics is four propositions, three proved and one proved and measured.**
Against section 9's milestones the score is M2 and M3 done, M1 partial, M4 and M5 and M6 not done.
Reproduce: scripts/step80_curve_b.py.  Data: runs/curve_b.json

## 1. Section 8's specification, item by item

| section 8 requires | status |
|---|---|
| x-axis a size measure growing **combinatorially** in components | **done** - n = 3..10, N(n) from A001187, 3.2e+01 to 3.5e+16 |
| y-axis: cost to rule out | **done** - seconds, measured on the real code paths |
| **(a) evaluation only** | **done** - exponent **1.0000** against N |
| **(b) evaluation + certificates** | **done this round** - exponent **0.0551** against N, **0.8466** against log N |
| **(c) certificates only** | **done** - exponent **0.0597** |
| locate the crossing | **done** - (a)/(b) separation 6.4 at n=3 rising to **9.3e14** at n=10 |
| measure the exponent | **done** |
| test that g(N) = O(1) produces no crossing | **done** - C1 has g = 4 constant, fraction 1.25e-01 falling to 1.13e-16, and lands in section 5.4's row 1: "no crossing ever; decoration" |
| report g(N), not the fraction | **done** |
| cost unit physical and shared | **done** - seconds |
| **L0 -> L1 -> L2 as the cost ladder** | **NOT DONE** - every curve is L0 |
| **L2 as where independent checking happens** | **NOT DONE** - not in the curve |

## 2. Curve (b), which was missing and is the only arm that rules out the whole space

A certificate library covering a fraction per step leaves a remainder, and a certificate alone
does not deal with it. The hybrid rules out all N: certificates where they apply, evaluation
elsewhere.

    hybrid cost = k * (c_p + c_v) + remainder * c_s

| n | N(n) | k | (a) eval only | (b) hybrid | (c) certs only | (a)/(b) |
|---|---|---|---|---|---|---|
| 3 | 3.2e+01 | 4 | 6.889e-02 | 1.076e-02 | 8.611e-03 | 6.400e+00 |
| 5 | 2.317e+04 | 10 | 4.988e+01 | 2.368e-02 | 2.153e-02 | 2.106e+03 |
| 7 | 2.387e+08 | 19 | 5.139e+05 | 4.306e-02 | 4.090e-02 | 1.194e+07 |
| 10 | 3.532e+16 | 37 | 7.605e+13 | 8.181e-02 | 7.965e-02 | **9.296e+14** |

**Measured exponents**: (a) **1.0000**; (b) **0.0551 against N** and **0.8466 against log N**;
(c) **0.0597**.

**So (b) does not share (a)'s exponent.** The certificate count grows logarithmically while the
remainder shrinks geometrically, so at large N the hybrid is dominated by k * (c_p + c_v) and its
exponent against N falls toward zero while evaluation stays at one. **That is the crossing
section 8 asks for, on the arm that was absent.**

**Caveat**: the remainder is held at its integer floor of 1, which is the idealised case. A real
library's remainder will not land exactly on 1, and the exponent of (b) is sensitive to how much
of the space the library actually clears.

## 3. The mathematics: four propositions

| | statement | status |
|---|---|---|
| **Prop 1** | any procedure deciding "does x in F have P(x)=1" from evaluations alone needs Omega(abs(F)) queries | **proved**, section 5.2, adversary argument |
| **Prop 2** | certification is cheaper than evaluation exactly when g(N) > (c_p + c_v)/c_s | **proved**, section 5.3, algebra |
| **Prop 3** | under uniform sampling, M = Theta(1/delta) independent of N - **so in the probabilistic regime there is NO crossing** | **proved**, section 5.5, sampling theory |
| **Prop 4** | a heuristic reading the same verdict prunes identically and scales as enumeration; only the certificate's cost lacks g(N) | **proved AND measured**, section 5.3, exact on eight sizes; certificate cost identical at n=3 and n=10 |
| library law | k = O(log N / log(1/(1-f))) | section 5.4; attacked by Finding 051, restored by Finding 052 |

**Proposition 3 is the one that bounds the contribution rather than enlarging it**, and it is
stated as a delimitation: where a probabilistic negative suffices, sampling is correct and there is
no crossing. The method owns only the regime where a **certain** negative is required.

## 4. Against section 9's milestones

| # | milestone | status |
|---|---|---|
| M1 | a sound, cheap, class-level certificate with a domain tag and g(N) -> infinity | **partial** - the four-certificate library covers a measured 0.42 to 0.79 per step, but each member's g(N) is Theta(N) only for the first cut; later cuts cover a fraction of the remainder |
| M2 | a structure representation with a size knob, emittable to Modelica | **done** - the emitter, and the tuned mass damper came through it with no new code |
| M3 | **the crossing at L0, measured, with the exponent** | **done** - 1.0000 / 0.0551 / 0.0597 |
| M4 | the crossing reproduced at L1 and L2 with OpenModelica | **NOT DONE** - the L2 rung exists and is validated to 2.8e-09, but the crossing was never reproduced there |
| M5 | the certificate names an invariant, and acting on that name constructs a working structure | **NOT DONE** - Finding 057 found the named remedy can be right while the claim is wrong, and nothing acts on it |
| M6 | a real orchestrator, a real scenario, the whole research flow | **NOT DONE** |

## 5. What the project can and cannot claim

**Can claim, and it is defensible:**

  1. **The structural argument** - certainty about an unexamined member is impossible by
     observation, so the negative conclusion is not "certificate versus heuristic" but
     "certificate versus nothing" (Propositions 1 and 4).
  2. **A cost theorem with a measured instance** - three arms, exponents 1.0000, 0.0551, 0.0597,
     a separation rising to 9.3e14, with the certificate side deliberately over-charged.
  3. **A falsifiable prediction, confirmed** - a certificate with g(N) = O(1) produces no
     crossing, and C1 was measured into section 5.4's decoration row.
  4. **A fidelity ladder with a real independence check** - Modelica-emitted models reproduce L0
     to 2.8e-09 and the emitter survives arbitrary topologies.

**Cannot claim:**

  1. **Superiority over existing practice**, because we chose the problem, the baselines and the
     metric (section 2.2), and section 12 forbids treating a self-authored benchmark as evidence.
  2. **That the crossing survives the cost ladder.** M4 is not done: the curves are L0 only.
  3. **That an agent can derive a certificate we do not have.** M6 is not done, and the one
     non-circular attempt produced the classical textbook argument - which turned out to be
     **correct** and my apparatus wrong (Findings 054 to 056).
  4. **That the check is a third-party verification.** Finding 057: a reader that can only read
     accepted a false certificate at 0.95 and a flawed control at 0.88, and the false one was
     installed.

## 6. The honest summary of where this stands

**The mathematics and the L0 crossing are the case.** Four propositions, three proved outright and
one proved and measured; a three-arm curve with exponents that match what section 5 predicts; and
a confirmed falsifiable prediction about the O(1) case.

**M6 is not the case.** The orchestrator runs, the LLM works, and the pipeline is real - but the
certificates in it are still ours, the scenario is one where the certificate is a textbook
algorithm, and Finding 048 showed the check there is circular. **Section 2.2's caveat applies to
M6 exactly as it applied to vibration: it shows the machinery runs, not that the method wins.**

**M4 and M5 sit between.** Both are reachable with the machinery that exists - L2 is built and
validated, and the named remedy is already a field on the certificate - and neither has been done.

## 7. What a wrap-up would contain, and what it would have to say about itself

A paper from this state would rest on sections 4 and 5: the structural impossibility of certain
negative conclusions from observation, the cost theorem, the four propositions, and the measured
L0 crossing with the O(1) prediction confirmed. **That is a real result and it does not depend on
any agent.**

It would have to state, in its own limitations section, that **the empirical arm is L0**, that the
certificates are the authors', and that **the two places where the apparatus was checked by an
adversary, it was wrong** - Findings 043, 055 and 056 - which is both a warning about the
apparatus and evidence for the project's own thesis that certain negative conclusions need an
argument rather than more observation.
