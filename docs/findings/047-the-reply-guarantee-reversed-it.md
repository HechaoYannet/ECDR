# Finding 047 - Guaranteeing a reply reversed the result: the agent checks itself when it believes a check is possible

Status: Finding 046 asked whether the agent audits its own evidence unprompted, found it did not,
and recorded that **its own framing was a confound** - the agent's stated reason for not searching
was that no result would ever arrive. **One sentence was added to guarantee the reply. Everything
else is identical. The result reverses completely.**
Reproduce: cd orchestrator && node node_modules/cordis/bin.js --selfaudit

## 1. The single variable

Added to the system prompt, and nothing else changed:

> If you set search_below to an integer, THE SEARCH WILL BE RUN AND ITS COMPLETE RESULTS WILL BE
> RETURNED TO YOU AS THE NEXT MESSAGE. You will then reply once more to finalise your certificate.
> Requesting a search costs you nothing but that one extra exchange.

## 2. What it did

| | Finding 046 (no guarantee) | **this run (reply guaranteed)** |
|---|---|---|
| turn 1 V | **6** | **3** |
| searched | **no**, search_below = null | **yes**, search_below = 6 |
| turn 1 reasoning | "above >= 3, below >= 3, **thus total >= 6. Solid.**" | "above needs two process matches, below at least one, **so V=3**" |
| turn 2 | - | "Search found a 3-unit network meeting Q_H <= 142.5 kW and none smaller" |
| final V | 6 | **3** |
| checker | **REFUTED**, nothing installed | **SOUND, INSTALLED** (heat.unit.V3) |

**Every part of the trajectory changed.** It proposed the correct value, it chose to look, it read
the result correctly, and it installed a sound certificate.

**And its pinch analysis was right this time.** In Finding 046 it argued "no feasible exchanger can
serve both above and below", concluded the two halves could not share a unit, and summed them to 6.
Here it reasoned "above needs two process matches, below at least one, so V=3" - **which is the
structure that actually holds**, because a unit may span the pinch.

**It also searched a WIDER bound than its own claim** (search_below = 6 against a proposed V = 3),
which is the sensible direction to look when checking whether anything smaller exists.

## 3. What this establishes

**The agent does check itself when it believes a check is possible.** Finding 046's negative result
was not a property of the agent but of the environment I described to it.

The behavioural story is coherent and worth stating plainly, though it is an interpretation rather
than a measurement: **told that no evidence would arrive, it reasoned to a worse answer and was
explicitly confident about it; told that evidence would arrive, it reasoned to the right answer and
then went and got the evidence anyway.** The claim it made without the prospect of check - "Thus
total >= 6. Solid." - is the one the check demolished.

## 4. Why this matters for ECDR beyond the rerun

The architecture's rule is that the certificate checker lives in a separate code path, and Finding
046 concluded from the negative result that the checker is "load-bearing rather than decorative".
That conclusion was right, but this run sharpens it:

**A checker that exists but is not VISIBLY reachable does not do its job.** The agent that believed
no evidence could be obtained did not just skip the search - it produced worse reasoning and
asserted it confidently. The checker's value is not only in rejecting false claims after the fact;
it is in changing what the agent does before the claim is made.

So the requirement is stronger than "the checker must exist in a separate process". It is: **the
agent must know, at the moment it commits to a claim, that the claim will be checked.** Making the
check implicit, or leaving its reachability to inference, forfeits the effect.

## 5. The method worked, and that is the other result

Finding 046 recorded its own framing as an unresolved confound rather than burying it, and stated
the exact experiment required: *"a rerun that guarantees a reply is required before 'the agent will
not audit itself' can be asserted."* That rerun was run, and it reversed the conclusion.

**A negative result was stated with the condition under which it should be withdrawn, and the
condition was then tested.** Finding 046 stands as the record of the confounded run; it is not
wrong, it is superseded with its own stated remedy.

## 6. Limits

  * **One run each way.** The reversal is large - V 6 to 3, no search to search, refuted to sound -
    but it is two samples.
  * **The added sentence may have changed more than responsiveness.** It plausibly reframes the
    task from "answer a question" to "run a process", and the improvement could be that reframing
    rather than the promise of a reply. **The two cannot be separated by this experiment**, and a
    task-matter-of-fact control would be needed to tell them apart.
  * The ground truth is still the corrected model of Finding 044, validated in two regimes but not
    against an exhibited physical 3-unit design.
  * The reasoning was saved again (runs/selfaudit_reasoning.txt) and has not been read; whether the
    agent changed its pinch argument because of the added sentence, or arrived at the right
    structure for an unrelated reason, is not established.
