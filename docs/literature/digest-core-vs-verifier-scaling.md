1. WHAT THE PAPER ACTUALLY DOES (mechanism level)

**CORE (2609.39069v1).** Proposer emits one structured decision at a time (JSON id/decision_type/value/depends_on); the controller owns stack, ledger, learned cores; prose is non-binding. Verifier returns accept / (reject, C) / **unknown**, C = canonical decision-value keys.

*Def. 1 (sound conflict core)*: C is sound for x iff **no valid completion contains all of C** — "stronger than 'these steps look suspicious'… a semantic nogood." Any such certificate works (constraint violation, a failed test's dynamic slice, a solver's unsat core); learned verifiers' cores "are not covered by exact guarantees."

*LearnAndJump*: minimize C by deletion-based replay (**≤8 extra checker calls**; else keep the non-minimal sound core) → insert, **delete stored supersets** → backjump to the level before C's most recent member → truncate → mark that value tried. A stored core "rejects later supersets regardless of the order of decisions outside C."

*Exhaustion cores* (§4.1, the structural primitive): if all legal alternatives at a level are exhausted and each v_i has certified core C_i ∋ (x,v_i), the exhaustion core is ∪(C_i \ {(x,v_i)}); any completion retaining x must pick some v_i, so **the level itself is eliminated** — "eliminating the current variable in constraint search."

*Discipline*: "Reproducing a failure on one complete trajectory is insufficient: another continuation might succeed." "**Running out of sampled candidates in one proposal batch does not establish exhaustion**." RejectLeaf (complete state failed by the *final* scorer) "does not cache a conflict without a sound explanation."

*Tiers*: exact (SAT/SMT/CSP, parsers, type checkers) / replay-certified / heuristic — the last is "soft constraints with expiration or confirmation, because hard pruning can destroy completeness," never hard-cached. Only sound cores get the formal guarantee.

*Theorem 1*: sound cores; finite branching/depth; the proposer eventually enumerates every legal candidate at a revisited state; **the verifier never rejects a prefix of a valid solution**; exact final scorer; no budget interruption ⇒ never prunes a valid solution.

**2502.00271.** Step-level beam search: N candidates/step, OVM/PRM rank, top-k proceed. **Pruning IS ranking** — a low-ranked valid path is permanently discarded, no certificate, no recovery. "Verifier failure" = the verifier "erroneously prune[s] all valid paths."

2. THE PRECISE EVIDENCE

**CORE testbed:** planted 3-coloring, 500 graphs × 4 sizes = 2,000; identical candidate ordering for all methods; exact verifier; 100,000-call cap. Median verifier calls (Chron/CORE-BJ/CORE): n=18 32.0/31.0/31.0; n=24 95.0/70.0/69.0; n=30 223.5/147.0/134.5 (**−39.8%**); n=36 267.0/189.0/173.5 (**−35.0%**). Mean n=36: 546.0→235.4. Memory's gain is claimed as 5.7/8.5/8.2%, but only 8.5% (n=30) and 8.2% (n=36) reconcile with Table 1 — n=24 is 70.0→69.0 = 1.4%. All 2,000 solved by all three. Proposer sensitivity (n=30, 200 paired): weak 236.0/149.5/135.0, strong 133.5/92.0/90.5 — memory's value shrinks with a good proposer.

**Five tasks** (GSM8K 500, MATH-500 500, 24-Game 200, Blocksworld 200, HumanEval 164); Qwen2.5-7B-Instruct / Qwen3-8B; 4 candidates/decision, ≤24 decisions, 16,384-token + 32-call budget; task-specific deterministic checkers returning unknown on parse failure. Mean success Qwen2.5: **75.9 vs ToT 72.5**, Self-Refine-4 65.1, SC-8 64.4, CoT 55.1; 10.9 vs 18.6 calls; 9.1k vs 14.2k tokens. Qwen3-8B: **84.2 vs 81.8**; 12.0 vs 19.0 calls; 6.0k vs 7.0k tokens. Blocksworld largest (+6.0/+5.0); HumanEval flat (72.0 vs 70.1; 76.2 vs 75.0).

**Ablations** (Qwen2.5): CORE 75.9/10.9, core size 2.7, jump 3.8; no memory 73.8/12.7; no backjumping 72.9/15.4; **full-prefix conflicts 71.8/16.1** (size 8.9, jump 1.2); soft heuristic cores 74.9/14.3.

**2502.00271:** GSM8K, MATH, OOD-L4 (train L1,2,3,5 → test L4), OOD-L5 (train L1–4 → test L5); Mistral 7B, DeepSeekMath 7B; OVM + PRM; beam size and candidate count each scaled with the other fixed at 8; 3 repeats; metric = coverage. **Crossover: PRM on GSM8K >20% above repeated sampling at sample size 1, inferior by 16, ~5% below at 32; OVM on MATH overtaken at 4, ~20% behind at 32.** At 32 gaps run ~−10% (OVM/GSM8K) to ~−30% (PRM/MATH); worst cell PRM OOD-L4 −46.1%. Table 2: **selection failures 88.6/83.5/80.0/77.1/84.3/81.2%** vs generation 11.4/16.5/20.0/22.9/15.7/18.8. Fig 4: failed selection stages rise monotonically as valid-path sparsity falls. Mitigations (Table 3, GSM8K/MATH/OOD-L4/OOD-L5): softmax selection temp 1 → +2.0/+5.4/+11.8/+10.3; Monte Carlo rollout weaker (+1.3 to +6.0, negative on MATH at λ≤0.75) — "the highest accuracy gain is achieved when relying entirely on the simulated reward, without incorporating the verifier-predicted score."

3. STATED AND IMPLIED LIMITATIONS

**CORE:** no Limitations section. Stated: guarantees conditional on soundness; learned cores "not covered by exact guarantees"; full-prefix cores degrade to chronological; "Verifier calls alone do not measure wall-clock cost: structured generation and core replay add work beyond a baseline answer check." Implied: the 35–40% headline is a synthetic, exact-verifier, matched-proposal testbed; real-task gain is +2.4/+3.4 points with HumanEval flat; memory's value evaporates with a strong proposer; the interface presumes canonicalizable, dependency-annotated decisions.

**2502.00271:** the only stated limitation is "We do not investigate the impact of scaling verifier sizes and the size of the training dataset." Implied: rank-based beam search only; failures measured by coverage, which they note equals precision "in applications with oracle solution selection, such as automatic theorem proving"; mitigations ≤11.8%, and the best variant discards the verifier.

4. WHAT IT MEANS FOR ECDR

**Reconciliation: not a conflict — 2502.00271 demonstrates what CORE's assumption (iv) buys.** (1) exact vs learned verifier (CORE concedes learned cores lose the guarantee); (2) CORE accepts-or-certifies with an explicit **unknown** channel, while ranking deletes, so no unknown-equivalent exists; (3) CORE assumes the verifier never rejects a prefix of a valid solution — ranking violates exactly that; (4) ledger + backjumping + re-enumeration vs permanent discard; (5) graceful degradation vs catastrophic, scale-growing loss, worst when valid paths are sparse and OOD; (6) neither suffices alone.

**Closed off:** pruning on a score, a failure streak, or an L1 surrogate's verdict is a learned verifier — 2502.00271 is the ablation that kills it, CORE files it under tier 3 (soft, expiring, never hard-cached). Their damage grows as valid candidates get sparse and OOD: exactly the escape regime, since the feasible mechanism is sparse and every new mechanism class is OOD to evidence gathered inside M1.

**Open:** **neither paper prunes a mechanism class.** CORE's strongest structural primitive is the exhaustion core (eliminate a decision level, only with coverage over all alternatives) plus order-independent nogoods; 2502.00271 has no structural representation — "valid-path sparsity" is statistical, not certified. Mechanism-class infeasibility with a coverage condition is unoccupied; ECDR's Λ<1 certificate is CORE tier-1, **above** the level where 2502.00271 fails.

5. CONCRETE INGREDIENTS WORTH BORROWING

1. **Three-valued interface** accept/(reject,core)/unknown — unknown lets L1 surrogates and LLM judgement *guide* without hard-pruning; log the abstention rate.
2. **Exhaustion-core pattern for mechanism abandonment** — prove infeasibility over the class's whole feasible parameter set, never sampled points.
3. **Two abstention rules** — a design failing L2 yields no cached conflict; BudgetExceeded ≠ infeasibility.
4. **Deletion-based core minimization, ≤8 checker calls**, re-certified per removal → reveals *which assumptions* (mass budget, actuator authority, bandwidth) the infeasibility rests on.
5. **Canonical keys + superset-eviction cache** (sorted hashes, inverted index), order-independent; keys encode type, dependencies, occurrence identity — not surface text.
6. **Report core size and jump distance**; full-prefix cores (8.9, jump 1.2) are the failure signature — analogue: certificate scope vs task constraints.
7. **Matched-proposal testbed** — planted solvable instances, deterministic noisy proposer, identical candidate ordering for all methods, hard call cap, paired instances.
8. **Budget-matched baselines** reporting realized cost on both axes.
9. **Sparsity- and OOD-stratified reporting** — an M1-derived certificate applied to M2/M3 is an explicit OOD transfer experiment.

**ECDR PRUNING RULE — abandon a route only if all hold:**

- **P1 Soundness** — a certificate that no completion in the route's feasible set satisfies the task; a semantic nogood, not a rank or a streak.
- **P2 Coverage** — abandoning a mechanism class is an exhaustion core: proof over every legal alternative/parameter, never sampled points.
- **P3 Scope/minimality** — name the assumptions the certificate depends on; minimize by re-certified deletion; log full-scope certificates as degenerate.
- **P4 Unknown channel** — the evidence source can return unknown, which never triggers hard pruning, only soft expiring guidance.
- **P5 No leaf-level learning** — a completed design failing L2 is not evidence about the mechanism unless lifted to a sound statement over the class.
- **P6 Budget honesty** — exhaustion is unknown/BudgetExceeded, never infeasibility; report the two separately.
- **P7 Domain of validity** — certificates carry derivation assumptions (linearity, SDOF, passivity, actuator authority); applying them outside is unsound and a measured OOD condition.
- **P8 Completeness preservation** — pruning must not remove the escape route; the fallback is non-chronological backtracking, never a rank cut.
- **P9 Monotone caching** — canonical key sets, superset eviction, order-independent; heuristic cores never hard-cached.