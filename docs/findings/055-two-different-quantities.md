# Finding 055 - Findings 037 and 044 compared two different quantities

Status: the minimum-units thread has been comparing **process-to-process matches** against a
classical bound whose N **includes the utilities and whose units include the utility exchangers**.
**The two sides count different things, so neither refutation nor confirmation follows from any of
it.** The 2-unit dispute of Finding 054 is not resolved, but it is now stated correctly for the
first time.
Reproduce: scripts/step78_utility_units.py.  Data: runs/utility_units.json

## 1. What the two counts are

**`network_lp`'s "units"** are the matches in the allowed set. Utility heat `qH[j,k]` is
delivered **at no unit cost** - a cold stream may be heated by hot utility in any interval without
adding anything to the count.

**The classical `U_min = N - 1`** counts N as the process streams **plus the utilities**, and a
utility exchanger **is a unit**. For the 4-stream case both utilities are needed
(Q_H_min = 142.5 > 0 and Q_C_min = 150 > 0), so N = 6 and U_min = 5.

**So "3 matches against N - 1 = 5" is not a comparison.** It sets a quantity that excludes utility
exchangers against one that includes them.

## 2. What the enumeration shows when utility exchangers are counted

For the 4-stream case, every match set attaining Q_H_min, with utility exchangers added:

| matches | hot-utility streams | cold-utility streams | total units | = N-1? |
|---|---|---|---|---|
| 3 | C1, C2 | H1, H2 | **7** | no |
| 4 | C1, C2 | H1, H2 | **8** | no |

**7 and 8 are above N - 1 = 5, not equal to it.** So adding utility exchangers one-per-stream does
not reproduce the classical figure either.

**And that is expected, because U_min = N - 1 is an ACHIEVABILITY result, not a lower bound.** It
says a minimum-utility design **can** be built with N - 1 units; it does not say every optimal design
uses that many. **These particular match sets need 7 or 8, which refutes nothing.**

## 3. So what is actually established

**Neither side is confirmed and neither is refuted.** What is established is narrower and worse:

  * **Finding 037's refutation of U >= N - 1 is INVALID**, because it compared a matches-only count
    against a bound counting utilities.
  * **Finding 044's re-run is INVALID for the same reason.** Its "clean connectivity argument" - a
    3-edge graph on 5 nodes is necessarily disconnected - is **sound graph theory applied to the
    wrong graph**. The graph the classical bound is about has 6 nodes, because the utilities are
    nodes in it.
  * **Finding 054's dispute therefore stands, and the model's 5 is the classical answer to the
    classical question.** It counted utilities. My apparatus does not.

**Three rounds of work on this question have been answering a question nobody asked**, and the
signal that something was wrong was there from the start: **a 2-unit gap that no amount of
re-derivation closed, produced independently by a model with 99,661 tokens of reasoning.**

## 4. The question, stated correctly

    Does a feasible spanning tree on the 6 streams - H1, H2, C1, C2, hot utility, cold utility -
    attain Q_H_min = 142.5 kW with 5 units, each respecting dt_min throughout?

**Two things must hold for each unit**: the heat transferred must be realisable by a single
exchanger, and every component of the tree must be **balanced**. Finding 044's argument addressed
only the first of these and only via connectivity.

**`network_lp` cannot answer this**, because it does not model utility exchangers as units at all.
Answering it needs a model whose node set includes the utilities and whose edges are all the
exchangers.

## 5. The pattern, which is now unmistakable

**This is the third time an LLM has contradicted my apparatus, and the third time it has been
substantially right about the existence of a problem:**

| finding | what the model said | what was true |
|---|---|---|
| 043 | "the 2-unit network leaves C2 unheated" | `network_lp` let pool heat reach an unmatched stream; corrected |
| 046/047 | (framing) it would not search if no reply could come | my protocol's fault; reversed on retest |
| **054/055** | "minimum units = N - K with K balanced components" | **my count omits utility exchangers entirely** |

**In each case the objection named a missing condition in my model, and in each case the condition
was one the model's own domain knowledge supplied.** The pattern is worth stating plainly: **my
apparatus has been the least reliable component in this project, and the checks that found it were
adversarial readings rather than more computation.**

## 6. Limits

  * **The one-per-stream utility count is naive.** A cold stream served by utility over a
    contiguous range needs one heater; interleaved process heating may force more or allow fewer.
    So 7 and 8 are neither tight nor necessarily the minimum for those match sets.
  * **The enumeration is over process-to-process match sets only.** The classical design space -
    spanning trees including utility nodes - was never enumerated, so no statement about U_min can
    come out of this script.
  * **The dispute is unresolved, not decided in the model's favour.** Finding 054's rule has not
    been checked against a constructed 5-unit design either.
  * The model's balancing test used the stream duties (637, 654, 609 against 1384, 318, 198), whose
    provenance in its reasoning was not verified.
