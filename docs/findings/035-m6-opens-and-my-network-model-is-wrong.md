# Finding 035 - M6 opens: the certificate is sound in a second domain, and my network model is wrong

SUPERSEDED IN PART BY FINDING 036: the missing mechanism was the per-stream residual chain,
and with it added the network model reproduces the problem table to the last digit, the bound
is tight, and all four properties hold. Sections 3, 4 and 5 below stand as the record of the
error and of how it was found.

Status: the heat-exchanger domain is established and the minimum-utility certificate is
computed two independent ways that agree EXACTLY. But the network model built to test
ACHIEVABILITY understates what a network can do by 53 percent, because it forbids heat from
being carried between temperature intervals. Soundness holds; tightness is untested.
Reproduce: scripts/step65_heat_min_utility.py, step66_heat_ecdr_question.py.
Data: runs/heat_min_utility.json, runs/heat_ecdr_question.json

## 1. Why this domain

Finding 009 section 2.2 and the roadmap's M6 say the same thing: the vibration work is ours
from end to end, so it can show the theory stands up but not that the method works. Heat
exchanger network synthesis is a scenario we did not author, with its own requirement and its
own physics, and it maps onto ECDR term for term:

| ECDR | heat-exchanger networks |
|---|---|
| structure S | a set of allowed matches between hot and cold streams |
| capability | the hot utility the network needs |
| requirement | hot utility <= Q* |
| delta(S) > epsilon | every network misses the requirement |
| certificate | Q_H_min, computed from the STREAM DATA alone |

Q_H_min is the exact analogue of the modal-dimension certificate: a property of the problem
rather than of any design, so it rules out an unbounded family at a cost that does not grow
with the family. And it names what is missing - the pinch temperature and the heat deficit
there - which is what a repair must act on.

## 2. What holds

The problem table (Linnhoff's cascade over shifted temperature intervals) and the
transshipment **linear program** (scipy HiGHS over the same relaxation) agree **exactly** -
worst difference 0.000e+00 over 12 cases spanning four stream sets and three values of
dt_min. And every case satisfies the stream-data energy identity

    Q_H - Q_C = (total cold duty) - (total hot duty)

which must hold for any network and depends on the stream data alone. Both routes satisfy it
in all 12 cases.

The behaviour is also physically sensible: with hot streams in excess the hot utility is
exactly 0; with cold streams in excess the cold utility is exactly 0; and raising dt_min
raises the utility requirement, as a smaller temperature driving force must.

**Agreement here checks the IMPLEMENTATION, not the physics** - both routes encode the same
relaxation. The physics claim is section 4.

## 3. What does NOT hold, and this is the finding

A network-level model was built to test achievability: for a set of allowed (hot, cold)
matches, solve a linear program over per-interval heat flows and find the least hot utility.
The intent was that enumerating every match set would show both that no network beats the
certificate and that some network attains it.

| case | certificate | network LP, all matches | difference | best over every match set |
|---|---|---|---|---|
| 4-stream | **142.5** | **217.5** | **+75.0** | 217.5 |
| 2x2 | **60.0** | **110.0** | **+50.0** | 110.0 |
| 3x2 | **0.0** | **70.0** | **+70.0** | 70.0 |

**The network model cannot reach the certificate, and is 35 to 53 percent above it.**

The cause is structural, not numerical. The model lets heat be exchanged only **within** a
temperature interval: hot stream i in interval k must have its duty absorbed by cold streams
in interval k, or dumped to cold utility. **It has no mechanism for heat to be carried from
one interval down to the next**, which is precisely what the aggregate cascade's residual
term represents and what a real network does whenever a hot stream cooling from 200 to 100
heats a cold stream from 50 to 150 across several levels.

The correct model - the standard transshipment formulation - carries a **per-stream residual
chain** so that heat released at one level can be absorbed at a lower one. That was omitted.

**The 3x2 case makes the error unmistakable**: the certificate says no hot utility is needed
at all, and the model says 70 kW are.

## 4. What survives

**Soundness survives.** In every case the best network found is at or above the certificate,
so the certificate remains a valid lower bound. That is the property the method actually
needs: a certificate that is sound but not tight is still a certificate; one that is tight
but unsound is worthless.

**Tightness does not.** Whether some network attains Q_H_min is now untested, because the
model that was supposed to demonstrate it cannot express the networks that would.

**And the rule-out property is therefore also untested in the form intended.** With
Q* = 0.9 * Q_H_min the certificate declares the requirement infeasible while the best network
found is far above Q* anyway - so the two agree for the wrong reason, and the case proves
nothing about the certificate's power. The 3x2 case is worse: the certificate equals 0, so
there is no Q* below it to rule out.

## 5. What this round actually established

  * A second domain exists, with a real requirement and physics we did not choose.
  * A sound, cheap, stream-data-only certificate for it, computed two ways that agree exactly.
  * A network model, and **proof by cross-check that the model is wrong** - it disagrees with
    the established route by up to 70 kW on quantities of order 100 kW.
  * The failure is in MY new code, found by comparing against the established computation
    rather than by inspection. The aggregate LP was written first and independently; had the
    network model been the only implementation, the 53 percent error would have been invisible
    and would have looked like a real property of the domain.

That last point is the same lesson as Findings 028 and 032, in a third setting: **the
instrument that catches a modelling error is another implementation of the same physics, not
more care.**

## 6. Next

  * Add the per-stream residual chains to the network model, then re-run the enumeration. Only
    then can tightness and the rule-out property be tested.
  * The minimum-units certificate (Euler's rule on the network graph) is the combinatorial
    analogue of the modal-dimension certificate and has not been written.
  * The orchestrator and the LLM loop are untouched by this round.

## 7. Limits

  * Three stream sets, one dt_min each in the enumeration, four to six streams. Not a survey.
  * All streams are constant-cp, single-phase, with fixed supply and target temperatures. The
    certificate's domain tag is exactly this, and it is not valid for phase change.
  * The utility relaxation allows utility heat at any temperature level, which is standard for
    the minimum-utility bound but is not how real utilities work.
  * No capital cost, no area, no unit count. The requirement modelled is utility alone.
