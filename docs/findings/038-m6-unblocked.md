# Finding 038 - M6 is unblocked: a real LLM, the Cordis reference, and a trap that returns nothing

Status: the API key works, the Cordis sources are cloned and sized, and a first trap is
recorded: **a status-200 completion that contains no answer at all.** An orchestrator that
treated it as a reply would proceed on an empty string.
Reproduce: the calls are in this finding; the reference is at reference/ (gitignored).

## 1. The model endpoint

| | |
|---|---|
| endpoint | https://api.deepseek.com/chat/completions (OpenAI-compatible) |
| key | SECRETS/DEEPSEEK-API.txt, read per run, never written into any committed file |
| models | **deepseek-flash** (DeepSeek-V4.1-Flash) and **deepseek-v4-pro** |
| context | 1,048,576 tokens in, 393,216 out, for both |
| effort levels | low, high (default), max |
| modalities | text and image in, text out |

M6's "an LLM in the loop, doing the actual work rather than executing a script" now has a real
LLM behind it.

## 2. The trap

Three calls, same question, differing only in how thinking is configured:

| call | completion tokens | reasoning tokens | finish | content |
|---|---|---|---|---|
| trivial prompt, default | 28 | 26 | stop | "ok" |
| hard prompt, default | 3000 | **3000** | **length** | **(empty)** |
| hard prompt, reasoning_effort = low | 2000 | **2000** | **length** | **(empty)** |
| hard prompt, thinking disabled | 53 | - | stop | a full answer |

**With thinking enabled the model can spend the entire budget reasoning and emit no content,
returning HTTP 200 with a well-formed body whose message content is the empty string.**
Raising max_tokens from 300 to 3000 did not help - the reasoning simply grew to fill it, 11,641
characters of it. Setting reasoning_effort to low did not help either.

It is fixed by disabling thinking: `"thinking": {"type": "disabled"}`. The trivial prompt
terminates normally even with thinking on, so this is not a blanket failure - it is
prompt-dependent, which is worse, because it will appear intermittently in a long agent run.

**This is the ninth instance of the pattern this project keeps meeting**: a number - here a
response - produced in a regime where it does not mean what it says. The orchestrator must
therefore treat `finish_reason == "length"[[/B]] with empty content as a FAILURE and not as an
answer, in the same way that `linearize.py[[/B]] refuses a dump whose B is identically zero. The
guard belongs in the adapter, at the boundary, so that no caller can forget it.

## 3. The reference

`github.com/cordiverse/cordis[[/B]] cloned to `reference/cordis[[/B]] (gitignored), paper at
`reference/paper[[/B]]. Core is small enough to read in full:

| file | lines |
|---|---|
| fiber.ts | 455 |
| reflect.ts | 253 |
| utils.ts | 250 |
| logger.ts | 214 |
| registry.ts | 182 |
| events.ts | 169 |
| context.ts | 69 |
| service.ts | 70 |
| index.ts | 7 |

plus `loader/` (index 152, internal 118, resolve 61), and packages for `hmr[[/B]], `group[[/B]],
`timer[[/B]], `include[[/B]].

The paper's own framing matches what the certificate knowledge base needs: **revertible effects**
- every context transformation carries an inverse the runtime holds - are temporal
composability, which is what revoking a certificate on crossing a domain boundary is; and
**reactive coeffects** - context changes classified against a coeffect specification - are
spatial composability, which is what keying a certificate to its domain tag is. The unified
context and the declarative loader with hot module replacement are what make the mechanism
inventory pluggable, which is roadmap item (3) at the orchestrator level.

## 4. What this does not establish

  * **Nothing has been built.** No orchestrator, no Cordis integration, no agent loop. This
    round opened the door and identified the reference and the first failure mode.
  * The exact request parameter for thinking is confirmed only for `deepseek-flash[[/B]]; the
    behaviour of `deepseek-v4-pro[[/B]] was not tested.
  * Cost, rate limits and long-run reliability were not measured - one call at a time.
  * The key lives in a file under SECRETS/ and is read per run. It is not in any committed
    file, but it is also not encrypted at rest, and the repository has no secret-scanning.
