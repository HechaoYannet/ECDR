# Finding 048 - What the checker is, and which of these results are circular

Status: a clarification forced by a question that had no good answer as the work stood. **The
heat-domain runs test the PIPELINE, not the CLAIM.** The checker is an algorithm rather than a
stored answer, but in that domain it is the SAME algorithm as the ground truth, so the loop
demonstrates agreement between two implementations and not an independent verification. Three
things in this stretch are non-circular and one of them is decisive.

## 1. The question

*"Where does the external checker come from? If we computed the answer in advance, this has no
meaning."*

It is the sharpest question asked in this project, because the answer is partly yes.

## 2. The checker is an algorithm, not a lookup - that half is clean

`unit_check[[/B]] and `checkUtilityBound[[/B]] accept ANY stream set and compute the bound from
scratch. **Finding 042 is the evidence**: six scenarios drawn from a seeded generator during that
session, whose Q_H_min did not exist before it ran. The checker judged those, and I did not know
the numbers in advance.

So the checker is not a table of precomputed answers. That distinction is real and it matters.

## 3. But the worry lands, and here is exactly where

**In the heat domain the checker and the ground truth are the same algorithm.** Q_H_min IS the
problem table's output, and the checker IS the problem table.

So the loop is: the agent computes X with its own implementation, the checker computes X with
another, and they agree. **That is a consistency check between two implementations, not an
independent verification.**

Concretely, this result carries almost no information:

> "the model proposed exactly Q_H_min, 6 times out of 6"

**Since Q_H_min is BY DEFINITION the problem table's output and the checker IS the problem table,
that exact agreement is guaranteed by both sides using the same method.** It shows the model can
perform pinch analysis. **About certificates it shows nothing at all.**

## 4. What is not circular

**Three things, and the third is decisive.**

**(a) The six random scenarios.** Those numbers did not exist before the run and nobody had
computed them. The checker decided them. This is a real test of the checker's generality, though
not of the certificate idea.

**(b) The cost claim of roadmap section 5.** A certificate excludes K structures with O(1) proofs
where search needs Omega(K) evaluations. **That is a theorem about cost and it does not depend on
who knew what.** It is the part of ECDR that is immune to this objection.

**(c) Finding 043: the checker was WRONG and I did not know.** I was certain the two-unit network
attained 142.5. The truth was 150.0. **The counterexample came from a computation and it overturned
a belief I held.** This cannot be circular - had I known the answer, I would not have written the
model that got it wrong.

That is the strongest epistemic event in the whole heat-domain stretch, and it happened because
the agent read a witness adversarially, not because the checker knew the answer.

## 5. The structural criterion

**A certificate is meaningful when BOTH hold:**

  * **(a) checking is cheaper than the search it replaces**, and
  * **(b) the checker decides without our having precomputed the instance.**

**The heat utility certificate satisfies both.** Pinch analysis is O(N log N); enumerating networks
is super-exponential; and no instance is precomputed. **But it is a known algorithm, so the
agent's contribution to it is nil.** The certificate is real; nobody derived anything.

**A unit-count certificate would be a genuine derivation** - it is not in any textbook in the form
the corrected model needs - **but its check REQUIRES the enumeration.** Checking costs what the
search costs, so there is no crossing, and by ECDR's own cost criterion (roadmap Prop 2) such a
certificate is worthless.

**So the heat domain can host a test of the agent and the orchestrator. It cannot host a test of
the crossing.**

## 6. The same objection applies to vibration, but it lands differently

We derived C1 to C4 by hand. We knew those. So "we knew the answer" is true there too.

**But the derivation and the check are different computations there, and that is the difference
that matters:**

| | derivation | check |
|---|---|---|
| heat, as set up here | pinch analysis, a known algorithm | pinch analysis, **the same algorithm** |
| vibration | a bound proved by hand, e.g. Rayleigh | **evaluate the bound on a specific structure and compare with its actual transmissibility** |

**In vibration the certificate is a theorem and the check is an evaluation on an instance.** They
share no code path and no answer. In heat I collapsed the two into one.

**And the derivation being ours is not a defect of the same kind**: a derived bound can be wrong in
ways an evaluation exposes, which is precisely how Finding 001's Lambda_2 was downgraded and how
Finding 014's second-order claim was refuted.

## 7. What this changes

**Reclassification, not retraction.** Findings 039 to 047 stand, with their scope corrected:

| finding | what it actually shows |
|---|---|
| 039, 040 | the orchestrator runs; the API behaves as documented |
| 041, 042 | the agent executes a known method exactly, on instances it cannot have memorised |
| 043, 044 | **the agent audited a witness and overturned MY belief** - non-circular |
| 045 | the agent audits well when asked |
| 046, 047 | it checks itself when it believes a check is possible; an unreachable checker forfeits that |

**None of them is evidence for the crossing. Together they are evidence that the pipeline is real
and that the agent behaves in ways the architecture can rely on - which is a precondition for the
crossing being worth measuring, not a substitute for it.**

## 8. The consequence for M6

M6's stated success criterion is a certificate that a domain expert accepts as **non-obvious**,
together with a structural change acting on what it names. **Nothing in the heat-domain work meets
that bar, because everything the agent produced is in the textbook.**

Two ways forward, and they are not equivalent:

  1. **Accept M6 as a pipeline demonstration** and stop claiming more for it. The crossing is
     measured in vibration, where the certificates are derived bounds and the checks are
     evaluations.
  2. **Find a heat certificate that needs deriving AND is cheaply checkable.** None has been found.
     If none exists, that is itself a result worth recording: **the domain was chosen to avoid
     self-confirmation and delivered a different kind of self-confirmation instead.**

**The non-circular test that is actually available**: ask the agent for a bound **we do not have** -
the corrected minimum-units relation, which Finding 044 refuted the textbook version of and did not
replace. **We cannot precompute the answer because we do not know it.** The check is enumeration,
so there is no crossing, but there is a genuine derivation to test.

## 9. What this does not change

The project's central mechanism is untouched. **Search returns upper bounds; a certificate decides.
No amount of search converts one into the other.** Findings 043 and 044 make that sharper rather
than weaker: my model was the search side, it was wrong, and the only thing that could have caught
it was a computation that did not share its assumptions.

The question asked was about **whose knowledge makes a result meaningful**. The answer is that it
is not knowledge of the answer that matters, but **whether the check shares assumptions with the
thing it checks**. Two implementations of one algorithm do not.
