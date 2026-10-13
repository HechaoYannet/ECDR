# Finding 042 - Not recall: 6 of 6 exact on randomly generated scenarios, in one call

Status: the objection Finding 041 raised against itself is answered. The model computed the
thermodynamic minimum hot utility **exactly, on all six randomly generated scenarios**, in a
single call. It is not recalling the textbook problem. **What this does not show - and the
distinction is the whole of M6 - is that it can DERIVE a certificate rather than APPLY one.**
Reproduce: scripts/step68_llm_scenarios.py then cd orchestrator && node node_modules/cordis/bin.js --random

## 1. The objection, and how it was removed

Finding 041 recorded that its two exact answers came on the standard textbook 4-stream problem,
which the model may have seen in training, and that exactness there was consistent both with
reasoning and with recall. It said that unless this was settled, the number proved nothing.

Six scenarios were generated from a seeded generator in this session, with stream counts of 4
to 6, temperatures from 20 to 260 C, heat capacity flowrates from 1 to 9 kW/K, and approach
temperatures of 5, 10, 15 and 20 C. Ground truth is the problem table of Finding 036, itself
verified against an independent LP and against **exhaustive enumeration of every network**. All
six have a positive minimum, so no certificate is vacuous.

**The prompt contains only the stream data.** `Q_H_min` appears in `src/random.ts` at lines
82, 87 and 88 - all after the call - and the user message is assembled from
`s.streams` alone. No tools were provided, so there was no other route to the answers.

## 2. The result

One call, max effort, **106.1 seconds**, and a **168-character** response.

| id | proposed | truth | ratio | error |
|---|---|---|---|---|
| R1 | 142.0000 | 142.0000 | 1.0000 | 0.0000 |
| R2 | 233.0000 | 233.0000 | 1.0000 | 0.0000 |
| R3 | 1503.0000 | 1503.0000 | 1.0000 | 0.0000 |
| R4 | 51.0000 | 51.0000 | 1.0000 | 0.0000 |
| R5 | 243.0000 | 243.0000 | 1.0000 | 0.0000 |
| R6 | 170.0000 | 170.0000 | 1.0000 | 0.0000 |

**6 of 6 sound, 6 of 6 exactly tight, mean ratio 1.0000.** A certificate at exactly Q_H_min is
the tightest sound certificate there is: it excludes every requirement below it and nothing
else. **Six independent pinch problems solved to the last decimal in a single response.**

## 3. What this establishes

**The model is a competent practitioner of pinch analysis.** It can take raw stream data and
produce the exact thermodynamic bound, repeatedly, on instances that did not exist before this
session. For M6 that matters: the premise that an LLM can do the domain work rather than
execute a script is now supported by a measurement rather than by hope.

It is also economical. One call, 106 seconds, 168 characters of output. The reasoning is in
`reasoning_content` and is not counted in the response size.

## 4. What it does NOT establish, and this is the part that matters

**Applying a known method exactly is not deriving a certificate.** Pinch analysis is a standard
textbook technique; the model executed it correctly. **ECDR's claim, and M6's stated success
criterion, are about DERIVING a certificate that a domain expert accepts as non-obvious.**

  * Nothing here shows the model can find an invariant that is not already in the literature.
  * Nothing here shows it can decide *which* invariant is worth computing for a new domain, or
    how to tag its domain of validity, or when to revoke it.
  * Finding 041's failure still stands and is a different mode entirely: after the domain
    changed, the model **reused a previously successful value instead of re-deriving under the
    new assumption**. It computed correctly here because each problem was presented fresh, in
    one context, with no prior answer to anchor on. **The failure appears precisely when a
    certificate has to be maintained across a change, which is the ECDR setting.**

**So the honest reading is narrow but real: the model can be trusted to compute a known
certificate correctly, and has not been shown to derive a new one.** The first is a
precondition for M6, not M6.

## 5. Limits

  * **Six scenarios, one call, one model, one effort setting.** Enough to refute the recall
    objection, which is what it was for; not enough to estimate an error rate, and a
    zero observed error rate over six samples bounds nothing usefully.
  * All six have positive minimum utility and none is near-vacuous. Cases where the answer is
    zero are a different regime - Finding 036 found them vacuous for the rule-out property.
  * The scenarios are single-phase constant-cp streams. That is the certificate's domain tag
    and the model was not tested outside it, nor asked to say where the tag should end.
  * The model was told what to compute. It was not asked whether a utility bound is the right
    certificate for the problem, which is the question an agent running a whole research flow
    would have to answer.
  * **The reasoning was not inspected.** `reasoning_content` was not captured or read, so
    whether the model performed a problem table, a composite curve, or something else entirely
    is unknown. That is worth capturing next and costs nothing extra to record.
