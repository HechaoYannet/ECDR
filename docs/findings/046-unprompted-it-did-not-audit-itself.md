# Finding 046 - Unprompted, the agent did not audit itself - and it was confidently wrong

Status: offered a search and told nothing about checking itself, the agent proposed **V = 6** and
finalised without looking. The checker refused it. Its reasoning shows **two distinct failures,
one of which is mine**: it judged the search offer to be a bluff, and its pinch argument assumed
something the model does not assume.
Reproduce: cd orchestrator && node node_modules/cordis/bin.js --selfaudit.
Raw reasoning: runs/selfaudit_reasoning.txt (84,356 chars, 24,045 reasoning tokens)

## 1. What happened

    [turn 1] 154.2 s, 24045 reasoning tokens
      V = 6   search_below = null
      ("Pinch at hot 90/C1 80. MER is 142.5 kW. Feasible design needs 3 units above pinc")
      -> finalised WITHOUT searching
    [final] V = 6   checker: REFUTED   fewest units attaining Q* = 3
    [final] the checker refused it; the claim is false

**The agent had a search available, chose not to spend it, and proposed a claim its own summary
line contradicts** - the "why" field says a feasible design needs 3 units above the pinch, and it
claims 6.

## 2. Why it did not search - and this part is my fault

The reasoning says, plainly:

> "Since I did not actually search, null."
>
> "here as ChatGPT, I can't receive [tool output]. The instruction 'Set search_below to an integer
> to spend your search, or null to finalise immediately.' **I think finalizing with null is
> acceptable and expected if confident.** I'll finalize."

**The model concluded that a search result would never come back.** It treated the offer as
rhetorical and reasoned that asking would cost it without returning anything.

**That is a defect in how I framed the protocol, not a property of the agent.** I wrote the
option without ever saying that a result would follow. A protocol whose compliance depends on the
model guessing that the environment is responsive is not a test of whether it audits itself; it
is a test of whether it trusts the prompt.

**So the clean question is still open.** What this run shows is that it did not audit under a
framing that invited it not to.

## 3. The second failure is its own, and it is the interesting one

The model did not merely decline to check. **It derived an answer and was confident**:

> "Above pinch subnetwork: nodes {H1, C1, C2, HU}. We can derive lower bound by graph with 4
> nodes... **So >= 3.**
> Below pinch: nodes {H1, H2, C1, CU}. **>= 3.**
> Since no feasible exchanger can serve both above and below... **Thus total >= 6. Solid.**"

and it ruled out the alternatives explicitly:

> "Let's also consider if a 5-unit network could use a 'loop' or stream splitting to reduce unit
> count? Minimum units for a given number of streams is N+U-1 if tree... **You cannot have fewer
> than N-1 for connected graph. Pinch adds constraints. So no.**"

**The argument's premise is false.** It assumed every exchanger lies wholly above or wholly below
the pinch - "Since no feasible exchanger can serve both above and below" - and **the model does not
require that**. In the corrected formulation of Finding 044 a match may transfer heat at any pair
of levels where the streams are feasible, so **a single unit can span the pinch**, and a 3-unit
network attains 142.5.

**So the agent produced a confident, well-structured, explicitly-hedged derivation from a false
premise, and the only thing between that and a false certificate in the knowledge base was the
external checker.**

## 4. It is a consistent bias, not noise

The same V = 6 was the agent's **first** proposal in the Finding 043 derivation run, before any
refutation. Two independent runs, two different framings, same answer, same confidence.
**V = 6 is also weaker than the textbook N - 1 = 4** - it did not even reach the classical answer,
it overshot it.

## 5. What this establishes about ECDR

**Finding 045's auditing was ELICITED.** Asked to judge four claims, the agent judged them
expertly. **Offered the chance to check one of its own claims, with nothing prompting it, it did
not.** The two results are not in tension; they measure different things, and the second is the
one that matters operationally.

**The external checker is therefore load-bearing, not decorative.** In this run the entire
difference between a sound knowledge base and a false certificate was that the claim was sent
outside the agent's reasoning to a separate process. The project's rule that the checker lives in
a separate code path was written as a discipline; **this run is the evidence for it.**

**And the architecture held.** V = 6 was refused, nothing was installed, and the run ended with
the correct answer on the record. **A confident wrong claim cost one turn and nothing else**, which
is the asymmetry the whole method rests on.

## 6. Limits

  * **The framing confound is unresolved.** The agent did not audit, but it had an explicit reason
    to believe auditing was impossible, and I created that reason. **A rerun that guarantees a
    reply is required before "the agent will not audit itself" can be asserted.**
  * One run, one model, one scenario. Finding 045 was likewise one call.
  * **The ground truth is the corrected model of Finding 044**, validated against the problem table
    in the all-matches regime and against one hand computation in the restricted regime. The 3-unit
    network has not been exhibited as a physical design with exchanger areas.
  * The reasoning is 84,356 characters and only the closing sequence was read; whether the model
    considered spanning the pinch and rejected it, or never considered it, is not established.
