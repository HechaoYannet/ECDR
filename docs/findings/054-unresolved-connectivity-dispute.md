# Finding 054 - An unresolved dispute: the model's classical connectivity argument against my model

Status: **OPEN. Do not read this as "the model was wrong."** Asked to derive a minimum-units bound
without being given the answer, the model produced the **classical connectivity argument** and a
number that contradicts `network_lp` by 2 units. **Twice before, an LLM disputed my apparatus and
was right** - Finding 043 found a real bug in `network_lp` that way. This one is not resolved.
Reproduce: cd orchestrator && node node_modules/cordis/bin.js --unitsbound.
Raw reasoning: runs/unitsbound_reasoning.txt (99,661 reasoning tokens, 597 s)

## 1. What it produced

Given eight solved cases and one held-out case, after **99,661 reasoning tokens**:

> rule: **"Minimum units = N - K, where K is the maximum number of independent components with
> balanced heat duties. For H1, no proper subset balances, so K=1 and units=5."**
>
> why: "No subset of hot duties (637,654,609) equals a subset of cold duties (1384,318,198), so all
> streams must be in one connected component."

held_out = **5**, claimed **exact**.

**The true value in my model is 3.** So the claim is refuted - or my model is wrong, again.

## 2. Why this cannot be dismissed

**Its argument is the classical one and it is well formed.** For a network with U units on N streams
(including utilities), U = N - C where C is the number of connected components, and each component
must be **balanced** - its hot duties must match its cold duties. If no proper subset of the streams
balances, C = 1 and U = N - 1 = 5.

**That is exactly the reasoning by which Finding 037 first refuted U >= N - 1, and exactly the
reasoning Finding 044 used to explain why the refutation survived** - "a disconnected network needs
only a spanning tree per component". **The model has produced the same argument, applied the
balancing test to the actual duties, found no proper balanced subset, and concluded connectivity.**

**So either the model is wrong, or my model admits networks that the balancing argument forbids.**

**And the record says this must be checked, not waved away.** Finding 043 began with an LLM refusing
a counterexample I offered, saying "the claimed 2-unit network leaves C2 unheated, so hot utility
>= 150 kW". I verified it, and it was right: `network_lp` was letting pool heat reach a stream
no unit touched, and the number was 142.5 where it should have been 150.0. **The identical posture
here deserves the identical treatment.**

## 3. What would resolve it

Find a 3-unit network in my model that attains Q_H_min = 142.5, and check it against the balancing
test by hand: **is its component structure balanced, and does each component respect dt_min
throughout?** Finding 044 argued that a 3-edge graph on 5 nodes is necessarily disconnected, and took
that as the refutation. **If each component also has to be balanced, that argument is incomplete** -
a disconnected network whose components are unbalanced is not a network.

**That is the specific gap to test, and it is the same shape as the gap Finding 043 found**: a
structural condition (connectivity, then balance) omitted from a model that reports a lower utility
than the omitted condition allows.

## 4. The second turn

Told the true value, the model revised to:

> "Fewest units = total cold streams when at most one pinch side contains hot streams; otherwise
> total hot + total cold - 1."
>
> held_out = 3, as a lower bound - **sound** with respect to my model.

**But "sound" here means sound relative to the model under dispute**, so this does not settle
anything either. It shows the model will move when corrected, which is now a familiar result
(Finding 047).

## 5. What is established here

  * The model, unprompted and with 99,661 tokens of reasoning, produced **the classical argument**
    rather than the number my model computes. That is a disagreement between two derivations, not a
    failure to derive.
  * **The model's stated rule is a rule, not a guess**: it names connectivity and balance and is
    checkable.
  * **The project's own history says my apparatus has been wrong before in exactly this way**, once
    in the same file, caught by the same kind of objection.

**The honest status: a 2-unit discrepancy between the classical balancing argument and
`network_lp`, with `network_lp` having already been corrected once for precisely this class
of omission.** Until a 3-unit network is exhibited and checked against balance, **neither Finding
044's refutation nor the classical bound should be treated as settled.**

## 6. Limits

  * One run, one model, one scenario; the reasoning has not been read beyond the headline rule.
  * The eight training cases were produced by the model under dispute, so they are not independent
    evidence - **if `network_lp` is wrong, the training data is wrong in the same direction.**
  * The held-out case's true value 3 comes from `network_lp` and therefore carries the same doubt.
  * Nine reasoning tokens in ten have not been examined; the balancing test may have been applied
    to duties in a way that differs from what the model would defend under questioning.
