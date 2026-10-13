# Finding 041 - A real LLM agent proposes the exact thermodynamic minimum, and the checker catches it when it does not

Status: M6's loop runs end to end with a real model. **Two of three proposals were EXACTLY
Q_H_min** - the tightest sound certificate - computed from stream data alone at max reasoning
effort. The third was wrong in an informative way, and the checker refused it.
Reproduce: cd orchestrator && node node_modules/cordis/bin.js --llm

## 1. The run

    [policy] llm
    [scenario ] textbook 4-stream  dt_min=10  streams=4  requirement Q*=128.25
    [propose  ] value 142.5000 kW  ->  SOUND  (<= Q_H_min 142.500000)
    [certify  ] installed heat.utility.10 at 142.5000 kW
    [decide   ] requirement 128.2500 is OUT OF REACH inside this domain
    [revoke   ] heat.utility.10 revoked, domain crossed
    [scenario ] textbook 4-stream  dt_min=5  streams=4  requirement Q*=128.25
    [propose  ] value 130.0000 kW  ->  SOUND  (<= Q_H_min 130.000000)
    [certify  ] installed heat.utility.5 at 130.0000 kW
    [decide   ] requirement 128.2500 is OUT OF REACH inside this domain
    [revoke   ] heat.utility.5 revoked, domain crossed
    [scenario ] textbook 4-stream  dt_min=2  streams=4  requirement Q*=128.25
    [propose  ] value 142.0000 kW  ->  REFUTED (> Q_H_min 122.500000)
    [budget   ] exhausted

The model was given the stream data, the requirement, dt_min, and the list of values it had
already proposed. **It was NOT given Q_H_min, any pinch analysis, or the problem table.**

**It proposed 142.5000 and 130.0000 - in both cases exactly the thermodynamic minimum**, to four
decimal places. Those are not merely sound certificates: they are the **tightest** sound
certificates available, the boundary of what can be claimed. A certificate at that value
excludes every requirement below it and nothing else.

## 2. The failure is the interesting part

On the third scenario dt_min had been tightened from 5 to 2, which LOWERS the minimum utility
from 130.0 to 122.5. **The model proposed 142.0 - a value near the dt_min = 10 answer - and was
refuted.**

The cause is legible in the transcript: after a domain change it **reused a previously
successful value instead of re-deriving the bound under the new assumption**. Tightening the
approach temperature reduces the utility requirement, and the proposal did not move down with
it.

That is a real capability limit, and it is exactly the limit the project cares about: **the
certificate is valid only inside its domain tag, and the agent did not update its reasoning when
the tag changed.** The loop's own design - revoke on domain crossing - is what kept the stale
certificate from being carried across.

**And the check worked**: 142.0 > 122.5 was REFUTED, no certificate was installed, and the
knowledge base ended empty rather than holding a false bound. **A wrong proposal cost a budget
unit and nothing else**, which is precisely the asymmetry the project is built on - an unsound
certificate would have been unrecoverable, an unsound *proposal* is free.

## 3. Configuration, corrected

Per Finding 040 and the API documentation:

  * `reasoning_effort: "max"` - the strongest setting, mapping to the model's max effort
  * **no `max_tokens`** - the API's own examples omit it and the default is the model's
    full output allowance; capping it truncates the reasoning and yields an empty answer
  * thinking **on** (the default)

## 4. The silent-failure class recurred, twice, in the same debugging session

Node runs TypeScript by stripping types, and it does so in **strip-only mode**: it rejects
**TypeScript parameter properties** (`constructor(private readonly config: LLMConfig)`).

When a module fails to parse, the Cordis loader **exits 0 and prints nothing at all.** There is
no error, no stack, no diagnostic. The composition simply does not run.

This is the **second instance of the Finding 039 class**, where a plugin that never activates is
indistinguishable from one that finished. Here it was worse: the failure was a **parse error**,
which one would expect to be the loudest possible failure.

**What found it was importing each module directly** and reading the exception Node had been
raising all along:

    node -e "import('./src/llm.ts').then(...).catch(e=>console.log(e.message))"
    -> TypeScript parameter property is not supported in strip-only mode

The loader was swallowing it. **Any orchestrator built on this stack needs a startup self-check
that imports every configured plugin and reports parse failures**, because the loader will not.

## 5. What M6 now has

| element | state |
|---|---|
| Cordis orchestrator, declarative plugin tree | works |
| physics behind a process boundary | works, drives the verified values |
| revocable, domain-tagged certificate store | works, `ctx.effect()`-backed |
| a checker that decides rather than a caller that asserts | works, refutes unsound proposals |
| a real LLM in the loop | works, `reasoning_effort: max`, no token cap |
| one run costs | 3 model calls and 3 physics calls |

## 6. Limits

  * **Three proposals, one scenario, one run.** Not a survey, and the model may have seen the
    textbook 4-stream problem in training. **That is a real concern and it is not addressed
    here**: the numbers being exact is consistent both with genuine reasoning from the stream
    data and with recall, and this run cannot distinguish them.
  * The requirement was never actually MET. Every scenario ended with the requirement out of
    reach and a domain change, and the run stopped on budget. **No structure was constructed
    that closes a gap** - which is half of what M6 is for.
  * The agent cannot yet propose a NETWORK, only a bound. The search half of ECDR is not in the
    loop.
  * ''Budget'' counts physics calls and proposals together; there is no cost model for tokens.
  * One model, one effort setting. Nothing was compared.
