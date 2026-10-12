# Finding 039 - The M6 orchestrator exists: Cordis composition, physics across a process boundary

Status: the orchestrator skeleton runs. A Cordis composition drives the verified physics across
a process boundary and installs and revokes a domain-tagged certificate as an effect. **The
LLM is not in the loop and there is no agent loop yet.**
Reproduce: cd orchestrator && node node_modules/cordis/bin.js

## 1. The architecture decision, and why the boundary is not cosmetic

The physics is Python, which is where it was built and verified across 38 findings. Cordis is
TypeScript. Rather than port either, the orchestrator is TypeScript and the physics is reached
through a **process boundary**: `orchestrator/python/bridge.py[[/B]] takes one JSON request on
argv and writes one JSON response on stdout.

**The boundary is required by the project's own discipline, not chosen for convenience.** The
certificate checker must live in a separate code path from agent code and never in the agent's
process. A process enforces that; a convention inside one language does not. A model-generated
string cannot reach into the checker's address space, and a checker bug cannot corrupt the
agent's state.

The bridge prints nothing but the response, so a stray print is a protocol error rather than a
silent corruption.

## 2. What the reference taught, and the one thing it cost

Cordis is driven by a **loader reading `cordis.yml[[/B]]**, not by programmatic composition. The
launcher mounts the loader and everything else is configuration:

    - name: './src/physics.ts'
    - name: './src/certificates.ts'
    - name: './src/demo.ts'

The concepts that mattered:

| concept | what it gives ECDR |
|---|---|
| `Service[[/B]] subclass, `super(ctx, 'name')[[/B]] | a capability occupies `ctx.<key>[[/B]]; consumers look it up rather than import it |
| `inject[[/B]] | declares a dependency; **load order is irrelevant**, Cordis starts a plugin when its services exist |
| `ctx.effect()[[/B]] | **registrations are revertible effects** |
| declarative loader + HMR | the mechanism inventory is pluggable, which is roadmap item (3) at the orchestrator level |
| `ctx.waterfall[[/B]] | policy interception that can delegate or short-circuit |

**`ctx.effect()[[/B]] is the whole reason Cordis is the right base.** The paper's *revertible
effects* mean every context transformation carries an inverse the runtime holds. A certificate
is exactly that: `install()[[/B]] returns a disposer, `revoke()[[/B]] calls it, and **plugin
unload does the same thing by construction**, so a certificate cannot outlive the component
that asserted it. The project's rule that certificates are revocable statements rather than
decisions is now enforced by the runtime rather than by care.

**The cost**: the npm package `cordis@4.0.0-rc.10[[/B]] declares `@cordisjs/plugin-loader[[/B]] and
`@cordisjs/plugin-include[[/B]] as peer dependencies, and its `bin.js[[/B]] fails with
`ERR_MODULE_NOT_FOUND[[/B]] without them. They are not installed automatically.

**And one silent failure, recorded because it will recur**: a plugin whose `inject[[/B]] is never
satisfied stays PENDING, **does not keep Node's event loop alive, and causes the process to exit
0 with no output at all**. The first smoke test of this round died that way. A composition that
prints nothing is therefore ambiguous between "finished" and "never started", and the
orchestrator will need a liveness assertion rather than trusting a zero exit.

## 3. What actually ran

    [physics] Q_H_min = 142.500000  Q_C_min = 150.000000  pinch(shifted) = 105
    [cert] installed heat.utility.lower-bound  live = 1
           tag = {"dt_min":10,"streams":4,"phase":"single","cp":"constant"}
    [verdict] requirement Q* = 128.2500   certificate = 142.5000
              best unconstrained network = 142.5000
    [verdict] the certificate decides it infeasible: true
    [cert] after revoke, live = 0

The numbers are the ones Finding 036 verified by hand and by exhaustive enumeration -
142.5, 150.0, pinch 105 - so the orchestrator is driving the real physics and not a stub. The
certificate carries its domain tag, and install and revoke behave as effects.

## 4. What this is not

  * **No LLM in the loop.** Finding 038 established the endpoint and the empty-content trap;
    the adapter is not written.
  * **No agent loop.** The demo is a fixed script; it proposes nothing, allocates no budget and
    derives no certificate of its own.
  * **No events, no tools, no session.** The certificate-revoked event is declared but nothing
    listens.
  * **The vibration domain is not reachable from the orchestrator** - only the heat bridge
    exists.
  * The composition runs once and exits. There is no daemon, no persistence, no recovery.

## 5. Next

  1. The LLM adapter as a service, with the `finish_reason == "length"[[/B]] and empty-content
     guard **inside the adapter** so no caller can forget it.
  2. The agent loop: propose a structure, ask the physics, install or revoke a certificate,
     repeat against a budget.
  3. A scripted policy first, so that when the end-to-end run misbehaves it is clear whether
     the orchestrator or the model is at fault.
