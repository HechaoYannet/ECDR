# Finding 049 - Re-anchoring against the roadmap: the harness deviates in three places

Status: an assessment requested after the harness had grown for ten rounds without being checked
against the roadmap's own requirements. **The citations are given with line numbers so they can be
verified.** The harness satisfies the shape of section 6 but not its content: it checks a NUMBER
where the roadmap requires a checkable ARGUMENT, it has no cost axis, and it never asks what a
certificate NAMES.
Reproduce: read docs/ROADMAP.md at the cited lines.

## 1. The citations, as requested

**Independently verifiable, and independent of the search that motivated it** - section 3, line 98:

> a **soundness argument** | checkable by a third party, **independent of the search that motivated it**

**Revocable rather than a gate, and why the domain tag is what does it** - section 3, line 99:

> a **domain tag** | the assumptions under which it holds; **this is what makes it revocable rather
> than a gate**

**Revoked, not edited** - section 6, Layer C, line 370:

> a certificate crossed by a higher fidelity is **revoked**, not edited.

**Confidence operator rather than filter** - section 3, lines 102 to 104:

> it is used as a **confidence operator**, not a filter: without a certificate, confidence
> accumulates by sampling and the conclusion is always "not found yet"; with one, a single
> derivation sets the confidence of an entire family **to zero**.

**A certificate must name the remedy** - section 6, Layer B, lines 354 to 357:

> which invariants are (i) sound, (ii) cheap, (iii) **have g(N) -> infinity**, and (iv) **name a
> structural remedy** - because a certificate that says only "impossible" is a gate, while one that
> says which invariant is violated **tells the agent what to build**.

## 2. Where the proposed framing extends the roadmap rather than citing it

The roadmap says a certificate sets confidence **to zero** - the operator is binary. **Treating it
as a multiplier that need not be 0 or 1 is an extension, and a defensible one**, because section 5.5
already concedes a statistical regime where probabilistic negatives are the right tool and no
crossing exists. **A multiplier is what lets one object straddle both regimes.** But it is not
currently in the roadmap, and it should be written in rather than assumed.

Rollback is squarely supported: line 99 makes revocability the POINT of the domain tag, and line 370
requires revocation rather than editing.

## 3. The three deviations

### 3.1 The harness checks a number; the roadmap requires a checkable ARGUMENT

Line 98 says the **soundness argument** is what a third party checks. My harness has the agent emit
a **scalar** - a V, a Q_H - and the checker **recomputes that scalar by another route**.

**Recomputing the answer is not checking the argument.** It verifies that two implementations agree,
which Finding 048 showed is circular where they share assumptions, and it is why a certificate that
was produced by reasoning and a certificate that was guessed are treated identically.

**Checking an argument means reading it.** A proof is checked by following its steps, not by
re-deriving the theorem. This is exactly what the proposed framing names, and it is closer to line
98 than what is built. **It is also already demonstrated**: Finding 045 put four claimed witnesses in
front of the model with their justifications and it found the defect in two of them and the exact
corrected values. **That was argument-checking, and it worked.**

### 3.2 There is no cost axis, so the harness cannot express the crossing at all

Layer C, lines 368 to 370:

> Proved regions take budget **zero**; unproved regions take sampling budget; the fallback when no
> certificate exists is ordinary non-chronological backtracking; **both live on one cost axis**

The loop has a flat counter of "physics calls" and does not distinguish a proved region from a
sampled one. **So the quantity the entire roadmap is about**, c_p + c_v against g(N) * c_s from
Proposition 2, **has no representation in the code.** Every M6 run so far has been unable to show a
crossing even in principle, because nothing in it knows what a region costs to rule out.

### 3.3 Nothing asks what a certificate NAMES

Layer B (iv) and the M6 success criterion both require it. The harness installs a certificate with a
domain tag and stops. **No field records what the certificate says is missing, and no step acts on
it.** By the roadmap's own words at line 356, that makes what has been built a **gate**, which is
the thing certificates were introduced to avoid.

## 4. The answer on certificates versus heuristics

**The logical question is settled, and settled against heuristics** - section 5.2, Proposition 1 and
line 144:

> Ruling out a region of K structures *with certainty* costs Omega(K) evaluations. **Escaping that
> bound requires an argument about the class, not more observations.** So the real choice for the
> negative conclusion is not "certificate versus heuristic" but **"certificate versus nothing"**.

**But section 2.1, line 60, records a measured fact that cuts the other way:**

> Where a certificate can prune, a plain heuristic reading the same verdict prunes identically |
> **measured**

**Put together, these say something the harness has been ignoring.** The certificate's *pruning
action* is indistinguishable from a heuristic's wherever both apply - that is measured, not
speculated. **The only thing separating them is CERTAINTY.** So a test that measures whether an
agent reaches the right verdict, as every M6 run so far has, **measures the one property the roadmap
already recorded as not differentiating.**

**That is the answer to whether the harness matches the research intent: it tests the pruning, and
the roadmap says the pruning is not the contribution.**

## 5. What has to change

  1. **A certificate becomes an object carrying its soundness argument**, not a scalar. The harness
     records the derivation, not only its output.
  2. **The checker examines the argument.** A model with the argument in context, in a separate
     process and a separate context from the agent that produced it, is a legitimate instantiation
     of "a third party" at line 98 - and Finding 045 shows it is not a formality.
  3. **The verdict is a confidence, and rollback is the default response to a lowered one.** Line 99
     already makes revocability the point of the domain tag; a multiplier is the extension of
     section 2 above and belongs in the roadmap first.
  4. **A cost axis is added**, so that a proved region and a sampled region are comparable, and
     Proposition 2 can be evaluated rather than asserted.
  5. **"Names the remedy" becomes a required field**, and something in the loop acts on it.

**Items 2 and 3 are what was proposed to me and they are right.** Items 1, 4 and 5 are consequences
of the citations that were not in the proposal, and 4 is the one without which none of the rest can
be evidence for the crossing.

## 6. What this does not say

The ten rounds of harness work are not wasted. The orchestrator, the process boundary, the
Cordis-backed revertible effect store, and the demonstrated fact that an agent will audit evidence
when it believes checking is possible - all of that is infrastructure the corrected design needs.
**What is wrong is the certificate representation and the accounting, and both are replaceable
without touching the parts that were verified.**
---

## 7. The certificate-versus-heuristic question, answered from the roadmap

This was asked and left unfinished. The roadmap settles it in two places, and the harness sits on
the wrong side of both.

### 7.1 What the roadmap already measured

Section 2.1 records two results, both marked **measured**:

> line 59: On small problems, score/streak/surrogate pruning is competitive with certification
>
> line 60: **Where a certificate can prune, a plain heuristic reading the same verdict prunes
> identically**

Taken alone these say certificates do not outperform heuristics. **That is the tension.**

### 7.2 And the roadmap's resolution, which is easy to miss

Section 5.2, lines 141 to 144:

> Ruling out a region of K structures *with certainty* costs Omega(K) evaluations. **Escaping that
> bound requires an argument about the class, not more observations.** So the real choice for the
> negative conclusion is not "certificate versus heuristic" but **"certificate versus nothing"**.

**Read line 60 carefully: "a plain heuristic READING THE SAME VERDICT".** A heuristic that reads the
same verdict is reading **the certificate's own bound** - it is the certificate being applied, not a
competitor to it. Of course the pruning is identical; it is the same pruning.

**The competitor is a heuristic WITHOUT the certificate**, and Proposition 1 says it cannot produce
certainty at any cost below Omega(K) evaluations. **So the certificate's contribution is not the
pruning. It is the certainty**, and section 5.5 then delimits where certainty is worth paying for:

> lines 317 to 323: In the regime where a *probabilistic* negative conclusion is acceptable, there is
> no crossing at all and sampling is the correct tool. The method's domain is exactly the regime
> where a **certain** negative conclusion is required: when the cost of a wrong "this structure
> cannot do it" is high, when the space cannot be enumerated, or when the same conclusion must be
> reused across many problems without re-sampling.

### 7.3 So does the harness match the intent? On this question, no

**Every M6 run so far measures the agent's VERDICT - whether it proposed the right bound, whether it
accepted a valid witness, whether it searched.** That is the pruning. **Section 2.1 line 60 says,
as a measured result, that the pruning is not where certificates differ from heuristics.**

**And more decisively: the harness never runs the alternative.** There is no sampling route, no
budget for one, and no cost axis on which the two could be compared. Section 6, Layer C, lines 368
to 370 require proved and unproved regions to "live on one cost axis"; the harness has a flat
counter of "physics calls" and one route. **Without the baseline, "the agent found the certificate"
is a description, not a comparison.**

### 7.4 A correction to the measurement made this round

Step 73 measured the Proposition 2 constants on the real code paths:

| | value | what it is |
|---|---|---|
| c_s | 9.164e-04 s | one transmissibility evaluation |
| c_v | 3.975e-08 s | one certificate check (200,000 in a batch) |
| c_p | 1.000e-06 s | deriving the certificate over the family |
| **(c_p + c_v) / c_s** | **1.135e-03** | the threshold g(N) must exceed |

**So the crossing condition of section 5.3 is satisfied at g(N) = 1.** Condition 1 of the Corollary -
"a crossing exists iff g(N) -> infinity" - is therefore **nearly vacuous as stated**: any predicate
excluding a single structure clears it, because a check is four orders of magnitude cheaper than an
evaluation.

**That does not show the crossing is real. It shows the stated condition is too weak to be
informative.** The content is in the rest of section 5.4:

  * **condition 2 (persistence)**: g(N) = Theta(N) gives a speedup that does not decay, capped at
    1/(1-f) - so covering half the space buys a factor of two;
  * **Finding 011's library**: k = O(log N / log(1/(1-f))) certificates, growing ADDITIVELY per
    decade of N against sampling's multiplicative growth. At N = 6.4e10 and f = 0.001 that is
    24,876 certificates against 6.4e10 evaluations.

**Both of those are comparisons against SAMPLING, not against a heuristic.** They are the real
content, and neither has a baseline in the harness.

### 7.5 What this means concretely

The harness needs one thing before any further M6 run is evidence for anything:

**Two routes, one cost axis.** For a given problem, run the certificate route and the sampling route,
charge both in the same unit, and report the comparison together with which regime the problem is
in - because section 5.5 says that in the probabilistic regime sampling wins outright and there is
no crossing to show.

**Until that exists, the honest statement about M6 is the one section 2.2 already makes about the
vibration benchmark**: it shows the machinery runs and the accounting is honest. It does not show
superiority, because we chose the problem, the baseline - and, at present, the absence of one.
