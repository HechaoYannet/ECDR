# Finding 057 - A reader that can only READ accepts a false certificate

Status: the certificate was built as the roadmap describes it - an object carrying its soundness
argument and naming the remedy - and judged by a reader in a separate context. **The reader accepted
a false certificate at confidence 0.95, accepted a deliberately flawed control at 0.88, and the
false certificate was installed.** The mechanism is not decorative; it is wrong as built, and the
reason is specific.
Reproduce: cd orchestrator && node node_modules/cordis/bin.js --argue.  Data: runs/argue_result.json

## 1. What was built, addressing Finding 049's three deviations

  * the certificate carries its **argument**, not just a number (roadmap line 98);
  * it **names the structural remedy**, or section 6 Layer B (iv) calls it a gate;
  * it carries a **domain tag**, which line 99 makes the basis of revocability;
  * and the judgement is a **confidence**, not a gate - the extension recorded in Finding 049.

The reader was a separate model call, in a separate context from the agent, given the problem, the
claim and the argument, **and neither answer**. It was told to look for unstated conditions, steps
that do not follow, and things never considered.

## 2. The result

| | value | argument | reader's verdict |
|---|---|---|---|
| the agent | **V = 6** (truth 5) | pinch decomposition: at least 3 above, 3 below, no exchanger serves both | **sound, 0.95** |
| the control | V = 6 (known false) | the same argument, written out in full | **sound, 0.88** |

**The reader did not discriminate, and the false certificate was installed at confidence 0.95.**

## 3. Why, and it is specific

**Both arguments rest on the same unstated assumption: that no exchanger can span the pinch.** The
control states it outright ("no feasible exchanger can serve both above and below"); the agent's
argument names the same belief in its remedy field ("the 90/80 pinch forces separate above/below
subnetworks").

**The reader was given prose and the problem statement. It was given no physics.** A reader that does
not independently know whether a unit may span the pinch cannot detect that both arguments depend on
the answer to that question. **It read carefully and had nothing to check against.**

## 4. The contrast that explains it

**Finding 045 put four claimed witnesses in front of the same kind of reader and it found the defect
in two of them**, with the exact corrected values. **What was different is that there it was given
concrete networks and could evaluate them.** It caught the flaw by computing C2's duty, checking H2
against C2's temperature, and bounding the exchanger - **not by reading the prose about them.**

**So the rule the two experiments establish together is:**

    a reader that can TEST finds flaws;  a reader that can only READ accepts them.

Section 3 line 98 requires a soundness argument **checkable by a third party**. **This experiment
says the third party must have test access to the domain, not merely the text of the argument.**
An argument-reading check with no access is a plausibility check, and plausibility is exactly what a
confidently written wrong argument has.

## 5. An unlooked-for result: the remedy was right while the claim was wrong

The certificate **named** "a cross-pinch exchanger" as what is missing. **That is correct.** Finding
056's optimal design is a spanning tree whose process part crosses the pinch, and the agent's own
assumption that this is impossible is precisely the defect in its argument.

**So the "names" field was right and the "claim" field was wrong, in the same certificate.** Layer B
(iv) requires a certificate to name the remedy so that it is not a gate. **This shows the naming is
not downstream of the claim being correct** - which is useful, because it means a certificate can be
partially useful even when it is refuted, and it also means **a correct-looking remedy is not
evidence that the claim is sound.**

Had the architecture used the named remedy as a cross-check - "is a cross-pinch exchanger actually
impossible?" - it would have caught the error. **It did not ask.**

## 6. The agent's own behaviour, for the third time

**V = 6 with the pinch-decomposition argument is now the agent's answer in three separate runs**
(Findings 043 turn 1, 046, and here), across two different framings and with the reply guaranteed.
**It is not noise.** The agent holds a specific false belief about pinch spanning, states it
confidently, and has been corrected only when given a counterexample it could evaluate.

## 7. What this changes

  * **The argument-reading checker as built is not fit for purpose** and must not be relied on. It
    installed a false certificate.
  * **The check needs test access.** Either the reader is given a search it can run, or the harness
    runs a falsification attempt and hands the reader its result - which is what made Finding 045
    work.
  * **The confidence was 0.95 for a false claim and 0.88 for a deliberately flawed one.** A
    confidence that high on a wrong answer is worse than no confidence, because it propagates.
  * **The named remedy is a usable cross-check** and was not used.

## 8. Limits

  * One run, one problem, one agent call, one reader call per certificate. The control was judged by
    a separate call with the same system prompt.
  * **The problem statement did not mention whether units may span the pinch**, which is the exact
    fact both arguments turn on. Giving it would have made the task easier and the reader's job
    different; withholding it made the reader's failure likely and the experiment a fair test of
    reading without access.
  * The reader's reasoning was not captured - only its verdict - so whether it considered pinch
    spanning and dismissed it, or never raised it, is unknown.
  * **The install threshold (0.6) was mine and arbitrary.** A stricter one would have blocked this
    certificate for the wrong reason, since the reader was confident.
