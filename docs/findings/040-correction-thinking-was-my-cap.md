# Finding 040 - Correction: Finding 038 blamed the model for my own token cap

Status: **Finding 038's "trap" section is WRONG and is retracted here.** The empty-content
response was caused by my own max_tokens, not by the model. The model was right, and the
recommendation to disable thinking is withdrawn because it costs correctness.
Reproduce: the four calls below, in this finding.

## 1. What I claimed, and what is actually true

Finding 038 recorded that with thinking enabled deepseek-flash "can spend the entire budget
reasoning and emit no content", that raising max_tokens from 300 to 3000 did not help, that
reasoning_effort=low did not help, and that the fix is `"thinking": {"type": "disabled"}`.

**Every one of those observations was real; the diagnosis was not.** I capped max_tokens at 300,
then 2000, then 3000. A reasoning model under a hard output cap spends the cap on reasoning
and is cut off before the answer. **3000 tokens is a very small budget for this model** - its
maximum output is 393,216.

The API documentation's own examples **omit max_tokens entirely**, and the parameter tables say
thinking is ON by default at effort=high. I did not read them before recording a behaviour as
a defect.

## 2. The retest

Same question, four configurations:

| configuration | wall | completion tokens | reasoning tokens | finish | content |
|---|---|---|---|---|---|
| **no max_tokens, thinking default** | **206.2 s** | **42,829** | **42,753** | **stop** | **full answer** |
| max_tokens=32000, thinking default | 78.9 s | 15,127 | 15,061 | stop | full answer |
| max_tokens=32000, effort=low | 16.1 s | 2,559 | 2,486 | stop | full answer |
| max_tokens=32000, thinking disabled | 0.9 s | 105 | - | stop | answer, **direction wrong** |

**The model terminates normally with `finish_reason: "stop"` in every configuration that
gives it room.** It used 42,753 tokens of reasoning on the uncapped call - more than ten times
the cap I had imposed and then interpreted as a model that would not stop.

## 3. The part that matters more than the retraction

All four answers were checked against **Finding 037**, which settled this question by exhaustive
enumeration. Three of them are right. One is not.

| configuration | the answer's claim |
|---|---|
| no max_tokens, thinking on | U_min = N-1 "is not a general lower bound ... it is the minimum number of units for a **connected** network" - **correct**, including the connectivity caveat |
| max_tokens=32000, thinking on | "an achievability result for a connected minimum-utility design" - **correct**, and gives the right generalisation, networks can use **fewer** units "down to N - S for S independent sub-networks" |
| effort=low, thinking on | "an achievability/target result ... General networks can require **fewer** units if they split" - **correct** |
| **thinking disabled** | "not for arbitrary networks, which can require **MORE** units if they are disconnected" - **WRONG, and backwards** |

A disconnected network has **more** components than one, and each component needs only its own
spanning tree, so it needs **fewer** units - which is exactly the mechanism that refuted the
bound in Finding 037, where the 4-stream case attained the optimum with 2 units against N-1 = 4.

**So disabling thinking did not merely lose depth; it produced an answer with the sign of the
effect reversed, on the precise question the project had already settled computationally.**
Finding 038 recommended exactly that as the fix.

## 4. What the corrected guard is for

The guard in `orchestrator/src/llm.ts` stays, with its justification replaced:

  * A request whose max_tokens is too small for the reasoning returns **HTTP 200** with
    `finish_reason: "length"` and an **empty content string**.
  * That is a **failure of the caller's budget**, not of the model, and the adapter raises
    rather than returning `""` so no caller can mistake truncation for an answer.
  * `max_tokens` is now passed only when configured. The default is the model's own
    allowance, which is what the API's examples use.
  * **Thinking is on unless explicitly disabled**, and the config field documents why.

## 5. The lesson, which is not the one I recorded

Finding 038 framed this as "the ninth instance of a number produced in a regime where it does
not mean what it says". That framing was itself the error: **the regime was one I had
manufactured.**

The project's rule is **not to argue from authority** - a claim is not accepted because a
document or a paper says so. **That is not the same as refusing to read the documentation.** I
skipped it, and the cost was mis-attributing my own misconfiguration to the tool and writing a
finding about it.

**The check that would have caught it takes one line of the API reference, and the check that
did catch it was the user's objection.** Worth stating plainly: of the corrections in this
project, the ones from outside the loop have been the most expensive to have missed.
