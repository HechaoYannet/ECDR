# Finding 003 - What the frontier literature says about Q1 and Q2

Status: evidence synthesis. Sources: 24 arXiv queries, 9 full texts read in depth,
4 independent reading passes. Local corpus: docs/literature/.

The user's framing was that Q1 and Q2 are two sides of one framework: strategic
candidate generation and pruning. The literature agrees they are one framework,
and then says something sharper: **the two sides are not equally supported.** One
of them is named by the closest comparable work as *the* missing capability. The
other has been tried hard, at scale, and shown not to work as a contribution.

---

## 0. The one-paragraph answer

Rest ECDR on **Q2**. Rescope Q1 from "generate candidates in new mechanism
classes" to "route to the right mechanism class, and maintain the inventory that
makes routing possible". Earn the word *open-ended* through certificate-driven
expansion of the **admissible** set, never through a claim about LLM creativity.
And make the pruning signal a **proof**, not a score, because the one large-scale
empirical study of score-based pruning shows it failing catastrophically and
increasingly with scale, while the one paper that prunes soundly reports the
mechanism that makes it safe.

---

## 1. Q2 is the load-bearing half, and it is named as such by others

### 1.1 Heuresis states ECDR's Q2 almost verbatim

Heuresis (arXiv 2606.25198) runs 3,222 scored runs across six gold-standard
open-ended and quality-diversity strategies (greedy, MAP-Elites, Go-Explore,
Islands, Curiosity, Omni) in three domains. Its Section 6.1 identifies the missing
capability as:

> "Search needs a signal that decides, for a novel-but-currently-weak idea,
> whether it is weak because the mechanism itself is bad or because the
> first-attempt execution simply has not been optimized."

That is the seed discussion's Section 5.2, independently restated: the difference
between "no feasible solution has been found yet" and "there is evidence that the
current design space contains no feasible solution".

Heuresis adds that no tested strategy makes this distinction, that this is why
novel ideas are discarded, and that it "calls for a re-design of how research
agents decide what to invest compute in."

There is an asymmetry worth exploiting. Heuresis frames the attribution problem
as a **retention / false-negative** problem and asks for a *predictor* of
refinement upside. ECDR frames the same attribution as a **pruning /
false-positive** problem and supplies a *sound closed-form proof*. A predictor can
be wrong; a proof cannot. That is the qualitative difference Heuresis says it
lacks.

### 1.2 Score-based pruning is empirically broken, and it breaks worse as the problem gets harder

arXiv 2502.00271 ("Scaling Flaws of Verifier-Guided Search in Mathematical
Reasoning") is the ablation that kills any heuristic pruning rule.

The mechanism matters: in verifier-guided beam search, **pruning *is* ranking**. A
valid path ranked below the top-k cut is discarded permanently, with no
certificate recorded and no way back.

Measured degradation of search over plain repeated sampling, DeepSeekMath 7B,
coverage gain at sample size 32 (Table 1):

| Split | OVM at #1 | OVM at #32 | PRM at #1 | PRM at #32 |
|---|---|---|---|---|
| MATH L1 | +11.6 | -3.1 | +8.5 | -11.6 |
| MATH L3 | +21.3 | -15.6 | +12.1 | -42.5 |
| MATH L5 | +7.0 | -23.9 | +2.5 | -37.8 |
| OOD-L5 | +1.2 | -32.8 | +5.0 | -39.1 |

Verifier-guided search is *ahead* at sample size 1 and *far behind* at 32. On MATH
with an outcome value model the crossover happens at **sample size 4**.

Cause, attributed directly (Table 2): 77.1 to 88.6 percent of failures are
**SELECTION** failures, i.e. a valid path was generated and then thrown away. The
proportion rises monotonically as valid paths become sparser (Fig 4).

And the best available mitigation is an indictment: among the fixes the authors
try, the largest gain comes from **discarding the verifier's score entirely** and
relying on simulated reward.

Why this is precisely ECDR's regime: the failure grows as valid candidates become
**sparse** and **out of distribution**. In an escape task the feasible mechanism
is by construction sparse among mechanisms, and every new mechanism class is OOD
relative to all evidence gathered inside the previous one. A pruning rule that is
merely usually right is worst exactly where ECDR operates.

### 1.3 Sound pruning exists, and its primitive is the one ECDR needs

CORE (arXiv 2609.39069) is the constructive counterpart. Its verifier returns
three things, not two:

    accept | (reject, C) | UNKNOWN

where C is a **sound conflict core**: a set of decisions such that *no valid
completion of the instance contains all of C*. The paper calls this "a semantic
nogood". The load-bearing discipline, quoted:

> "Before learning C, the checker must establish that no valid completion
> contains all of C. Reproducing a failure on one complete trajectory is
> insufficient: another continuation might succeed."

Core production is tiered, and the tier that governs admissibility is explicit:

  1. exact (SAT/SMT/CSP, parsers, type checkers)
  2. replay-certified (a sound checker rules out every completion containing it)
  3. heuristic (LLM or learned) - "may guide search but should be soft constraints
     with expiration or confirmation, because hard pruning can destroy
     completeness". Heuristic cores never enter the hard cache.

The **exhaustion core** is the primitive ECDR needs. If every legal alternative
at a decision level has a certified core, the union of those cores eliminates the
**decision level itself** - the analogue given is "eliminating the current
variable in constraint search". Two consequences follow immediately:

  * abandoning a *mechanism class* is exactly an exhaustion core over that class
  * it requires proof over **every** legal alternative, not over sampled points.
    CORE states the trap: "Running out of sampled candidates in one proposal batch
    does not establish exhaustion."

Completeness (Theorem 1) holds under: sound cores, finite branching and depth,
the proposer eventually enumerating every legal candidate at a revisited state,
the search-time verifier never rejecting a prefix of a valid solution, and an
exact final scorer. When cores degenerate to the full prefix, CORE reduces to
chronological backtracking - visible in the ablation as core size 8.9 and jump
distance 1.2 versus 2.7 and 3.8 for the real thing.

Results: median verifier calls reduced 39.8 percent at n=30 and 35.0 percent at
n=36 against chronological repair on 2,000 planted graph-colouring instances with
matched proposals and an exact verifier. On five LLM reasoning tasks the mean gain
over Tree of Thoughts is +2.4 to +3.4 points.

### 1.4 The rule this forces on ECDR

A design route may be abandoned only if all of the following hold:

| # | Property | Concretely |
|---|---|---|
| P1 | SOUNDNESS | Abandonment requires a certificate that no completion within the route's feasible set satisfies the task. Not a low rank, not a failure streak. Exact or replay-certified only. |
| P2 | COVERAGE | Abandoning a mechanism class requires the exhaustion-core form: a statement over the whole class, not over sampled parameter vectors. |
| P3 | SCOPE | The certificate must name the assumptions it depends on, and be minimised (deletion-based replay with re-certification). A certificate that mentions the whole design is worthless. |
| P4 | THREE-VALUED | The evidence source must be able to return UNKNOWN, and UNKNOWN may never hard-prune. Log the abstention rate. |
| P5 | NO LEAF LEARNING | One design failing at L1/L2 is not evidence about the mechanism unless lifted to a sound statement over the class. |
| P6 | BUDGET HONESTY | Budget exhaustion is BudgetExceeded, never infeasibility. Report the two separately. |
| P7 | DOMAIN OF VALIDITY | Every certificate carries the assumptions under which it was derived. Applying an M1 certificate to M2 is an explicitly measured OOD condition, not an assumption. |
| P8 | COMPLETENESS PRESERVED | The fallback when certification is unavailable is plain non-chronological backtracking, never a rank cut. |
| P9 | MONOTONE CACHE | Certified cores cached as canonical key sets with superset eviction; heuristic cores never cached hard. |

ECDR's Lambda certificate is **tier 1** by this taxonomy: exact, closed form,
derived from the mechanism's own transfer function, independent of any budget,
search history, or objective weighting. It sits above the level at which
2502.00271 fails.

**This also rescues the user's premise about mathematics.** The validated agent
strength is not "verifier-guided search" - that is the thing 2502.00271 breaks.
It is **sound verification plus strategic search over certified failures**. The
distinction is the whole ballgame, and it is why the certificate, not the search
policy, is the asset.

---

## 2. Q1 is real but cannot be the contribution, and the reason is empirical

### 2.1 The negative result

Heuresis, 3,222 scored runs, six strategies, three domains:

  * **zero** ideas rated NS 1 "Original" on the five-point Gupta-Prunthi rubric
  * the best rating anywhere is NS 2 "Minor Similarity"
  * strict top-10 intersected with the novel side is **exactly one idea** across
    all three tasks, and empty on two of them
  * the per-task (quality, novelty) Pareto front is **re-occupied, not moved**
  * novel-side *medians* match known-side medians; the deficit is at the peak
  * Islands: all eight converged on rearrangements of the same building blocks,
    and "migration accelerates this convergence rather than counteracting it"
  * Omni had the highest median pairwise embedding distance yet produced no
    novelty: **diversity is not novelty**

Corroboration from AlphaEvolve (2506.13131): it *does* demonstrate component
introduction at code level (its diff example adds three ResNet blocks and swaps
Adam for AdamW). It demonstrates **mechanism-class introduction nowhere**, and
it has **no discard, restart, or abandon rule at all** - selection is score-only.
Its own stated limitation: "it handles problems for which it is possible to devise
an automated evaluator". Its abstraction level is a human configuration choice.

Every search mechanism in both papers is a **steering** device over a fixed space:
score selection, novelty gates, curiosity weights, island migration, QD grids on
**hand-defined** axes. Heuresis states the architectural gap plainly: "every
strategy we tested delegates idea generation to an LLM ideator and prunes
generated ideas on a first-attempt score."

### 2.2 What Q1 becomes

Given the above, Q1 survives only in this form:

> **Q1 (rescoped): given a per-task mechanism inventory, route the design to the
> mechanism class whose feasible set contains a solution - and maintain the
> inventory as an explicit, versioned, certifiable artefact.**

This is a decision problem, not a generation problem, and it is exactly what the
M1/M2/M3 ladder already is. The empirical asymmetry between the two mechanism
classes is real and measurable: M1 and M3 differ by **one term in the numerator**
of the transfer function - the damping feedthrough - and that single term is what
makes the task provably unsolvable for M1 and solvable for M3. Mechanism class is
therefore not a narrative device; it is a decision-relevant unit with a
mathematical signature.

*Open-ended* is then earned the only defensible way: the agent may propose an
inventory extension, but the extension is admissible only once an accompanying
certificate or witness is produced. Expansion of the **admissible set**, certified
- not a claim about creativity.

---

## 3. The framing the evidence actually supports

Both halves remain, but they carry different weight and different epistemic status:

| | Q2 - pruning | Q1 - generation |
|---|---|---|
| Status in the literature | named as *the* missing capability (Heuresis 6.1) | tried at scale, negative result |
| Epistemic status of the signal | sound proof available (Lambda) | no reliable signal; diversity does not yield novelty |
| Failure mode if done naively | catastrophic, grows with scale and sparsity (2502.00271) | populations converge; zero Original ideas |
| ECDR's role | **primary contribution** | routing + inventory maintenance |
| What must never be claimed | that a score or a streak is evidence | that the agent invents mechanisms |

The unifying object is the **mechanism-vs-execution attribution problem**: given a
failing design, decide whether the mechanism class is inadequate or the execution
within it is merely unoptimised. Heuresis names it and lacks a signal. 2502.00271
shows that a learned signal is unsafe. CORE supplies the discipline that makes a
signal safe. The Lambda certificate is a worked instance of the safe kind, for one
mechanism class in one physical domain.

---

## 4. What is now closed off, and what remains

### Closed off - do not claim these

  * "physics-in-the-loop" / "closed-loop with physical verification" as novelty.
    Physics-in-the-Loop (IJCAI 2026) and The AI Engineer (2608.21976) both hold it.
  * "verification-closed engineering design". 2608.21976 says so explicitly and
    deliberately: "Unlike open-ended generative AI systems...". It also holds a
    real China Classification Society Approval in Principle on a 20 MW floating
    wind foundation, beating a human baseline by 8.1 percent on steel mass and
    unit capital cost.
  * **"certifiable" without qualification.** 2608.21976's certificate is a
    *fitted* surrogate: an Automated Reviewer calibrated on 11 reference projects
    against a regulatory channel (Spearman 0.717, MAD 3.9 points), with the
    threshold set at the 90th percentile of regulator-passed projects, and the
    gate itself validated on a **single** submission - which then passed only
    after three rounds of formal clarification and design refinements. The
    certified artefact is not the as-generated one.
  * cost-aware / budget-aware evaluation. SimulCost (ICML 2026) owns it.
  * diverse candidate generation, quality-diversity, multi-agent critics. Design
    fixation in GenAI is a named, measured phenomenon with published instruments
    (novelty proportion P_n = unique/(unique+shared); CLIP embedding pairwise
    distance with Mann-Whitney; ChatGPT 67.4 percent vs Red Dot 78.2 percent).
  * "expanding the search space" as a slogan. 2608.21976 already uses that phrase
    for BESO topology evolution.
  * automating FEA or CAD generation. VFEAgent and the CAD-agent line own it.

### Remains open - five claims, strongest first

1. **Certified infeasibility as a first-class action.** Both competitors terminate
   on *sufficiency* gates: 2608.21976 needs a composite score above a threshold
   with no sub-score below a floor; 2605.19717 needs all checks to pass within 10
   iterations. Neither represents "this design space cannot succeed". 2608's
   recovery path is replan(theta, F_p), "a predefined set of corrective actions"
   over three hierarchies, with backtracking over the *topology design domain*,
   not the physical mechanism. 2605.19717 names the gap verbatim in Section 9.2:
   future work should detect "when a CAD design becomes **unrecoverable**".
   Lambda = 0.2903 is a statement about *(mechanism, task)*, not a score about a
   candidate: the static-sag bound and the isolation-band bound are incompatible
   by a factor 3.445.
2. **Certificate independence.** Lambda is invariant to budget, search history and
   objective weights, and re-derivable from the returned design vector alone.
   2608's gate is fitted to regulatory outcomes and was validated on n = 1.
3. **Mechanism-class change as a distinct, certified action.** Both action spaces
   are geometry- and parameter-only within a fixed physical mechanism.
4. **A ground-truth escape ladder.** M1 provably infeasible (Lambda = 0.2903);
   M2 not feasible in the scanned family (best peak-feasible in-band |T| = 0.3044
   against a limit of 0.1, 331,776 combinations); M3 feasible with an explicit
   witness. No competitor has a task with *proven* infeasibility of the initial
   class.
5. **Diagnosis accuracy against injected ground truth**, plus the ablation that
   isolates evidence from inventory size.

---

## 5. Revised thesis

> An engineering design agent given a **fixed mechanism inventory** and a **fixed
> evaluation budget** escapes a provably inadequate design space more often, and
> at lower cost, when it prunes on **certified infeasibility** than when it prunes
> on performance scores, failure streaks, or surrogate predictions - and the
> advantage grows as the feasible mechanism becomes sparser.

Three things make this falsifiable and fair:

  * the inventory is held **fixed** across arms, so the experiment measures
    evidence use, not inventory size
  * the certificate is a **separate code path** from anything the agent authors
  * the primary endpoint is **escape rate**, with the cost ledger reported
    alongside so that "escaped" cannot mean "spent more"

Where the frontier leaves the two competitors, and where ECDR enters:

    2608.21976   fixed pipeline;  sufficiency gate;  mechanism constant;
                 certificate = fitted surrogate;  validated on n = 1
    2605.19717   geometry only;   sufficiency gate;  mechanism constant;
                 names the gap: "unrecoverable"
    ECDR         mechanism inventory;  certified infeasibility gate;
                 certificate = closed-form proof;  ground-truth escape ladder

---

## 6. Integrity requirements inherited from the literature

These are not optional; each is backed by a documented failure in a 2026 paper.

1. **Never accept a self-reported verdict.** Re-derive the certificate from the
   returned design vector with a frozen, independently versioned checker.
   (2608.28639: proofs passed compilation *and* the standard source-level sorry
   scan while depending on sorryAx, detectable only by kernel-level axiom audit.)
2. **Search amplifies hacking.** The same paper: whole-proof sampling lost 4
   proofs at PAB@32 and 8 at PAB@128 to the exploit, while MCTS lost 11 and 19.
   ECDR explores more mechanism classes than a local optimiser, so it will find
   more exploits. Measure audit rates **per arm**, never assume them equal.
3. **Separate "solver converged" from "constraint satisfied".**
4. **Confirm by counterfactual ablation.** If the agent claims M3 is feasible,
   disable the claimed witness term and confirm the design collapses.
5. **The agent must not author its own certificate.** Generation and checking are
   separate code paths.
6. **Pin and hash the whole verification stack.** The sorryAx bug was documented
   at Lean 4.9.0 and still reproduced at 4.15.0; "fixed upstream" is not safe.
7. **A clean domain is not a sound harness.** The exploit vanished on physics
   benchmarks purely because the model lacked domain familiarity.
8. **Plant traps; measure trap density per domain.**
9. **Report unaudited and audited numbers side by side**, never only the audited.
10. **State what the check does not establish.** L2 independent numerical
    validation is not experimental physical validation.
11. **Hidden conditions must include a different environment, not just seeds.**
    Heuresis: 13 runs decoding game objects from the observation tensor were
    judged valid at submission time and were caught only by held-out evaluation.
12. **Pair every escape claim with the cost ledger.**
13. **Do not tune on the domain you claim transfer to.** BOCoDe: "the best method
    on synthetic problems can rank last on engineering ones"; feasibility falls
    from 0.94-1.00 on synthetic to 0.51-0.91 on engineering.

---

## 7. Reusable infrastructure (do not reinvent)

  * **BOCoDe** (2608.15073): 307 problems, 159 engineering, 5 formulation classes,
    31 reference algorithms behind one CLI, unified evaluate(x) -> (obj, cons),
    per-problem JSON metadata with provenance, and a full statistical ranking
    protocol (median best-so-far, Friedman + Iman-Davenport + Nemenyi, Holm
    Wilcoxon when n < 20). Caveats: package not released until acceptance;
    TabPFN-3 weights are non-commercial. It has **no mechanism axis**, which is
    exactly ECDR's contribution, and its 31 algorithms are the "same design
    operators for strong baselines" the seed discussion demanded.
  * **AlphaEvolve's evaluation cascade** maps one-to-one onto the L0/L1/L2 ladder:
    advance to the next stage only if all earlier stages were promising.
  * **CORE's three-valued verifier interface** and its exhaustion-core pattern.
  * **The three-stage audit protocol** from 2608.28639: lexical screen (never
    sufficient) then independent re-derivation then counterfactual removal.
  * **The design-fixation instruments**, with the unit replaced: measure the
    distribution of proposed mechanism class over the last N failures instead of
    word or embedding diversity.
  * **The ablation shape** from 2605.19717: disable one component, hold everything
    else, report a contingency test (their headline: FEA feedback on 59.0 percent
    inside target safety-factor range versus 22.2 percent without, Fisher exact
    p < 0.01).

---

## 8. Immediate consequences for the work plan

1. Rewrite the README thesis to the falsifiable form in Section 5, with the
   competitor table and the closed-off list.
2. Add the **mechanism inventory** as a first-class, versioned artefact, and
   implement the **certificate checker as a separate code path** from any agent
   code.
3. Build the **task family** by sweeping the band edge: Lambda < 1 gives M1
   infeasibility, and the passive 2-DOF threshold sits between 110 and 160 Hz.
   Each task carries a ground-truth minimal mechanism class.
4. Make the headline experiment the **ablation**: identical inventory, identical
   budget, pruning signal varied (certificate versus score threshold versus
   failure streak versus surrogate prediction).
5. Report escape rate **stratified by feasible-mechanism sparsity** and by OOD
   transfer (applying an M1 certificate to M2/M3), following 2502.00271 Fig 4.
6. Extend the certificate layer: M2 currently has necessary conditions
   (Lambda2 = 1.006420, so the absorber mass fraction is capped at 0.006379) but
   no proof. Closing that gap converts "no witness found" into a theorem and is
   the single highest-value theoretical task.
