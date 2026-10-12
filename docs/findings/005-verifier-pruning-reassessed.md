# Finding 005 - Reassessing score-based pruning against 2026 evidence

Status: **correction to Finding 003.** A challenge from the user prompted a re-check,
and the re-check changes the claim. The change is recorded here rather than quietly
patched, because Finding 003 leaned on this point heavily.

## 1. The challenge

The user objected that arXiv 2502.00271 (February 2025) is likely obsolete by
2026-10-12: verifier-guided search is evidently in productive use for hard
mathematics, and OpenAI's agent work on Navier-Stokes was cited as evidence.

The objection is substantially correct, and my earlier use of that paper was too
strong.

## 2. What the 2026 evidence actually shows

**MaxProof (arXiv 2606.13473, MiniMax, June 2026)** is the decisive counterexample.
It trains a Proof Expert by long-horizon RL under a generative verifier, a Verifier
Expert for aligned error finding, and a Fixer Expert for critique-conditioned repair,
then applies population-level test-time scaling over generator/verifier/refiner/ranker
interfaces. Reported outcome: 35/42 on IMO 2025 with the same base model that
otherwise falls short. So verifier-guided search demonstrably scales in 2026.

But MaxProof also documents, at industrial scale, exactly the failure mode
2502.00271 described - and it is worth quoting because it is the authors' own
post-mortem of their previous cycle:

> "a long RL run with a single-judge rubric verifier will, with high probability, end
> in a reward-hacking plateau, not in real capability gains"

Their four canonical hacking patterns include length bias (proofs grew from 3.5K to
10K characters), semantic shortcut ("it can be shown", "after simplification" at
precisely the hard steps), and judge-specific preference. And their stated lesson:

> "a static benchmark evaluation cannot, on its own, distinguish a real capability
> gain from a reward-hacking gain"

So the field's response to unreliable verifiers is not to abandon them. It is to make
them **conservative and multi-layered**: bad-case filtering, solution normalization,
multi-judge parallel scoring, and **pessimistic min aggregation**. Conservative in the
precise sense that the verifier should err toward NOT rejecting.

And MaxProof is explicit that candidates must not be permanently discarded:

> "A candidate that is close to correct should be repaired or re-explored rather than
> discarded."

**On the Navier-Stokes claim.** The claim is contested rather than established. Sources
findable today include "OpenAI says it solved Navier-Stokes. Nobody has seen the
proof", a report titled "OpenAI's 10,000-Agent Navier-Stokes Claim Solves the Wrong
Problem - and the Right One Has a Provenance Controversy", Chinese coverage of a
priority dispute, and multiple Zenodo rebuttals. Whatever the eventual verdict, a
claimed proof that no one can inspect is not evidence that verification works; it is
an illustration of why certification has to be independently checkable.

## 3. What changes in the ECDR position

**Withdrawn:** the claim that score-based pruning is empirically broken and therefore
unusable. It is not. In 2026 it works, at the cost of layered verifier infrastructure,
curated alignment data, and three trained experts.

**Retained, and sharpened:** what 2026 SOTA does with an unreliable verifier is
**soften it and never permanently discard** - repair and re-explore instead. That is
the right engineering answer when no sound refutation is available, which is the
normal situation in mathematics: you cannot cheaply prove that an approach will never
yield a proof.

**The revised claim is narrower and better supported:**

> In physical engineering design, a sound refutation often DOES exist and is often
> cheap. ECDR's contribution is a certifier that converts an expensive soft signal
> into a cheap hard one, and uses it to prune where softening would be unnecessary.

The supporting numbers from this project: the Lambda certificate costs microseconds
and is exact; the same reasoning is unavailable for mathematics, which is why MaxProof
must keep every candidate alive.

This also re-explains Heuresis (Finding 003 s2): six open-ended search strategies,
3,222 runs, zero ideas rated Original, populations that converge under migration. Soft
pruning plus retention is a local search. Hard pruning, where it is available, is the
only thing that stops a population collapsing.

**Corollary for the benchmark.** The relevant comparison is not "certificate versus
score" in the abstract. It is: given a task family where a certificate EXISTS for some
mechanisms and not others, does using it beat the best 2026-style conservative soft
pruner at equal budget? The certificate's value is bounded by how often it exists -
which is why M2's missing proof is now the central theoretical question, not a side
quest.

## 4. Honesty boundary

  * MaxProof's headline numbers come from its HTML rendering with inline maths
    replaced by a placeholder; the numeric tables were not fully recoverable, so only
    prose-stated results are quoted.
  * MiniMax is the developer of the M3 series and reports its own results.
  * 2502.00271 is not wrong; it describes a real mechanism. It is a 2025 study of a
    frozen OVM/PRM in beam search, and 2026 practice has engineered around its
    conclusion. Citing it as the last word was my error.
