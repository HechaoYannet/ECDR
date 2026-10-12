# Finding 010 - The g(N) census

Status: run. One candidate certificate is **eliminated**, one design rule is established,
and the census did its job as a go/no-go before any apparatus was built.
Code: ecdr/structure/. Reproduce: scripts/step19_gN_census.py

## 1. Why a census and not an experiment

Roadmap 5.4 says a certificate is useful only if g(N) - the NUMBER of structures it rules
out - grows with the space. That is a counting question, answerable in an afternoon, and
it can kill a candidate before a simulation harness exists. Cheapest possible test of the
most serious risk, so it went first.

## 2. The space

A structure is a connected labelled graph on n nodes (each node a mass, each edge a
spring-damper), one distinguished payload node, plus a non-empty subset of nodes tied to
ground. Edge types are fixed so the combinatorics are not confounded with component-type
choices. Then

    abs(S(n)) = c(n) * (2^n - 1),  c(n) = connected labelled graphs (OEIS A001187)

| n_max | N (structures) |
|---|---|
| 4 | 602 |
| 5 | 23,170 |
| 6 | 1,705,522 |
| 7 | 238,720,034 |
| 8 | 64,383,610,994 |

N grows super-exponentially, which is the property the crossing argument needs.

## 3. What was measured, and the honest scope

Three predicate families were probed, all with a FIXED requirement:

  * **I1 mode counting** - rules out structures with fewer than m nodes. This is the
    certificate taken from the draft (a target with m distinct frequencies needs m modes).
  * **I2 ground-path counting** - rules out structures with fewer than q grounded nodes.
  * **I3 balanced threshold** - rules out structures whose grounded subset has fewer than
    half the nodes.

**Scope, stated up front: I2 and I3 are SHAPE PROBES, not physical invariants.** They were
invented to test whether all three regimes of 5.4 are reachable. The census measures the
coverage shape of predicate families; whether a physically SOUND invariant with the I3
shape exists is a separate and harder question, and it is not answered here.

## 4. Results

| n_max | N | g_I1 | g_I1/N | g_I2 | g_I2/N | g_I3 | g_I3/N | speedup I3 |
|---|---|---|---|---|---|---|---|---|
| 3 | 32 | 32 | 1.0e+00 | 28 | 8.8e-01 | 14 | 0.438 | 2.00 |
| 4 | 602 | 32 | 5.3e-02 | 408 | 6.8e-01 | 394 | 0.654 | 2.89 |
| 5 | 23,170 | 32 | 1.4e-03 | 11,328 | 4.9e-01 | 11,314 | 0.488 | 1.95 |
| 6 | 1,705,522 | 32 | 1.9e-05 | 572,112 | 3.3e-01 | 1,106,178 | 0.649 | 2.85 |
| 7 | 238,720,034 | 32 | 1.3e-07 | 52,827,280 | 2.2e-01 | 118,680,306 | 0.497 | 1.99 |
| 8 | 64,383,610,994 | 32 | 5.0e-10 | 9,108,576,592 | 1.4e-01 | 40,869,552,210 | 0.635 | 2.74 |

Three regimes, all realised:

| predicate | g(N) | fraction | speedup | row of 5.4 |
|---|---|---|---|---|
| I1 resource bound, fixed requirement | **32, exactly constant** | 1.0 -> 5e-10 | -> 1 | **no crossing** |
| I2 resource bound, growing | 28 -> 9.1e9 | 0.875 -> 0.141 | 8.0 -> 1.165 | crossing, but **decaying** |
| I3 balanced threshold | 14 -> 4.1e10 | ~0.5 steadily | ~2.4, **persistent** | **row 3** |

## 5. The finding that matters: the draft's own certificate is in the wrong row

**Mode counting has g(N) = 32, exactly constant.** Once the space can exceed the
requirement, the set it rules out is a fixed finite prefix - 32 structures - no matter how
large the space becomes. The fraction collapses from 1.0 to 5e-10.

By roadmap 5.4 this certificate **produces no crossing**. Its entire value is a one-off
absolute saving that never grows. It is sound, it is exact, it is free to check, and it is
**the wrong shape**.

Scaling the requirement does not rescue it: with m = n_max//2 the ruled-out count is 32 at
n_max = 8, a fraction of 5e-10. In a super-exponentially growing space, "too few
components" is always a vanishing predicate.

This is the census working exactly as intended: it eliminated the candidate I had put
forward as "the first certificate", before any harness was built around it.

## 6. The design rule it establishes

> Certificate predicates must be **thresholds on balanced structural attributes**, not
> **resource bounds**.

Resource bounds - too few masses, too few components, too few ground paths - are
necessarily satisfied by a vanishing fraction of a super-exponentially growing space.
They sit in rows 1 or 2 and their advantage decays to nothing.

A threshold on a balanced attribute (for example: fewer than half the nodes grounded) is
satisfied by a roughly constant fraction, sits in row 3, and yields a persistent
constant-factor speedup.

**This changes what the certificate layer is looking for.** The question is no longer
"which invariants can we prove?" but "which invariants are sound AND have a balanced
predicate?". Provability is necessary and not sufficient, and a physically sound invariant
with the wrong predicate shape is worthless for the crossing claim - which is precisely
what happened to mode counting.

It also retro-explains the vibration result: the Lambda certificate rules out a fixed
low-dimensional region, so g(N) = O(1) as the space grows, so 5.4 predicts no crossing,
and none was observed. The theory predicted its own negative result.

## 7. What must happen next, and in what order

1. **Search for a sound invariant with a balanced predicate.** This is now the critical
   path and it is a physics question, not a counting question. The candidate families in
   roadmap 6 are the starting list, but each must be checked for predicate shape FIRST and
   proved SECOND.
2. **Do not build the harness until one is found.** Section 5.4 says a row-1 or row-2
   invariant cannot produce the result regardless of how good the machinery is.
3. **Record the shape test as a standing gate**: every proposed certificate must report
   g(N) on a growing space before it is implemented.

## 8. Honest limits

  * I2 and I3 are invented predicates. The census establishes what shapes are reachable,
    not that any of them is physically sound.
  * The space uses one edge type. Adding component-type choices multiplies N further,
    which can only push resource-bound predicates further into the vanishing regime - it
    cannot rescue them - but it also changes the balanced-attribute arithmetic, which has
    not been checked.
  * Only fixed requirements were swept for I2/I3. The scaling-requirement sweep was run for
    I1 only.
  * The speedup for I3 oscillates with the parity of n (about 2.0 for odd n, about 2.8 for
    even); the persistent average is about 2.4, not a clean constant.
