# Decision 001 - Q4: simulation kernel and orchestrator

Date: 2026-10-12. Decided by the user; recorded here with the engineering assessment.

## Decision

  * **Simulation kernel: mature third-party implementations, not in-house.** In-house
    development is high cost and cannot serve as an independent validator anyway,
    since a second implementation by the same author is not independent.
  * **Orchestrator: build on DeepSeek Harness, whose composition layer is Cordis**
    (arXiv 2608.25512, "A Programming Paradigm for Spatiotemporal Composability",
    Yifan Shi, Wei Zhang, Tianyi Cui, 2026-08-26; source checkout at
    D:/otherProject/dsh-win32).

## Why Cordis is a good fit, in its own abstractions

Cordis formalizes two orthogonal dimensions, and both map onto a requirement ECDR
already has from Finding 003:

| Cordis concept | Formal content | ECDR requirement it satisfies |
|---|---|---|
| **Revertible effects** | every context transformation carries an inverse that the runtime holds; temporal composability | CORE-style backjumping requires reverting the state of an abandoned route. Getting this from a runtime that tracks inverses is far safer than hand-rolled undo. |
| **Reactive coeffects** | each context change is classified against a component coeffect spec, driving activation and deactivation; spatial composability | Certified conflict cores must be keyed by decision identity and dependencies, and cores must be evicted on superset. A declarative dependency mechanism is exactly that bookkeeping. |
| **Declarative component loader with configuration reconciliation and hot module replacement** | components can be added and removed at runtime without disturbing others | The **mechanism inventory** becomes a set of pluggable components: adding a mechanism class is loading a component, and removing one must leave no residue. |

The "observational equivalence up to which the effects of distinct components
interleave without disturbing one another" property is what makes an ablation honest:
removing the certificate component must not perturb anything else, so the experiment
measures evidence use rather than implementation drift.

## Consequences to work out

1. **Language boundary.** DSH is Node/TypeScript; the physics stack is Python
   (numpy/scipy) and the L1/L2 kernels are separately chosen. The boundary should be
   an explicit, versioned interface with the certificate checker on the Python side
   and never in the agent's process, per Finding 003 integrity rule 5.
2. **Mature L1 kernels** (nonlinear, saturating, perturbed) and **mature L2 kernels**
   (independent implementation) must come from *different* toolchains, otherwise L2
   is not independent. Candidates to evaluate: OpenModelica, Julia
   DifferentialEquations, SciPy, FEniCS/scikit-fem, and for multi-body work an
   established library. Open for decision.
3. **Cost ledger.** The kernel choice fixes the cost model, which must align with
   SimulCost's analytically defined, platform-independent simulator cost so that
   budget-matched comparison is meaningful.
4. **Reproducibility.** Pin and hash every kernel version into the run manifest
   (Finding 003 integrity rule 6).
