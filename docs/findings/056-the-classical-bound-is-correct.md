# Finding 056 - U >= N - 1 is CORRECT: the three-round refutation was an artifact

Status: **the classical minimum-units bound holds on this case, as a bound AND as an achievement.**
A model with the utilities as nodes finds that the fewest units attaining Q_H_min is **5 = N - 1**,
and that **4 units cannot do it**. Findings 037, 044 and 054 were all wrong about this, and the LLM
that disputed them was right - **the third time.**
Reproduce: scripts/step79_design_units.py.  Data: runs/design_units.json

## 1. The model the classical statement is about

Nodes:

    H1, H2, C1, C2, HU (hot utility), CU (cold utility)          N = 6

Edges: a process exchanger (H_i, C_j); a heater (HU, C_j), and since HU sits above every stream it
may deliver at any level; a cooler (H_i, CU), and CU sits below every stream so it may absorb at any
level. **A design is an edge set and its unit count is the number of edges.**

219 designs enumerated.

## 2. The result

| units | designs | best Q_H | attains Q_H_min = 142.5 |
|---|---|---|---|
| **4** | 3 | **150.000000** | **no** |
| **5** | 10 | **142.500000** | **YES** |
| 6 | 12 | 142.500000 | YES |
| 7 | 6 | 142.500000 | YES |
| 8 | 1 | 142.500000 | YES |

**Fewest units attaining Q_H_min = 5 = N - 1.** And **no 4-unit design reaches it** - the best is
150.0. So on this stream set the classical bound holds **both ways**: it is achieved, and it is not
beaten.

## 3. The optimal design is a spanning tree, exactly as the theory says

    process exchangers   H1-C1, H1-C2, H2-C1
    heater               HU-C2
    cooler               H2-CU                       total 5

Six nodes, five edges: H1-C1 and H2-C1 connect H1, H2, C1; H1-C2 adds C2; HU-C2 adds HU; H2-CU adds
CU. **Connected, acyclic, five edges on six nodes - a spanning tree**, which is what the classical
derivation of U_min = N - 1 constructs.

## 4. What went wrong over three rounds

**The three process exchangers of Finding 044 are real.** H1-C1, H1-C2, H2-C1 is exactly the optimal
design's process part. **What Finding 044 treated as a complete design was an incomplete one**: that
network still needs a heater to supply C2 and a cooler to take H2's surplus. **Add them and the count
is 5.**

So the error was not in the physics of any single step. It was in **treating a fragment of a design
as a design**, and then comparing its edge count against a bound that counts the whole thing.

| finding | claim | status |
|---|---|---|
| 037 | U >= N - 1 refuted, 2 units against N - 1 = 4 | **WRONG** |
| 044 | refutation redone, 3 units against N - 1 = 4 | **WRONG** |
| 054 | open dispute, model says 5, apparatus says 3 | **the model was right** |

## 5. The pattern, now with three instances and no exceptions

| finding | the model's objection | what was true |
|---|---|---|
| 043 | "the 2-unit network leaves C2 unheated" | `network_lp[[/B]] let pool heat reach an unmatched stream |
| 046/047 | it would not search because no reply could come | my protocol's fault, reversed on retest |
| **054/056** | "minimum units = N - K with K balanced components" | **my count omitted the utility exchangers entirely** |

**Three times an LLM contradicted my apparatus, three times it named a missing condition in my
model, and three times it was right.** In each case the condition it named was one its own domain
knowledge supplied and my code did not represent.

**The uncomfortable and correct conclusion is that in this project the apparatus has been the least
reliable component, and every defect in it was found by an adversarial reading rather than by more
computation.** More computation would have produced more numbers from the same wrong model.

## 6. What this does and does not settle

**Settled**: U >= N - 1 is correct on this stream set, as a bound and as an achievement. Findings 037
and 044 are withdrawn in substance, not merely invalidated. The 2-unit dispute of Finding 054 is
resolved in the model's favour.

**Not settled**: whether U >= N - 1 holds in general. One stream set, one dt_min, one enumeration.
The classical result is a theorem and this is an instance of it; the project's contribution here is
that it took three rounds to stop contradicting a theorem with a miscount.

**And not touched**: the certificate question this thread was originally about. Whether a
unit-count certificate is *useful* is Finding 050's question, and Finding 050's answer - that a
resource bound covering a vanishing fraction sits in section 5.4's row 1 - **does not depend on
whether the bound is true, only on how much it covers**.

## 7. Limits

  * **One stream set, dt_min = 10.** The enumeration is 219 designs.
  * **The utility temperatures are not modelled.** HU is assumed hotter than every stream and CU
    colder, so a heater or cooler is always feasible. A real utility has a fixed temperature and
    that constrains where it can deliver.
  * **One exchanger per edge.** A single edge may need several shells; the classical count has the
    same convention.
  * **The LP allows a match to transfer at any pair of levels**, which Finding 044 validated against
    the problem table in the all-matches regime. The utility edges add the flags, nothing else.
  * The three-round error was mine and was invisible to every test I ran, because every test asked
    the same model the same kind of question.
