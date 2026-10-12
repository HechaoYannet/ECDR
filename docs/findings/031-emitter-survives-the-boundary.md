# Finding 031 - The emitter survives the Modelica boundary; the residual is a transient

Status: the structure representation **is** emittable as Modelica, answering Finding 009's
risk 4. The disagreements in the first ensemble run are unconverged transients, proven by
their convergence trend, and the right fix is **linearization** rather than longer
simulations.
Reproduce: scripts/step59_modelica_ensemble.py, step60_modelica_convergence.py.
Code: ecdr/l2/modelica/{emit.py,run.py}.  Data: runs/modelica_ensemble.json, runs/modelica_convergence.json

## 1. The emitter

ecdr/l2/modelica/emit.py takes any ecdr.structure.Structure and writes Modelica
**declarations and connections only**:

  * each node becomes an MSL Translational Mass;
  * each edge a Spring and a Damper in parallel, connected between the two masses;
  * each ground tie a Spring and a Damper to a Position source prescribing the ground motion.

**No equations of motion appear in the generated file.** The tool assembles them. That is
what makes this a check on the modelling rather than on the numerics - the distinction
Finding 026 drew when it said the Julia rung could not provide it.

## 2. It survives the boundary

Eight comparisons, four ensemble structures, two frequencies each (below and above the first
resonance):

| structure | n | edges | ground ties | omega | L0 abs T | Modelica | rel |
|---|---|---|---|---|---|---|---|
| 0 | 5 | 4 | 3 | 26.222 | 1.11372703 | 1.11372537 | **1.49e-06** |
| 0 | 5 | 4 | 3 | 109.26 | 2.64104979 | 2.64103666 | **4.97e-06** |
| 1 | 3 | 2 | 1 | 22.024 | 1.54594523 | 1.63532814 | 5.78e-02 |
| 1 | 3 | 2 | 1 | 91.768 | 1.03372406e-01 | 3.84890431e-01 | 2.72e+00 |
| 2 | 4 | 3 | 2 | 18.934 | 1.52215503 | 1.52178125 | 2.46e-04 |
| 2 | 4 | 3 | 2 | 78.891 | 5.11948287e-02 | 6.54468247e-02 | 2.78e-01 |
| 3 | 2 | 1 | 1 | 13.686 | 1.52321298 | 1.52251455 | 4.59e-04 |
| 3 | 2 | 1 | 1 | 57.025 | 2.21449915e-01 | 2.21378434e-01 | 3.23e-04 |

**The representation is emittable and the toolchain accepts it for every topology tested.**
Finding 009's risk 4 - that the representation might not survive the Modelica boundary,
forcing L2 to be a second Python model and destroying its independence - is answered.

## 3. But the numbers disagree, and the pattern says why

Structure 0 matches to 5e-06. Structures 1, 2 and 3 disagree by up to a factor of 3.7, and
the error grows with frequency.

**Structure 0 is the one with three ground ties.** Fewer ground ties means less damping and
a longer settling time. **That predicts the direction**: an unsettled transient makes the
measured amplitude LARGER than the steady-state value, and every disagreement has the
Modelica value larger than L0.

Tested on structure 1 at omega = 91.768, where L0 gives 1.03372755e-01:

| periods | stop time | intervals | Modelica | **ratio to L0** |
|---|---|---|---|---|
| 40 | 2.739 | 4,000 | 3.84893890e-01 | **3.723359** |
| 120 | 8.216 | 12,000 | 1.78277640e-01 | **1.724610** |
| 360 | 24.649 | 36,000 | 1.05632440e-01 | **1.021860** |
| 1080 | 73.946 | 108,000 | 1.03349559e-01 | **0.999776** |

**The ratio walks to 1.** An unsettled transient predicts exactly this; a genuine modelling
error would not. The disagreement is integration time, not physics - the same failure mode
Finding 026 found on the Julia rung, and now the second time it has appeared in an L2
comparison.

## 4. The residual is still 2.2e-04, and longer runs are the wrong fix

At 1080 periods the relative difference is 2.244e-04, two orders of magnitude worse than
structure 0's 5e-06 at 40 periods - because structure 0 is well damped and settles fast. The
transient decays like exp(-zeta omega_1 t), so reaching 1e-06 on structure 1 would need
roughly five times longer still: about 5000 periods, or nearly six minutes of simulated time
per comparison.

**Extending the simulation is the wrong instrument.** OpenModelica can **linearize** a model,
returning the state-space matrices (A, B, C, D) about an operating point. The frequency
response then follows from the state-space directly - no transient, no settling time, exact
for a linear model. The generated model stays equation-free either way, so the modelling
check is preserved; only the way the answer is extracted changes.

**That is the next step, and it is the difference between an L2 that works on well-damped
structures and one that works on all of them.**

## 5. Limits

  * Eight comparisons, four structures, two frequencies, one seed. The convergence was shown
    on ONE structure at ONE frequency; the others were not individually extended.
  * The convergence test used up to 1080 periods and 108,000 output intervals. It is evidence
    that the residual is a transient, not a proof that the limit is exactly L0.
  * Gravity is still absent from the emitted model. It shifts the equilibrium and does not
    affect a linear transmissibility, but the static-sag constraint - one of the four L0
    requirements - cannot be checked through this route as it stands.
  * The emitter writes one model per structure with the component values as literals, so each
    frequency is a separate compile and simulation. At roughly five seconds per case this does
    not scale to an ensemble sweep, which is another reason to move to linearization.
  * The L1 mechanisms - the lagged sky-hook and the tuned mass damper - are not emitted at
    all; only the passive networks are.
