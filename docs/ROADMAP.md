# Research roadmap

Status: proposed. Naming is deliberately deferred (it is a consequence of the method,
not a wrapper around it).

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

with delta(S) = inf_theta L( F(S, theta; z), y* ) the best error the structure can ever
achieve, and a capability gap being delta(S) > epsilon.

**The whole research lives in that decomposition.** Everything else is machinery for
computing, bounding, or revising one of its two terms.

---

## 1. The central difficulty, stated as a fact rather than a complaint

Search can only ever produce an upper bound:

    search finds theta_hat   =>   delta(S) <= ell(S, theta_hat)

The decision problem needs a lower bound:

    should I abandon S ?     <=>   delta(S) > epsilon ?

**These are different questions, and no amount of search converts one into the other.**
Search can show delta(S) <= epsilon by exhibiting a witness. Search can never show
delta(S) > epsilon, because *every* negative result it produces is equally consistent
with "the structure is inadequate" and "my search is inadequate".

So an agent whose only instrument is search cannot perform the attribution the draft
asks for in sub-challenge 1. Not "performs it poorly" - cannot, in principle. It can
only ever report ell(S, theta_hat), and it has no way to know which term dominates.

This is the reason the research needs something other than better search, and it is a
structural argument, not an appeal to any paper.

---

## 2. What we have actually established, and what follows

### 2.1 Established

| result | status |
|---|---|
| A closed-form infeasibility certificate exists for one mechanism class (passive SDOF: two incompatible bounds on omega_n, Lambda = 0.2903, independently falsified on 7 tasks) | exact, verified |
| That certificate **transfers upward** through a fidelity ladder built so each level only ADDS constraints | exact, verified |
| A certificate's **feasibility** verdict does NOT transfer upward; the 172-240 Hz zone is where the L0 verdict is crossed by L1 | measured |
| Score/threshold/streak/surrogate pruning is cheap and, on small problems, competitive with certification | measured |
| Where the certificate can prune, a plain heuristic observing the same verdict prunes identically | measured |

### 2.2 What that implies

1. A certificate works by being **class-level**: one derivation, a whole region removed,
   cost independent of the region's size.
2. A certificate is a **statement**, and like every statement it holds on an assumption
   set. The assumption set is what makes it revocable when a higher fidelity crosses it.
   The danger is never "provable"; it is **"provable with the domain left unsaid"**,
   which degrades into a hard gate.
3. On problems small enough that sampling is cheap, certification buys nothing. That is
   not a defect of certification, it is a statement about the problem size.
4. **The current bottleneck is the size of the design space, not the number of
   certificates.**

---

## 3. The idea

> **A capability gap should be certified, not searched for.**

A **capability-gap certificate** for a structure family F, a behaviour requirement
(C, epsilon) and conditions z is a statement

    for all S in F :  delta_z(S) > epsilon

carrying three things:

| component | role |
|---|---|
| a **soundness argument** | checkable by a third party, independent of the search that motivated it |
| a **domain tag** | the assumptions (linearity, passivity, single ground path, ...) under which it holds; this is what makes it revocable rather than a gate |
| a **cost independent of abs(F)** | the property that makes it different in kind from sampling |

and it is used as a **confidence operator**, not a filter:

  * no certificate: confidence in "S can do it" accumulates by sampling; the cost per
    unit of confidence grows with the size of the space; and the conclusion is always
    "not found yet", never "cannot be done"
  * certificate: **one derivation sets the confidence of the entire family to zero**,
    at a cost that does not depend on how large the family is, and the derivation can be
    re-checked by someone who does not trust the agent

---

## 4. Why a proof is cheaper, argued structurally

This must be argued from the structure of the two methods, not cited:

    sampling:  cost  ~  (number of candidates that must be examined)
                       x (cost of one evaluation)
                       -> grows with the size of the structure space

    proof:     cost  ~  (cost of deriving the invariant)
                       + (cost of checking it)
                       -> depends on the invariant, not on the space

The two are not on the same axis at all, so they must cross. **The deliverable is the
crossing point**, measured, as a function of a design-space size measure.

A crossing that is asserted is worthless; a crossing that is measured is the paper.

---

## 5. The method: three layers

### Layer A - structure representation

    S = (component inventory, connection topology, boundary relations)
    theta in Theta(S)

Requirements:
  1. a **size measure** that can be swept (number of components, number of topologies,
     number of discrete choices)
  2. **emittable as a simulation model** - if S cannot be turned into a Modelica model
     it is the wrong representation, because L2 must be able to check it
  3. **compositional**: adding a component must be a local operation, or the space
     cannot grow

### Layer B - the certificate layer

A library of **physical invariants of structure classes**, each with the three
components of section 3. Not a fixed taxonomy to be filled in: the research question is
which invariants are (i) sound, (ii) cheap, (iii) **cover an interesting fraction** of
the space, and (iv) **name a structural remedy**.

The last point is the bridge to sub-challenge 2 and is easy to miss. A certificate that
says only "impossible" is a gate. A certificate that says *which invariant* is violated
tells the agent what to build:

| invariant | rules out | names the remedy |
|---|---|---|
| mode / state dimension | structures with too few independent modes | add degrees of freedom (components) |
| energy / passivity | behaviours needing more energy transfer than a passive structure allows | add a source or an active element |
| time-scale / relaxation | responses at a rate the structure's storage and conductance cannot produce | add storage or a conductance path |
| band-tradeoff (waterbed type) | isolation in one band without amplification elsewhere | change the ground coupling topology |

### Layer C - confidence bookkeeping and budget allocation

  * proved regions: budget **zero**, no sampling, retained as a revocation-able statement
  * unproved regions: budget by sampling, and the fallback when a certificate is
    unavailable is ordinary non-chronological backtracking
  * the two must live on **one cost axis** so that "cheaper" means something
  * a proof that has been crossed by a higher fidelity is **revoked**, not edited

---

## 6. The first certificate, worked

The draft already contains it, which is a good sign: it is the right kind of statement.

**Target** y*(t) = 0.7 cos 2t + 0.3 cos 5t, to be produced as the free response of a
passive linear mechanical structure.

**Invariant.** The free response of an n-degree-of-freedom linear time-invariant system
is a sum of at most n harmonics, at the system's natural frequencies. The draft proves
the n = 1 case directly (substitution forces omega^2 = 4 and omega^2 = 25 at once).

**Certificate.**
    for all S with fewer than m degrees of freedom :  delta(S) > epsilon
where m is the number of distinct frequencies in y*.

**Cost**: O(1) given the target's spectrum. **Coverage**: every topology with fewer than
m components - a combinatorial class.

**Domain tag**: linear, time-invariant, passive, free response (no external forcing),
output a linear functional of the state. Each of those assumptions is a *prediction*
that a higher fidelity can refute, which is precisely the draft's own capability
criterion.

**One precision that decides whether the certificate is sound at all**, and it must be
fixed before the certificate is used: does "produce y*" mean *exact* generation or
generation *within tolerance over a time window*? An exact statement is clean (a damped
system cannot emit an undamped two-tone signal asymptotically), while a windowed
tolerance statement is a different and harder theorem. Lambda_2 died precisely because a
direction-of-approach question was left unstated, so this one is stated here as the
first thing M1 must settle rather than the last.

**This is small mathematics.** That is not the point. The point is that it is (i) sound,
(ii) free, (iii) covers a combinatorially large class, and (iv) names the remedy: *add
degrees of freedom*. The research is not "prove hard theorems"; it is **what an agent
must do to produce, tag, check, use and revoke statements of this kind, and whether
doing so beats sampling.**

---

## 7. The central experiment

**Measure**: at fixed evidence strength, the cost of **ruling out a region** of the
structure space, as a function of the space's size.

    x-axis:  size measure of the structure space (number of topologies / components)
    y-axis:  cost to rule out (model evaluations at L0, simulations at L1/L2)
    curves:  (a) sampling only
             (b) sampling + certificate layer
             (c) certificate only
    fixed:   required behaviour, evidence strength (tolerance, confidence), budget unit

Expected: (a) grows with the size measure, (c) flat, (b) tracks (a) below the crossing
and (c) above it. **The deliverable is the crossing point and its scaling.**

Design constraints that make it a real experiment:
  * the x-axis must genuinely grow - a parameter box will not do, the growth must be
    combinatorial in components
  * the certificate must cover a **fraction** of the space, and that fraction must vary
    with size; all-or-nothing coverage makes the curve trivial
  * the cost unit must be physical and shared (evaluations, then simulations)
  * the fidelity ladder L0 -> L1 -> L2 is the **cost ladder**, and L2 is where
    independent checking happens

---

## 8. Milestones, each with a falsifier

| # | milestone | falsified if |
|---|---|---|
| M1 | one certificate that is sound, cheap, class-level, with an explicit domain tag | the direction of approach or the domain cannot be pinned down (this is where Lambda_2 failed) |
| M2 | a structure representation with a genuine size knob, emittable to Modelica | the space cannot be made to grow combinatorially, or cannot be emitted |
| M3 | the crossing curve at L0, measured | the curves do not cross in the reachable range, or the certificate covers 0% or 100% |
| M4 | the crossing reproduced at L1 and L2 with OpenModelica | the crossing moves so far that it is out of reach, or OpenModelica cannot express S |
| M5 | certificate names an invariant, and acting on that name constructs a working structure | the named invariant does not determine a useful repair |
| M6 | the method transfers to a second physical domain (thermal / energy path) | no invariant of the same character exists there |

M5 is the one that connects diagnosis to construction and is therefore the one that
makes this the draft's research rather than a search paper.

---

## 9. Risks, stated plainly

1. **The certificates may be shallow.** Mode counting is linear algebra. If every usable
   invariant is of that character, the method reduces to "a few special-case proofs
   plus search". Mitigation: the claim is about the *agent's behaviour*, not the depth
   of the mathematics, and the crossing experiment measures behaviour. But this is the
   most serious risk and it should be attacked early.
2. **Coverage may be degenerate.** If certificates rule out almost everything, the
   problem is trivial; if almost nothing, they are useless. The interesting regime is
   intermediate and it must be checked before building the full apparatus.
3. **The size axis may not grow fast enough** to push the crossing into reach at a
   fidelity we can afford. This is exactly the failure the current repository suffers,
   one level up.
4. **The structure representation may not survive the Modelica boundary**, which would
   force L2 to be a second Python model, which is not independent, which would remove
   the strongest evidence the method can offer.

---

## 10. What this programme will not do

  * It will not train any model, including a verifier. Training belongs to the agent's
    self-evolution, not to a component that is supposed to be an independent check.
  * It will not insert the researcher's prior into the loop as predicates. The prior is
    frequently the thing that is wrong, and a gate built from it misleads.
  * It will not treat a certificate as a decision. A certificate is a statement with a
    domain; crossing the domain revokes it, and revocation is a normal event, not a
    failure.
  * It will not argue from cited authority. The case for certification over sampling is
    structural (section 4) and the case for the method is experimental (section 7).
  * It will not report a result from a design space small enough that the crossing is
    out of reach. That is the mistake the first six rounds made.
