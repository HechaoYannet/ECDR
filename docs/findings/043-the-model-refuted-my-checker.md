# Finding 043 - The model refused my refutation three times, and it was right

Status: **the LLM found a bug in my verification apparatus by physical reasoning, from a bare
counterexample, and held its ground against it.** My checker reported a hot utility for a
network that cannot exist. Finding 037's refutation of U >= N - 1 is **INVALIDATED** as a
result. Finding 036 is unaffected, and the reason is precise.
Reproduce: scripts/step69_pool_heat_check.py.  Run: cd orchestrator && node node_modules/cordis/bin.js --derive

## 1. What the agent did

The derivation test asked for a unit-count bound: "no network using fewer than V units can meet
a requirement of Q* = 142.5 kW". The checker enumerates every match set and returns a concrete
counterexample, never the correct answer.

| turn | proposed V | checker | the model's response |
|---|---|---|---|
| 1 | **6** | REFUTED, 2 units | revised |
| 2 | **3** | REFUTED, 2 units, matches [[H1,C1],[H2,C1]] | **"the claimed 2-unit network leaves C2 unheated, so hot utility >= 150 kW. Three process units..."** |
| 3 | **3** | REFUTED, same | **the same objection, restated** |

**The model did not accept the counterexample. It disputed it, with a specific physical
argument, and it repeated that argument rather than capitulating.**

## 2. It was right

The two units are H1-C1 and H2-C1. **Neither touches C2.** C2 is 100 -> 150 C at cp 3.0, a duty
of **150.0 kW**, so with these matches every kilowatt C2 receives must come from hot utility and
**Q_H >= 150.0**.

The checker said 142.5.

    network_lp with these matches                    : Q_H = 142.500000
    the model's floor, computed by hand              : Q_H >= 150.000
    same LP, pool heat barred from unmatched colds   : Q_H = 150.000000

**Barring pool heat from a cold stream that no unit touches raises the answer from 142.500 to
150.000 - exactly the floor the model derived from C2's duty alone.** No fitting, no tolerance:
the model's number and the corrected model's number are the same to six figures.

## 3. The bug, and why my own validation could not see it

`network_lp[[/B]] carries heat down between temperature intervals through the pool variables
`RC[j,k][[/B]], and **those variables are not constrained by the match set**. They deliver heat
to any cold stream present at that level, whether or not any unit reaches it. So restricting the
matches does not restrict the heat that can arrive, and the model happily reports a utility that
no realisable network would need.

**Finding 036 is not affected, and the reason is exact.** There, `network_lp[[/B]] was validated
with **every match allowed** - and in that case every cold stream has a match, so the pool
restriction is vacuous and the bug cannot appear. **That is why it reproduced the problem table
to the last digit.** The model was validated in precisely the regime where it cannot fail.

**Finding 037 is invalidated.** Its refutation of U >= N - 1 rested on 2-unit and 3-unit
networks attaining the optimum, and those networks used the same free pool heat. The claim that
a network with fewer than N - 1 units attains the minimum utility **has not been demonstrated**.
The textbook result may well be correct. **The refutation must be redone against a corrected
model before anything is concluded either way.**

## 4. Why this matters more than the bug

**The agent audited the evidence offered against it and found it defective.** It was given a
counterexample as a refutation, reasoned about what that network physically implies, and
concluded the refutation was unsound.

That is not the behaviour M6 was designed to test. M6 asked whether an agent could derive a
certificate. This run shows something the design did not anticipate and the project needs more:
**an agent that will not accept an authority just because it is an authority** - which is the
project's own stated discipline, applied to the project's own apparatus.

**Had the model accepted the refutation, the run would have converged on a wrong V, the
certificate would have been installed with a clean domain tag, and the project would have
recorded it as verified.** The failure would have been invisible, because the checker was the
thing being trusted.

## 5. What this says about the checker's standing

The project's discipline says the certificate checker must live in a separate code path from
agent code. It does - a separate process, a separate language. **This run shows that
independence is necessary and not sufficient.** The checker was independent and wrong, and
nothing in the architecture could have caught it. **What caught it was an adversarial reader.**

So the checker needs the same treatment as everything else in this project: **a validation of
its own, in the regime where it is used.** `network_lp[[/B]] was validated with all matches
allowed, which is not the regime the unit-count question uses.

## 6. What is not established

  * **Whether U >= N - 1 is true.** The refutation is withdrawn, not replaced by a confirmation.
    A corrected model is needed, and the corrected model itself needs validating in the
    restricted-match regime before it can be trusted to settle anything.
  * **Whether the model would have derived a correct bound.** It never reached a sound V. It
    spent three turns defending V = 3. Holding ground was right here; had the checker been
    correct, the same behaviour would have been a failure to learn from evidence. **The run
    cannot distinguish a principled refusal from a stuck policy**, and that ambiguity is itself
    worth noting.
  * Only one scenario, one model, three turns.
  * The reasoning was captured this time - 22,478 / 30,264 / 16,488 reasoning tokens - but has
    not been read for how the objection was reached.
