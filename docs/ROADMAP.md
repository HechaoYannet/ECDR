# Research roadmap

Status: proposed, revised after review. Naming deliberately deferred - it is a
consequence of the method, not a wrapper around it.

---

## 0. The question, restated so that it has an answer

The draft asks:

> Can an AI agent recognise a **capability gap** in the current structure from physical
> evidence, and construct a structure that closes it?

and decomposes the error of a design attempt as

    ell(S, that)  =  delta(S)  +  [ ell(S, that) - delta(S) ]
                     ^^^^^^^^     ^^^^^^^^^^^^^^^^^^^^^^^^^^^
                     structural   search has not closed it yet
                     gap

with delta(S) = inf_theta L( F(S, theta; z), y* ) and a capability gap being
delta(S) > epsilon.

**The whole research lives in that decomposition.**

---

## 1. The central difficulty, stated as a fact rather than a complaint

Search can only ever produce an upper bound:

    search finds theta_hat   =>   delta(S) <= ell(S, theta_hat)

The decision needs a lower bound:

    should I abandon S ?     <=>   delta(S) > epsilon ?

**No amount of search converts one into the other.** Every negative result search
produces is equally consistent with "the structure is inadequate" and "my search is
inadequate". So an agent whose only instrument is search cannot perform the attribution
of sub-challenge 1 - not poorly, but in principle. This is a structural fact and
section 5 turns it into a theorem.

---

## 2. What we have established, and the epistemic status of it

### 2.1 Results

| result | status |
|---|---|
| **Waterbed closed form** | **CORRECTED by Finding 018: W = pi * sum over RHP zeros of Re(1/z)**, verified to 4e-07 where roots are computable and exact on the 85 networks with no RHP zero. The coefficient form was invalid: |
| ~~Waterbed coefficient form (originally Finding 004)~~ | **DOWNGRADED by Finding 016.** The identity p1/p0 = q1/q0 is exact (6.9e-18, resting on C 1 = g), so the closed form predicts zero for every passive network - but the integral is non-zero and converged for about one network in ten. The formula is not valid in general |
| Closed-form infeasibility certificate for one mechanism class (passive SDOF; two incompatible bounds on omega_n; Lambda = 0.2903; independently falsified on 7 tasks) | exact, verified |
| Certificates **transfer upward** through a fidelity ladder built so each level only ADDS constraints | exact, verified |
| A certificate's **feasibility** verdict does NOT transfer upward (the 172-240 Hz zone) | measured |
| On small problems, score/streak/surrogate pruning is competitive with certification | measured |
| Where a certificate can prune, a plain heuristic reading the same verdict prunes identically | measured |

### 2.2 The epistemic status of the vibration benchmark

Stated plainly because it governs how the results may be used: **the certificate, the
three mechanisms, the heuristics, the task family, the metric and the baselines were all
authored by us.** What the vibration work establishes is therefore

  * **soundness** - a class-level certificate can be derived, is exact, survives brute-force
    falsification, and transfers up a fidelity ladder;
  * **feasibility** - the machinery runs end to end and the accounting is honest.

It does **not** establish superiority over existing practice, because we also chose the
problem, the baselines and the metric. A self-authored benchmark can make a theory stand
up; it cannot make the case for it.

The case has to come from two places that are not ours to choose:

  1. the **mathematical analysis** of section 5, whose statements are true or false
     independently of what we would prefer;
  2. the **real-scenario orchestrator** of M6, where the structure space and the
     requirement come from outside the project entirely.

---

## 3. The idea

> **A capability gap should be certified, not searched for.**

A **capability-gap certificate** for a structure family F, a requirement (C, epsilon) and
conditions z is a statement

    for all S in F :  delta_z(S) > epsilon

carrying three things:

| component | role |
|---|---|
| a **soundness argument** | checkable by a third party, independent of the search that motivated it |
| a **domain tag** | the assumptions under which it holds; this is what makes it revocable rather than a gate |
| a **cost growing slower than abs(F)** | the property that makes it different in kind from sampling (section 5 makes "slower" precise) |

and it is used as a **confidence operator**, not a filter: without a certificate,
confidence accumulates by sampling and the conclusion is always "not found yet"; with
one, a single derivation sets the confidence of an entire family to zero.

---

## 4. Why a proof is cheaper - the structural argument

    sampling:  cost ~ (candidates that must be examined) x (cost per evaluation)
    proof:     cost ~ (deriving the invariant) + (checking it)

The second does not contain the size of the space. Section 5 proves that this is not a
matter of degree.

---

## 5. The mathematical analysis of the crossing

The crossing must be a theorem, not a plot. Experimental curves alone can always be
attributed to a badly tuned baseline; a theorem cannot.

### 5.1 Setup

Let the structure space at size N be S_N, abs(S_N) = N. Let P : S_N -> {0,1} be the
feasibility predicate for the requirement (C, epsilon). Write c_s for the cost of one
evaluation and c_p for the cost of deriving and checking a certificate.

### 5.2 Certainty about an unexamined member is impossible by observation

**Proposition 1 (query lower bound).** Any procedure that correctly decides
"does there exist x in F with P(x) = 1" using only evaluations of P has worst-case query
complexity at least abs(F).

*Proof.* Adversary answers P = 0 to every query. A procedure that stops after fewer than
abs(F) queries has left some x* unqueried; the instance with P(x*) = 1 and P = 0
elsewhere is consistent with every answer received, but the correct answers differ.
Hence no procedure with fewer than abs(F) queries is correct on both. (Standard; stated
because it is the load-bearing step.)

**Consequence.** Ruling out a region of K structures *with certainty* costs Omega(K)
evaluations. **Escaping that bound requires an argument about the class, not more
observations.** So the real choice for the negative conclusion is not "certificate versus
heuristic" but "certificate versus nothing".

### 5.3 The cost theorem and the crossing

**Proposition 2.** If a certificate establishes P = 0 on a subfamily C_N with
abs(C_N) = g(N) at cost c_p, then

    cost to certainly rule out C_N by evaluation  =  Theta(g(N) * c_s)
    cost to certainly rule out C_N by certificate =  c_p + c_v

and certification is cheaper exactly when

    g(N)  >  Theta( (c_p + c_v) / c_s )

**This is where the design criterion comes from.** Everything depends on g(N), the NUMBER
of structures the certificate rules out, and not at all on the fraction.

### 5.4 The coverage growth condition

Two different quantities must not be confused:

    ABSOLUTE saving  =  g(N) * c_s  -  c_p        grows whenever g(N) -> infinity
    RELATIVE saving  =  N / (N - g(N))            tends to 1 unless g(N) = Theta(N)

So the corollary splits in two, and the second half is the one that matters.

**Corollary (design criterion).**
  1. A crossing exists iff g(N) -> infinity.
  2. The crossing is **persistent** - a speedup that does not decay toward 1 - iff
     g(N) = Theta(N), i.e. iff the certificate rules out a constant FRACTION.

**But condition 2 is not the right target, and Finding 011 supersedes it.** A single
certificate satisfying condition 2 still caps the speedup at 1/(1-f), so covering half the
space buys a factor of two. What produces a real separation is a **library**:

    certificate i rules out a fraction f_i of the space remaining after 1..i-1
    => remaining <= prod(1 - f_i)
    => k = O( log N / log(1/(1-f)) ) certificates suffice

and the count grows ADDITIVELY per decade of N while sampling grows MULTIPLICATIVELY. At
N = 6.4e10, a per-step coverage of one part in a thousand gives k = 24,876 certificates
against 6.4e10 evaluations: a separation of 2.6e6. **The requirement therefore relaxes
from "cover a constant fraction" to "cover a constant, arbitrarily small, fraction per
step"**, and the thing to look for is a FAMILY of scale-free, mutually independent,
physically sound invariants - not one deep theorem.

| g(N) | absolute saving | relative saving | verdict |
|---|---|---|---|
| Theta(1) | bounded | -> 1 | **no crossing ever**; decoration |
| -> inf but o(N) | grows | -> 1 | crossing exists but the advantage **decays away** |
| Theta(N) | grows | constant > 1 | **persistent advantage** |

**A structural consequence, which is the real content.** In a space whose size grows
super-exponentially in the number of components, any predicate of the form "this
structure has too few of a bounded resource" - too few masses, too few components, too
few ground paths - is satisfied by a **vanishing fraction** of the space. Such predicates
are therefore permanently in the second row, however sound and however easy to prove.

| predicate shape | fraction | row |
|---|---|---|
| resource bound (needs >= m components) | vanishing | 1 or 2 |
| threshold on a **balanced** structural attribute | roughly constant | 3 |

**Findings 011 and 012 supersede the "balanced structural attribute" rule above**, which
was a symptom rather than the cause. The corrected rule is:

> **Prefer invariants whose bound is a CONTINUOUS physical quantity.**

Coverage is a property of the triple (invariant, ensemble, requirement), not of the
predicate alone: Finding 012 measured the same invariant giving coverage that sweeps
continuously through (0,1) on one ensemble and is pinned at 0 on another. A continuous
bound - sag, bandwidth, time constant, energy - is always calibratable. A discrete or
combinatorial bound jumps unless the ensemble spreads that attribute, which is a fragile
coincidence. This is a **relaxation**: physical bounds are naturally continuous, so the
"shape" obstacle largely dissolves, and Finding 010's failure of mode counting is re-read
as a consequence of its bound being a small integer.

**AND FINDING 024 REPLICATES IT AND ADDS A FOURTH MEMBER.** A fourth sound certificate - the
FAST time scale, omega_n^2 <= max_i (K_ii + sum abs K_ij)/m_i, from the infinity norm
dominating the spectral radius, 0 violations in 300 and tightest of the four at 1.33 - joins
modal, statics and slow-time-scale. The four compose with sequential conditionals
**0.564 / 0.760 / 0.389**, and on a genuinely different family (tree **plus two extra edges**,
**uniform** values, n in 2..7) the same figure is **0.547 / 0.794 / 0.368**, agreeing to
within 0.035. Round survival 0.0367 against 0.0400; **28 and 29 certificates** for 1e10. One
calibration was found to deplete the space before the library finishes its members, and the
reading there is flagged as vacuous rather than reported.

**AND FINDING 023 CORRECTS A DIRECTION ERROR RUNNING FROM FINDING 013 TO 022.** The ratio
P(notA and notB)/(P(notA)P(notB)) was read as "above 1 is complementary". It is the
reverse: identical cuts give 2.0 and disjoint cuts give 0.0. The numbers are unaffected -
every conditional and every Spearman rho was computed correctly - but two conclusions flip:
Finding 013's performance axes were mildly **complementary**, not redundant, and Finding
015's "structural cuts compose better" is **withdrawn**, since 1.111 is the more redundant
family. Finding 023 also adds a **third sound certificate** (Rayleigh: omega_1^2 <= sum of
ground stiffnesses / sum of masses; 0 violations in 300, rho = -0.006 against the modal
count) and composes all three: the sequential conditionals are **0.537-0.550** and
**0.760-0.806** across four space sizes, leaving 5.2-8.3 percent per round. **The library
condition holds BETTER than independence**, since the cuts are complementary. Library
arithmetic: about **24 certificates against 1e10 evaluations**.

**AND FINDING 022 TURNS THE CONDITION INTO A MEASUREMENT.** A pair of sound certificates -
the modal bound (n degrees of freedom gives at most n harmonics) and the static-equilibrium
bound (sag under gravity) - was tested across four space sizes. With the requirement
calibrated, the second cut takes **0.525 to 0.558 of what the first left** at every size,
and the independence ratio stays above **0.88**. Under a FIXED requirement the modal cut
decays as 1/n_max toward zero, which is Finding 010's mechanism operating slowly. So the
library condition of Finding 011 is satisfiable, and **what binds is the calibration of the
requirement, not the certificates** - the third appearance of that same lesson. The
arithmetic gives k ~ 17 pairs (34 certificates) against 1e10 evaluations. At the sizes this
ensemble can reach the advantage is a dozen against five hundred, so the separation is a
statement about growth and not a demonstrated practical gain.

**AND AGAIN BY FINDING 021, which withdraws Finding 020's pessimistic conclusion.** The
capability space has an **effective dimension of 4.62** (leading eigenvalue share 0.36,
7 components for 90 percent of variance, 14 of 66 pairs below abs(rho) = 0.1). Finding 020
had measured a set of cuts **all taken on one axis** - sag, peak, in-band, g0/m0, W are
every one a monotone measure of how well the structure isolates - and generalised to the
whole space. The correct rule is: **no two cuts on the SAME axis compose; cuts on
different axes do.** A composing pair now exists - the modal bound (sound, topology-keyed)
against isolation performance gives abs(rho) <= 0.17 across three seeds, against 0.81 for
two performance bounds. This also softens Finding 010: mode counting is eliminated only
when the requirement is fixed while the space grows, which is Finding 012's calibration
condition rather than a defect of the invariant.

**CORRECTED AGAIN BY FINDING 020.** Finding 019's "topology vs value" explanation is
refuted by a controlled test: cuts on single component values with controlled overlaps show
no separation (disjoint-draw mean 0.976, shared-draw 1.000, all within two standard errors
of 1.0). What Finding 019 actually measured is that **every performance cut is a monotone
function of one scalar - how well the structure isolates** - with pairwise |Spearman rho|
between 0.39 and 0.82. The separation is real (TOP minus VAL = 0.2477, 95% CI
[0.1786, 0.3185]) but the cause is **common-scalar redundancy**, and the consequence is
worse: every physical performance bound is such a monotone measure, so **no two such
certificates will compose**. The operational test is now the rank correlation between the
certificates' BOUNDS: |rho| near 0 is worth having, |rho| near 0.5 or above is one
certificate wearing two hats.

**SUPERSEDED BY FINDING 019: the split that matters is TOPOLOGY vs VALUE, not structure
vs performance.** Two independently chosen cut lists reproduce the same two numbers -
value-value 0.8274 against Finding 013's 0.8210, and topology-topology 1.1330 against
Finding 015's 1.1110 - so Finding 015 was measuring topology against value and calling it
structure against performance. **A cut composes only if it is keyed to a part of the
structure that varies independently of the parts the other cuts use.** Both candidate
certificates (the payload ground-damping law and the waterbed) are value-derived and
therefore do NOT compose with each other (ratio 0.6066, rho -0.4976). And this is exactly
the draft's notion of structural capability: a statement holding for all theta in
Theta(S) is a statement about S.

**And the axes must be structurally distinct, not merely metrically distinct.**
Finding 013 measured the composition of the three requirement axes (static deflection,
peak transmissibility, in-band attenuation). Each cuts a substantial share of what the
previous ones leave - 0.59, 0.49, 0.76 - so they are not nested. But the observed joint
survival is 0.0500 against 0.1143 for independent marginals, a ratio of **0.437**: the
failures are positively correlated, because a heavy, softly supported, lightly damped
structure is bad on all three at once. **Independent coverage must come from certificates
keyed to different STRUCTURAL FEATURES, not to different performance metrics.**

**And calibration is a benchmark constraint, not a certificate one.** Coverage being
tunable by moving the requirement is nearly circular - in a real problem the requirement is
given. What matters is whether the given requirement lands in the marginal region of the
ensemble's capability distribution, and that must be checked when the benchmark is chosen.

This also retro-explains the earlier failure: the Lambda certificate rules out a fixed
low-dimensional region, so g(N) = O(1) as the structure space grows, which predicts no
crossing - and none was observed.

### 5.5 The statistical regime, and the boundary of the method

If certainty is relaxed to confidence, the picture changes completely.

**Proposition 3.** Under uniform sampling without replacement, M failed draws bound the
feasible fraction by O(1/M) with high probability. M = Theta(1/delta) for a confidence
target delta, **independent of N**.

**Consequence - and this is a delimitation, not a caveat.** In the regime where a
*probabilistic* negative conclusion is acceptable, there is no crossing at all and
sampling is the correct tool. The method's domain is exactly the regime where a
**certain** negative conclusion is required: when the cost of a wrong "this structure
cannot do it" is high, when the space cannot be enumerated, or when the same conclusion
must be reused across many problems without re-sampling. Stating this boundary is part
of the contribution; a method that claims a regime it does not own is not credible.

### 5.6 Proved versus measured

| claim | status |
|---|---|
| Proposition 1 (Omega(K) query lower bound) | provable, short adversary argument |
| Proposition 2 (cost comparison given an invariant) | provable algebra |
| Proposition 3 (statistical regime, no crossing) | provable from sampling theory |
| Corollary (g(N) -> infinity is necessary) | follows from Proposition 2 |
| **Does a given physical requirement admit a certificate with g(N) -> infinity and c_p independent of N?** | **empirical, per invariant. This is the research.** |

So the mathematics fixes the *shape* of the answer and the empirical work must fill in
whether any physical invariant actually achieves it. If none does, the programme fails,
and section 5 says exactly where it would fail.

---

## 6. The method: three layers

### Layer A - structure representation

    S = (component inventory, connection topology, boundary relations),  theta in Theta(S)

  1. a **size measure** that can be swept
  2. **emittable as a simulation model** - if S cannot become a Modelica model it is the
     wrong representation, because L2 must be able to check it
  3. **compositional** - adding a component is a local operation

### Layer B - the certificate layer

A library of physical invariants of structure classes. The research question is which
invariants are (i) sound, (ii) cheap, (iii) **have g(N) -> infinity**, and (iv) **name a
structural remedy** - because a certificate that says only "impossible" is a gate, while
one that says which invariant is violated tells the agent what to build.

| invariant | rules out | names the remedy |
|---|---|---|
| mode / state dimension | too few independent modes | add degrees of freedom |
| energy / passivity | energy transfer a passive structure cannot supply | add a source or active element |
| time-scale / relaxation | rates the storage and conductance cannot produce | add storage or a conductance path |
| band-tradeoff (waterbed type) | isolation in one band without amplification elsewhere | change the ground coupling topology |

### Layer C - confidence bookkeeping

Proved regions take budget **zero**; unproved regions take sampling budget; the fallback
when no certificate exists is ordinary non-chronological backtracking; both live on one
cost axis; a certificate crossed by a higher fidelity is **revoked**, not edited.

---

## 7. The first certificate, worked

The draft already contains it, which is a good sign - it is the right kind of statement.

**Target** y*(t) = 0.7 cos 2t + 0.3 cos 5t, as the free response of a passive linear
mechanical structure.

**Invariant.** The free response of an n-degree-of-freedom LTI system is a sum of at
most n harmonics at the natural frequencies. The draft proves n = 1 directly
(substitution forces omega^2 = 4 and omega^2 = 25 simultaneously).

**Certificate.** For all S with fewer than m degrees of freedom, delta(S) > epsilon,
where m is the number of distinct frequencies in y*.

**Cost** O(1) in the target's spectrum. **Coverage** every topology with fewer than m
components - and crucially, **g(N) grows like the number of such topologies**, which for
a compositional inventory is exponential in m. This is the first candidate with
g(N) -> infinity, so section 5 predicts a crossing here.

**Domain tag** linear, time-invariant, passive, free response, output a linear functional
of the state. Each assumption is a *prediction* a higher fidelity can refute - which is
the draft's own capability criterion.

**One precision that decides soundness, and which M1 must settle first**: does "produce
y*" mean exact generation or generation within tolerance over a time window? An exact
statement is clean; a windowed tolerance statement is a different and harder theorem.
Lambda_2 died of an unstated direction-of-approach question, so this one is settled
first rather than last.

---

## 8. The central experiment

**Measure**: at fixed evidence strength, the cost of **ruling out a region**, as a
function of the design-space size.

    x-axis:  size measure (number of topologies / components)
    y-axis:  cost to rule out (evaluations at L0, simulations at L1/L2)
    curves:  (a) evaluation only   (b) evaluation + certificates   (c) certificates only
    fixed:   requirement, tolerance, confidence, cost unit

The theory (section 5) predicts (a) grows as Theta(g(N)) and (c) is flat. **The
experiment's job is to locate the crossing and measure the exponent, and to test the
prediction that a certificate with g(N) = O(1) produces no crossing at all** - a
falsifiable prediction the theory already makes about the existing Lambda certificate.

Design constraints:
  * the x-axis must grow **combinatorially** in components; a parameter box cannot
  * the certificate must have **g(N) -> infinity**; report g(N), not the fraction
  * the cost unit must be physical and shared across arms
  * L0 -> L1 -> L2 is the **cost ladder**; L2 is where independent checking happens

---

## 9. Milestones, each with a falsifier

| # | milestone | falsified if |
|---|---|---|
| M1 | one certificate that is sound, cheap, class-level, with an explicit domain tag **and g(N) -> infinity** | the direction of approach cannot be pinned down (where Lambda_2 died), or g(N) turns out bounded |
| M2 | a structure representation with a genuine size knob, emittable to Modelica | the space cannot grow combinatorially, or cannot be emitted |
| M3 | the crossing at L0, measured, with the exponent | no crossing in reach, or the measured exponent contradicts section 5 |
| M4 | the crossing reproduced at L1 and L2 with OpenModelica | it moves out of reach, or Modelica cannot express S |
| M5 | the certificate names an invariant, and acting on that name constructs a working structure | the named invariant does not determine a useful repair |
| **M6** | **the real thing, below** | the method does not transfer to a scenario we did not author |

### M6 - a real orchestrator, a real scenario, the whole research flow

The vibration work is ours from end to end (section 2.2), so it can show that the theory
stands up but not that the method works. M6 is where that changes:

  * an orchestrator built on **Cordis**, whose revertible effects and reactive coeffects
    are exactly what a revocable certificate knowledge base needs, and whose hot module
    replacement makes the component inventory pluggable;
  * an **LLM in the loop**, doing the actual work rather than executing a script;
  * the agent runs the **whole research flow** itself - proposing structures, deriving and
    tagging certificates, allocating budget, revoking when a domain is crossed;
  * the **scenario comes from outside**: the structure space and the requirement are given
    by a domain we did not design. Suggested domain: **heat-engine improvement**, where
    the time-scale and energy-path invariants have clean physical counterparts and where
    the target is set by thermodynamics rather than by us.

Success criterion for M6 is not a benchmark number. It is: **the agent produces a
certificate that is sound, domain-tagged, and that a domain expert accepts as
non-obvious, together with a structural change that acts on what the certificate names.**

---

## 10. Risks

1. **The certificates may be shallow.** Mode counting is linear algebra. If every usable
   invariant is of that character, the method reduces to "a few special-case proofs plus
   search". **Most serious risk; attack it first.** Note the mitigation is now sharper
   than before: section 5 says what has to be true (g(N) -> infinity, c_p flat), and
   counting settles it quickly for a candidate invariant.
2. **g(N) may be bounded for every invariant we can find.** Then section 5 predicts no
   crossing and there is nothing to show. This is a real possibility and it is the
   fastest thing to check.
3. **The size axis may not grow fast enough** to put the crossing inside an affordable
   fidelity - the present failure, one level up.
4. **The structure representation may not survive the Modelica boundary**, which would
   make L2 a second Python model, i.e. not independent, removing the strongest evidence.

---

## 11. Scale-up: parallel agents and annotation data

Placed late on purpose; flagged now so it is designed rather than accreted.

Two things must not be conflated:

  * **Training a component of the method.** Excluded. A trained adjudicator is the same
    gate in harder-to-inspect material, and it would make the independent check depend on
    the thing it is supposed to check.
  * **The agent's own self-evolution**, which is a different thing and is explicitly in
    scope.

What large-scale parallel agents plausibly buy:

  1. **Parallel exploration of the structure space**, with the shared certificate
     knowledge base as the coordination substrate: a certificate derived once by one agent
     removes the region for every agent. This is the natural place for the g(N) argument
     to become a systems argument - **the value of a certificate scales with the number of
     agents that would otherwise have had to sample the region.**
  2. **Annotation data as a by-product**, not as a goal: traces of (structure, requirement,
     evidence, verdict, revocation) that are produced anyway, and that can later serve the
     agent's self-evolution. Consistent with the earlier retraction - the data is not the
     purpose of the harness.

Open questions to settle before building any of it: what exactly is annotated; what the
data would be used for if not for training a verifier; how parallel agents avoid
duplicating derivation work; and how revocation propagates across agents without becoming
a consensus protocol. **Detailed analysis deferred - recorded here so the roadmap has a
place for it.**

---

## 12. What this programme will not do

  * Train any model, including a verifier.
  * Insert the researcher's prior into the loop as predicates. The prior is frequently the
    thing that is wrong, and a gate built from it misleads.
  * Treat a certificate as a decision. A certificate is a statement with a domain;
    crossing the domain revokes it, and **revocation is a normal event, not a failure**.
  * Argue from cited authority. The case for certification is structural (sections 4-5).
  * Claim a regime it does not own. Section 5.5 states where sampling is the right tool.
  * Report results from a design space small enough that the crossing is out of reach -
    the mistake of the first six rounds.
  * Treat a self-authored benchmark as evidence of superiority. Section 2.2.
