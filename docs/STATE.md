# The state of the project

Written at round 56. This is the honest inventory: what is proved, what is measured, what failed,
and what a paper from this state could and could not say. It is not a summary of effort; it is a
statement of what is true.

---

## 1. The claim

Certainty about an unexamined member of a design space cannot be obtained by observation. A
procedure that concludes "no structure in this family has property P" from evaluations alone must,
in the worst case, evaluate the whole family. **A certificate is a class-level statement with a
soundness argument, a domain tag, and a cost that does not contain the size of the family** - and
because of that last property it can reach a conclusion that evaluation cannot reach at any price.

The contribution is **not** "certificates beat search". It is that the two are different kinds of
thing, that the difference is a scaling difference and not a constant, and that the difference is
**bounded**: where a probabilistic negative suffices, sampling is the correct tool and there is no
crossing at all.

---

## 2. What is proved

| | statement | status | where |
|---|---|---|---|
| **Prop 1** | deciding "does x in F have P(x)=1" from evaluations alone needs Omega(abs(F)) queries | **proved**, adversary argument | ROADMAP 5.2 |
| **Prop 2** | certification is cheaper than evaluation exactly when g(N) > (c_p + c_v)/c_s | **proved**, algebra | ROADMAP 5.3 |
| **Prop 3** | under uniform sampling M = Theta(1/delta) independent of N, so **in the probabilistic regime there is NO crossing** | **proved**, sampling theory | ROADMAP 5.5 |
| **Prop 4** | a heuristic reading the same verdict prunes identically and scales exactly as enumeration; **only the certificate's cost lacks g(N)** | **proved AND measured**, exact on eight sizes | ROADMAP 5.3, Finding 053 |
| library law | k = O(log N / log(1/(1-f))) | section 5.4; attacked by 051, restored by 052 | ROADMAP 5.4 |

**Proposition 4 is the one that makes the project's central sentence falsifiable.** If a procedure
existed that read the same verdict, pruned identically, and cost independent of g(N) without being a
class-level argument, part 3 would fail. The proof says why none exists: any procedure that examines
members has g(N) in its cost.

**Proposition 3 is the one that limits the claim rather than enlarging it**, and it is stated as a
delimitation.

---

## 3. What is measured

### 3.1 The central experiment (section 8), all three arms

Cost of ruling out a region, against a design space that grows combinatorially. x-axis N(n) from
A001187, 3.2e+01 to 3.5e+16. Cost unit: seconds, on the real code paths.

| arm | exponent | meaning |
|---|---|---|
| **(a) evaluation only** | **1.0000** against N | Theta(g(N)), as predicted |
| **(b) evaluation + certificates** | **0.0551** against N, **0.8466** against log N | the hybrid, and the only arm that rules out the whole space |
| **(c) certificates only** | **0.0597** | flat, as predicted |

**The crossing, located**: (a)/(b) separation **6.4 at n = 3 rising to 9.3e+14 at n = 10**.

### 3.2 The cost ladder (section 8, "L0 -> L1 -> L2 is the cost ladder")

| fidelity | cost of one evaluation | separation at n = 10 |
|---|---|---|
| L0, frequency-domain transmissibility | 1.509e-03 s | 9.296e+14 |
| L1, robust evaluation, 2^2 corners | 6.036e-03 s | 3.446e+15 |
| **L2, emit + OpenModelica linearize + evaluate** | **1.8816 s** | **3.431e+16** |

**The crossing survives the ladder and moves earlier**, because the certificate's cost is c_p + c_v
and contains no c_s.

### 3.3 The O(1) prediction, confirmed

Section 8 asks the experiment to test that "a certificate with g(N) = O(1) produces no crossing at
all". **C1 (modal) was measured into section 5.4's row 1**: coverage 1.25e-01 falling to 1.13e-16,
speedup 4200.7 times that never improves. **Confirmed.**

### 3.4 g(N) for the library, measured uniformly from the space at each n (Finding 062)

1000 structures per size, n = 3..12, thresholds calibrated at n = 3 and held fixed.

| certificate | coverage n=3 -> n=12 | exponent | g(N) |
|---|---|---|---|
| **C1 modal** | 1.0000 -> **0.0000** | -12.287 | **BOUNDED** |
| **C3 slow** (Rayleigh) | 0.5000 -> 0.6370 | **+0.145** | **-> infinity** |
| **C4 fast** (row sum) | 0.5000 -> 0.0270 | **-2.133** | **-> infinity** |

**C1's coverage is exactly zero for every n >= 4** - not decaying, identically zero, because a
requirement of four harmonics cannot be violated by a structure with four or more modes.

**And C4 decays as n**-2.13 and STILL diverges**, because N(n) grows super-exponentially while the
decay is polynomial. **Constant coverage is sufficient but not necessary.** That is a stronger
statement than section 5.4 makes, and it softens the design criterion: a candidate invariant need
not be scale-free, only not exponentially shrinking.

### 3.5 The certificate survives the fidelity change (Finding 061)

A **free-response** Modelica model (the emitter had none, which invalidated two earlier attempts).
C1 checked against what OpenModelica actually integrated: **0 violations on 8 structures**, and L0
measured **by the same procedure** agrees with L2 to **9.50e-05**. **Section 6 Layer C revokes
nothing.**

### 3.6 The named remedy determines the repair (Finding 059)

A certificate whose claim and argument were both **false** named "a cross-pinch exchanger" - and
**H1-C1 transfers 10 kW across the pinch in the optimal design**. Acting on the name constructs the
working structure. **M5's falsifier is answered.**

---

## 4. Milestones

| # | milestone | status |
|---|---|---|
| **M1** | a certificate with g(N) -> infinity | **SATISFIED** - C3, coverage 0.500 -> 0.637 |
| **M2** | a structure representation emittable to Modelica | **DONE** - the tuned mass damper came through with no new code |
| **M3** | the crossing at L0, measured, with the exponent | **DONE** - 1.0000 / 0.0551 / 0.0597 |
| **M4** | the crossing reproduced at L1 and L2 with OpenModelica | **DONE** - to 3.431e+16, and the certificate is confirmed at the top of the ladder |
| **M5** | the certificate names an invariant, and acting on the name constructs a working structure | **DONE** - Finding 059 |
| **M6** | a real orchestrator, a real scenario, the whole research flow | **NOT DONE** - see section 7 |

**Five of six.** The one that is missing is the one that would show the method works on a problem
the project did not choose.

---

## 5. The negative results, which are the most useful part of this record

### 5.1 The apparatus was wrong three times, and each time an outside reading caught it

| | the objection | what was true |
|---|---|---|
| Finding 043 | "the 2-unit network leaves C2 unheated" | `network_lp` let pool heat reach an unmatched stream; the number was 142.5 where it should be 150.0 |
| Findings 046-047 | (a framing objection) it would not search if no reply could come | my protocol's fault; adding one sentence reversed the result |
| Findings 054-056 | "minimum units = N - K, with K balanced components" | **my count omitted the utility exchangers entirely**; the classical bound was right and had never been refuted |

**In each case the objection named a missing condition in my model, and in each case the condition
was one the objecting model's own domain knowledge supplied.** Finding 044's "clean connectivity
argument" was sound graph theory applied to a graph missing two nodes.

**And Finding 057 is the same lesson pointed at the checking machinery itself**: a reader given an
argument but no way to test it judged a false certificate **sound at confidence 0.95** and a
deliberately flawed control at **0.88**, and the false one was installed. Finding 045's reader found
real defects **because it had concrete cases to evaluate**. A reader that can test finds flaws; a
reader that can only read accepts them.

### 5.2 Ten verdicts that could not fail for the reason the test existed

| # | the verdict | why it was wrong |
|---|---|---|
| 1 | an anomaly in the ramp response | compared against a synthetic baseline |
| 2 | "the scale factor is two" | the pre-factor was held fixed |
| 3 | "the crossing exponent is 1" | the crossing had not been reached |
| 4 | "the named remedy is not what was missing" | decided from a four-unit count, **contradicted by its own table** |
| 5 | "agreement 7 of 8" | forced response used to test a free-response claim |
| 6 | "osc_pairs <= n, 0 of 8" | the excitation's pole counted as a structural mode |
| 7 | "C1 does NOT survive at L2" | an inverted metric: an unexcited mode scored as a mismatch |
| 8 | "agree to within 8.21e-01" | 8.21e-01 **was** the disagreement |
| 9 | "C4 survives" | an arbitrary 0.05 threshold let a decaying quantity pass |
| 10 | "C3 decays too, at alpha = +0.145" | a positive exponent is not a decay |

plus one more of the same kind, unnumbered: calling alpha = +0.145 with a standard error of 0.0114
"indistinguishable from zero" when it is 12.7 standard errors from zero.

**Five of the ten were arithmetically correct.** The failure was never in the arithmetic; it was in
attaching a conclusion to a number that did not support it.

**What actually caught them, in order of how often it worked:**
  * **looking at the raw data the statistic was computed from** (instances 4, 7);
  * **asking what the number would look like if the claim were false** (instances 5, 6);
  * **an outside reader with test access** (the 043, 055 and 057 family).

**More computation never caught one.** Every one of the ten was produced by computation.

### 5.3 Findings withdrawn

| finding | withdrawn by | why |
|---|---|---|
| 037, 044 | 055 | compared a matches-only count against U >= N - 1, whose N includes utilities and whose units include utility exchangers |
| 038 | 040 | claimed the model returned empty content; the cause was my own max_tokens cap |
| 051 | 052 | measured the procedure of section 2.1 line 60 - a heuristic - and attributed its cost to the certificate |

**Finding 052 is the one worth reading.** It restored a result the project had spent a round
declaring wrong, and the thing that caught the error was rereading the roadmap's own requirement
that a certificate's cost grows slower than abs(F) - which the procedure Finding 051 measured
plainly violates.

---

## 6. What a paper from this state can and cannot claim

**Can claim, and it does not depend on any agent:**

  1. the structural impossibility of a certain negative conclusion from observation (Prop 1);
  2. a cost theorem with a measured instance - three arms, exponents 1.0000 / 0.0551 / 0.0597, a
     separation to **9.3e+14**, with the certificate side **deliberately over-charged**;
  3. a falsifiable prediction confirmed - a certificate with g(N) = O(1) produces no crossing;
  4. the finding that constant coverage is **sufficient but not necessary**, which softens the
     design criterion;
  5. a fidelity ladder with a real independence check, where the certificate survives and the
     revocation path is exercised and nothing is revoked;
  6. Proposition 4, which makes "a certificate is a different kind of thing" falsifiable rather than
     rhetorical.

**Cannot claim:**

  1. **superiority over existing practice** - the problem, the baselines and the metric are all ours
     (section 2.2), and section 12 forbids treating a self-authored benchmark as evidence;
  2. **that an agent can derive a certificate we do not have** (M6);
  3. **that the check is a third-party verification** - Finding 057;
  4. **generality of the coverage numbers.** Coverage is a property of the
     (invariant, ensemble, requirement) triple (Finding 012); the structures are sampled uniformly
     in **graph structure**, not in physical plausibility, and a real design space is not a uniform
     graph ensemble.

---

## 7. The M6 gap, stated precisely

The orchestrator exists and runs on Cordis. It has a real service graph (physics, certificates,
checker, llm, loop, run, derive, audit, selfaudit, unitsbound), the LLM works, certificates are
installed and revoked through `ctx.effect()`, and the whole pipeline executes end to end.

**None of that is the milestone.** M6 asks whether the method transfers to a scenario the project
did not author, and its falsifier is exactly that. What is missing:

  * **the certificates in the loop are ours**, not the agent's;
  * **the scenario is one where the certificate is a known algorithm** - pinch analysis in the heat
    domain - and Finding 048 recorded that the check there is circular, because the checker and the
    ground truth are the same algorithm;
  * **the one non-circular attempt produced the classical textbook argument, and it was right while
    my apparatus was wrong** (Findings 054-056);
  * **the agent's own contribution is a consistent false belief** - V = 6 with the pinch-decomposition
    argument, in three separate runs, corrected only when handed a counterexample it could evaluate.

**So the honest statement is: the machinery is demonstrated, the method is not.** A paper that
claimed M6 on this evidence would be claiming that a pipeline runs, not that certification works on
an unfamiliar problem. Section 12 forbids it and the evidence does not support it.

**What it would take**: a domain where the certificate is not a known algorithm, a requirement where
a certain negative is genuinely needed, and a certificate the agent derives that the authors did not
supply. **The cheapest step toward it is Finding 057's own finding** - the named remedy is a
refutation test the harness was not running, and wiring it in costs one enumeration.

---

## 8. Reproducibility

64 commits, 62 findings, 89 step scripts, 73 run artifacts. Every claim above names the script that
produces it and the JSON it writes.

Standing rules adopted after the failures above, each traceable to a specific instance:
  * check any two compared columns for algebraic identity;
  * **never print a verdict not computed from the same run's data**;
  * check the variance before testing an effect;
  * test the rate for an asymptotic claim;
  * never ignore a numerical warning;
  * **an empty or degenerate regime is neither a separation nor a failure**;
  * **a number produced in a regime where it does not mean what it says is not a result.**

The last two were added after the instances in section 5.2, and the ten instances are the evidence
that they were needed.
