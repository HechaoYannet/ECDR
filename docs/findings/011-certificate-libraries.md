# Finding 011 - Certificate libraries, and the two separable conditions

Status: the target of roadmap 5.4 is **replaced**. The design requirement relaxes by
three orders of magnitude, and what remains hard is relocated precisely.
Code: ecdr/structure/library.py. Reproduce: scripts/step20_library.py

## 1. The single-certificate target was wrong in both directions

5.4 asked for one certificate with g(N) = Theta(N): a constant FRACTION of the space
ruled out. That target is

  * **too strong**, because in a combinatorial space a constant fraction is hard to come
    by - Finding 010 showed resource-bound predicates cannot deliver it; and
  * **too weak**, because even if achieved it caps the speedup at 1/(1-f). Covering half
    the space buys a factor of two. That is not a result.

## 2. The correction: libraries compose

Suppose a LIBRARY of certificates where certificate i rules out a fraction f_i of the
space REMAINING after certificates 1..i-1. Then the remaining fraction is prod(1 - f_i),
so a uniform lower bound f gives

    remaining  <=  (1 - f)^k        =>        k  =  O( log N / log(1/(1-f)) )

certificates to reduce the space to a sampleable remainder, at cost k * c_p against
Theta(N) * c_s for exhaustive sampling.

**The logarithm is the whole point: at fixed f the certificate count grows ADDITIVELY
per decade of N while sampling grows MULTIPLICATIVELY.**

| coverage f | N=1e3 | 1e6 | 1e9 | 1e12 | 1e18 |
|---|---|---|---|---|---|
| 0.500 | 10.0 | 19.9 | 29.9 | 39.9 | 59.8 |
| 0.100 | 65.6 | 131.1 | 196.7 | 262.3 | 393.4 |
| 0.010 | 687 | 1375 | 2062 | 2749 | 4124 |
| 0.001 | 6904 | 13809 | 20713 | 27617 | 41426 |

And the separation at the census space size N = 6.44e10:

| coverage f | certificates | library cost | sampling cost | separation |
|---|---|---|---|---|
| 0.635 | 24.7 | 25 | 64,383,610,994 | 2.6e+09 |
| 0.500 | 35.9 | 36 | 64,383,610,994 | 1.8e+09 |
| 0.100 | 236 | 236 | 64,383,610,994 | 2.7e+08 |
| 0.010 | 2,476 | 2,476 | 64,383,610,994 | 2.6e+07 |
| **0.001** | 24,876 | 24,876 | 64,383,610,994 | **2.6e+06** |

**A tenth of a percent of coverage per step buys a factor of 2.6 million.** The design
requirement therefore relaxes from "cover half the space" to:

> **a constant, arbitrarily small, per-step coverage lower bound.**

## 3. Robustness is a property of the predicate shape, not of the space

The census of Finding 010 ran on all connected labelled graphs, a space dominated by
near-complete graphs that no mechanical structure resembles. Re-running the same two
predicate families on a sparse space (trees, Cayley n^(n-2), times non-empty ground
subsets):

| n_max | N (trees) | g_balanced | fraction |
|---|---|---|---|
| 4 | 265 | 171 | 0.645 |
| 5 | 4,140 | 2,046 | 0.494 |
| 6 | 85,788 | 55,182 | 0.643 |
| 8 | 69,066,997 | 43,581,351 | 0.631 |
| 10 | 104,813,164,156 | 64,963,238,446 | 0.620 |

The balanced-threshold fraction sits at 0.44 to 0.65 across two different spaces and eight
orders of magnitude of N, while the resource-bound fraction collapsed from 1.0 to 5e-10
on the dense space. **Shape decides robustness; the space does not.**

## 4. The consequence: two conditions, and they are separable

The library formulation splits what looked like one hard problem into two, and they are
checked by different means:

| condition | what it is | how it is checked | status |
|---|---|---|---|
| **Shape** | the predicate must be scale-free: it must cut a constant fraction of whatever remains | counting, on a growing space | **settled analytically** (Findings 010, 011); balanced-threshold predicates qualify, resource bounds do not |
| **Soundness** | the invariant must actually be true of the physics | proof, domain-tagged | **open - this is the work** |

There is a third requirement that belongs to the benchmark, not to the invariant:

  * **Calibration.** The performance requirement must sit at the marginal point of the
    structural capability distribution, so that a non-trivial fraction can meet it and a
    non-trivial fraction cannot. A requirement that nothing meets gives coverage 1 and a
    trivial answer; one that everything meets gives coverage 0.

## 5. What this changes about the search for physics

The target is no longer "one deep theorem". It is:

> **a FAMILY of sound invariants whose predicates are scale-free and mutually
> independent**, each cutting a constant fraction of what the previous ones left.

That is a materially different and more reachable brief: several shallow-but-sound
invariants beat one deep one, because the composition is what produces the separation.
And it explains why the mode-counting certificate failed twice over - it is not scale-free
(g = 32 constant), and it is alone.

## 6. The honest gap

**No physically sound invariant with a scale-free predicate has yet been demonstrated.**
The balanced predicates in Findings 010 and 011 were INVENTED as shape probes: "fewer
than half the nodes grounded" is combinatorially convenient and has no established
physical meaning. Whether the number of grounded nodes, or the payload's connectivity, or
any other balanced attribute corresponds to a real physical limitation is exactly the
open question, and it is a physics question.

Three failure modes to watch for, in order of likelihood:

  1. the only scale-free predicates available are combinatorially convenient and
     physically vacuous, so the shape condition is met but the soundness condition is not;
  2. sound invariants exist but their predicates are resource bounds, so soundness holds
     and shape does not - this is exactly what happened to mode counting;
  3. the requirement cannot be calibrated to the marginal point because the capability
     distribution is degenerate (almost all structures succeed or almost all fail).

## 7. Next, in order

  1. **Enumerate candidate invariants and test their predicate shape FIRST.** Shape is a
     counting question and it is cheap; soundness is a proof and it is expensive. Testing
     shape first is the whole lesson of Findings 010 and 011.
  2. **Look for independence.** Two scale-free predicates that are perfectly correlated
     compose to nothing. Report the joint coverage, not just the marginal.
  3. **Calibrate the requirement** by measuring where the capability distribution actually
     sits, rather than assuming a difficulty.
  4. Do not build the harness until at least two sound, scale-free, independent invariants
     exist on paper - one certificate does not a separation make.

## 8. Limits

  * The composition assumes successive coverage fractions are well defined and bounded
    below; it says nothing about how to FIND such a sequence, which is the research.
  * c_p is treated as constant per certificate. If deriving the i-th certificate gets
    harder as the space shrinks, the argument degrades - it needs c_p = O(polylog N), and
    that is an assumption, not a result.
  * The tree space is still a crude model of a real mechanical structure: one edge type,
    no component choices, no boundary conditions.
