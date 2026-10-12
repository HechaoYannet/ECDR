# Finding 009 - Centre-of-gravity correction

Status: **the previous six rounds optimised the wrong object.** This document records
the correction, the verified defects that came out of an independent review, what
survives, what is downgraded, and what the experiment must become.

Source of the correction: docs/CONSENSUS.md, produced in a separate session, plus a
user-supplied draft (引言与理论背景_中文初稿.md).

## 1. The drift, stated precisely

The draft defines the design object as

    D = (S, theta),   S = component types + connection topology + boundary relations
                      theta in Theta(S) = the continuous parameters S permits

and the research question as: **can an agent recognise a capability gap in the current
structure and construct a structure that closes it?**  The failure of interest is a
STRUCTURAL gap delta(S) > epsilon, with the key decomposition

    ell(S, that) = delta(S) + [ ell(S, that) - delta(S) ]
                   ^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                   structural   search has not closed it yet
                   gap

What the repository actually built was: a **fixed topology**, **2 to 5 continuous
parameters**, and **frequency-domain scalar constraint satisfaction**.  The topology
never varied.  M1 has 2 parameters, M2 has 5, M3 has 2 or 3.  So the "mechanism
switch" was a switch between two fixed parameter boxes, not the construction of a
structure.

Those are not the same object, and the difference is not cosmetic: the object, the
definition of failure, and the form of the answer all differ.

**The consequence is the one that matters.**  CONSENSUS section 17: the binding
bottleneck is not that there are too few certificates, it is that **the problem is too
small**.  In a 2-to-5-dimensional fixed-topology box the experiment stays permanently
to the left of the crossing point, so the value of a proof relative to a heuristic
cannot be measured there at all.  Rounds 4, 5 and 6 measured something real about
tooling and nothing about the thesis.

This is my error and it is recorded as such rather than framed as a detour.

## 2. Verified defects from the independent review

### 2.1 L1 objective sign - FIXED and verified

ecdr/l1/problem.py evaluate() accumulated

    worst_obj = max(worst_obj, -in_band)

The objective is maximised and the stored value is -in_band, so the worst case over
the perturbation box is the MINIMUM.  Taking the maximum optimised the **most
optimistic** direction in the box.  Reproduced exactly on f_low = 210 Hz, M1,
design [111.86361, 0.590427]:

| quantity | value |
|---|---|
| per-direction in-band abs T | 0.095015, 0.106220, 0.097152, 0.097869, 0.107885 |
| old evaluate() returned | 0.095015 (the best direction) |
| worst direction | 0.107885 |
| verify_l1 with 24 directions | **0.110556**, fails the 0.1 target |

Fixed by switching to min AND moving the accumulator from -inf to +inf.  The second
half matters: min with an -inf initialiser silently returns -inf, which is what the
first attempt at the fix did, and the check script caught it.  After the fix
evaluate() returns -0.107885 and the reproduction passes.

Scope: **L1 only.**  ecdr/bench/problem.py has no multi-direction reduction and is
unaffected, so findings 001 through 008 and the L0 ablation stand.

### 2.2 Search and verification use different perturbation direction sets

The search optimises the worst over 5 fixed directions; verify_l1 draws 24 fresh
random directions on a different grid (1500 points from 0.05 to 1e5 versus 8000 from
0.02 to 2e5).  Both estimate a worst case; they are not the same worst case.  Measured
gap: M2 at 210 Hz gives 0.09869 from the search, which passes, against 0.10558 to
0.10946 from verification, which fails.

This inflates the "not escaped" counts.  It is a design question, not a coding error,
and CONSENSUS marks it undecided, so it is flagged here rather than changed.

### 2.3 The certificate is nearly inert in the current experiment

Verdict census over the six L1 tasks: infeasible 1, feasible_at_l0_only 5, unknown 10.
Trace comparison at f_low = 150, 180, 210 Hz:

| f_low | plateau trace | certificate_hybrid_L1 trace |
|---|---|---|
| 150 | M1 8 gen/144, M2 8 gen/288, M3 success at 336 | M1 **pruned at 0**, M2 8 gen/144, M3 success at 192 |
| 180 | as above | **identical** |
| 210 | as above | **identical** |

Where the certificate can hard-prune, a pure heuristic that observes "infeasible"
prunes identically; where the certificate could discriminate, it has no certificate to
offer and degenerates to a heuristic.  So the honest reading of Finding 007's
"21 percent better on wasted budget" is that it comes mostly from **evaluating the
certificate before the search object is constructed**, not from the certificate's
content.

This is consistent with section 17 and is the strongest internal evidence that the
problem, not the certificate layer, is the bottleneck.

## 3. Status changes to earlier findings

| item | status |
|---|---|
| findings/001 Lambda certificate for M1 | **stands.**  Exact, independently falsified by brute force on 7 tasks |
| findings/001 Lambda_2 (absorber mass ceiling) | **DOWNGRADED.**  It was derived from the high-frequency asymptote, but that asymptote is approached from BELOW when absorber damping exceeds a threshold, in which case it is an upper bound and not a necessary condition.  It must be re-derived with the direction of approach stated.  Losing it does not affect the Lambda certificate, which is separate |
| findings/002, 003 (Q1/Q2 from literature) | **downgraded as arguments.**  Per CONSENSUS 13-15 the cited work has test beds with small solution spaces where heuristics have the advantage, so it cannot carry the method.  The material stays as background |
| findings/004 waterbed invariant | stands as mathematics; its use for M2 remains a negative result |
| findings/006 escape ladder | stands as a fact about the L0 box; the box is the wrong object |
| findings/007 L0 ablation | stands with its own stated caveat; superseded as evidence for the thesis |
| findings/008 false-positive zone | **reframed, not withdrawn.**  Per CONSENSUS 5 it is not a counterexample to provability; it is the empirical instance of a proof's domain of validity being crossed by higher fidelity.  That is the mechanism working, not failing |

Retracted positions, carried forward so they are not re-invented: the capability
declaration protocol (a revival of expert systems, inserting the researcher's prior
into the loop as predicates - and in real research it is often the prior that is
wrong); a trained external adjudicator (the same gate in harder-to-inspect material,
and it contradicts "train nothing"); and framing the harness as producing training
data (data is a by-product).

## 4. What the object must become

    S = (component inventory, connection topology, boundary relations)
    theta in Theta(S)

with a size measure N(S) that can be swept, so that the experiment can move across the
crossing point.  The concrete proposal on the table is to generalise the tuned mass
damper from a fixed two-degree-of-freedom topology to a composable structure carrying
any number of absorbers at chosen attachment points.

## 5. The experiment this implies

CONSENSUS 16: at fixed evidence strength, measure the cost of RULING OUT a region as a
function of design-space size.  The heuristic must sample, so its cost grows with N;
a proof does not sample, so its cost is flat.  The claim is that the curves cross, and
the deliverable is the crossing point.

Three things are needed for that to be a real experiment rather than a slogan:

1. **A size axis that actually varies.**  Number of absorbers, each with mass,
   stiffness, damping and an attachment choice, gives a space that grows
   combinatorially in the number of components rather than linearly in dimension.
2. **A class-level certificate, not a point certificate.**  The existing Lambda rules
   out one parameter region of one fixed mechanism.  What the crossing experiment
   needs is a statement of the form "no member of this entire family can do X",
   whose derivation cost does not depend on how large the family is.
   The direction I believe is provable: for a passive isolator in which the payload
   is tied to ground through a single passive branch, the high-frequency
   transmissibility is governed by that branch alone, so
   abs T -> k1/(m1 w^2) independently of how many masses hang off the payload and how
   they are connected.  Combined with the sag constraint forcing k1 to carry the whole
   supported weight, that gives a ceiling on the fraction of mass that may be moved
   off the payload - for the whole family at once, at constant derivation cost.
   **Stated as a belief, not a result: the direction of approach to the asymptote
   decides whether it yields a necessary condition, and that is exactly the point on
   which Lambda_2 failed.  It must be proved before it is used.**
3. **A like-for-like cost model.**  Proof cost is derivation plus checking;
   heuristic cost is samples times the cost per evaluation.  They must be reported on
   one axis, and CONSENSUS 16 fixes that axis as "cost to rule out a region", not
   "cost to find a design".

## 6. Decisions

  * **L2 kernel: OpenModelica**, chosen by the user for alignment with the stated goal
    of industrial-scale applied-physics systems.  It is a genuinely different
    toolchain from the SciPy stack used so far, which is what L2 independence
    requires.  Recorded in docs/decisions/002.
  * **The L1 sign bug is fixed and the fix verified**, rather than deferred, because it
    silently corrupted every L1 number produced so far and the fix is one line.
  * **Nothing in the current L1 conclusion set is promoted** until the design space is
    enlarged.  Findings 009 exists so that no later reader mistakes the parameter-box
    results for evidence about the thesis.
