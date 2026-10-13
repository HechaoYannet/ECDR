# Finding 045 - The agent audits evidence: 4 of 4 witnesses judged correctly, with the exact values

Status: Finding 043's behaviour was **auditing, not disagreeing**. Given four claimed networks -
two genuine, two false - the model judged all four correctly AND produced the exact minimum hot
utility for each, including a case where the naive shortcut gives the wrong answer. Its reasoning
was captured and it is a complete physical derivation.
Reproduce: cd orchestrator && node node_modules/cordis/bin.js --audit.  Raw reasoning:
runs/witness_audit.json (gitignored; 75,543 chars, 22,253 reasoning tokens)

## 1. The design

Finding 043 showed an agent rejecting a counterexample I had offered, correctly, but could not
say whether it was auditing or merely contrarian, and the reasoning was discarded. This asks the
same capability in ONE call and with a proper mix:

| id | matches | claimed | true Q_H | claim valid? |
|---|---|---|---|---|
| W1 | H1-C1, H2-C1 | 142.5 | **150.0** | no |
| W2 | H1-C1, H1-C2, H2-C1 | 142.5 | **142.5** | **yes** |
| W3 | H1-C2, H2-C2 | **262.5** | **332.5** | no |
| W4 | all four | 142.5 | **142.5** | **yes** |

**W3 is the discriminator.** Its claimed 262.5 is exactly C1's duty - the figure a naive "count
the untouched stream's duty" rule produces - and the true value is 332.5. A model that knows
only the shortcut accepts W3 and is wrong. **And a model that rejects everything scores no better
than one that accepts everything**, which is what W2 and W4 are for.

## 2. The result

| id | said correct | actually | said value | true value | |
|---|---|---|---|---|---|
| W1 | false | false | **150.00** | 150.00 | both right |
| W2 | **true** | true | **142.50** | 142.50 | both right |
| W3 | false | false | **332.50** | 332.50 | both right |
| W4 | **true** | true | **142.50** | 142.50 | both right |

**4 of 4 fully correct** - the verdict and the value, on all four, in one call.

## 3. How it got W3, in its own words

> "C1 no match -> hot utility 262.5. C2 can be heated by H1/H2 process... **H2 cannot heat C2
> because H2 max 90 < C2 min 100+10=110. So only H1 can heat C2.** Max H1-C2 we computed 80 kW.
> C2 demand 150, so remaining 70 kW hot utility required for C2. Thus total hot utility at least
> 262.5 (C1) + 70 (C2 residual) = 332.5."

and the 80 kW, derived rather than assumed:

> "For countercurrent exchanger, at hot inlet 150, cold outlet could be up to 140. At cold inlet
> 100, hot outlet must be at least 110. **Max Q constrained by hot outlet >= 110:
> Q <= cp_h * (150 - 110) = 2 * 40 = 80.** Then cold outlet = 100 + 80/3 = 126.67. Feasible: hot
> inlet 150 with cold outlet 126.67 dt 23.33; hot outlet 110 with cold inlet 100 dt 10."

**That is the whole calculation, done from first principles**: a temperature-feasibility test on
the untouched pair, the countercurrent maximum duty bounded by the approach temperature at
BOTH ends of the exchanger, and the decomposition into the unmatched stream's floor plus the
matched stream's residual.

**It also explicitly refused the shortcut rather than stumbling into the right answer**:

> "Claimed 262.5. Is it correct? **Need check if process heating C2 can be done without requiring
> additional hot utility?** It doesn't affect C1... So C2 needs utility at least 70."

And it named the difficulty before solving it:

> "For fixed set of matches, maximum heat recovery can be found by treating each match as a heat
> exchanger with unknown duty and using temperature constraints and energy balances... **Feasibility
> is nontrivial.**"

## 4. What this settles about Finding 043

**The behaviour was auditing.** It accepted two witnesses and rejected two, and the two it
accepted were the two that are true. A contrarian would have rejected all four; a credulous
reader would have accepted all four. **The mix is what makes the discrimination visible, and the
model passed it.**

**And the capability is the one ECDR actually needs.** The project's rule is that a certificate
is a revocable confidence operator rather than a decision. That only means something if the
holder can TELL when the evidence for it is bad. **An agent that recomputes a claimed witness
from the physics and finds it wanting is an agent that can audit its own certificates** - which
is the property that makes the whole architecture safe rather than merely organised.

## 5. Limits

  * **One call, one model, four witnesses.** The two it accepted are also the two where the
    answer equals the unrestricted global minimum, which is arguably the easier judgement: W2 and
    W4 could be settled by knowing Q_H_min, without the exchanger-level analysis W3 required.
    **So the test is asymmetric and the score of 4/4 overstates the difficulty of half the task.**
  * W3's true value 332.5 comes from the corrected model of Finding 044, which was itself
    validated only against the problem table in the all-matches regime and against one hand
    computation in the restricted regime. **The ground truth here is better founded than it was
    in Finding 037, but it is not independently confirmed.**
  * The reasoning is 75,543 characters and only the W3 passage was read. The rest, including how
    it settled W2 and W4 and whether it derived the global minimum correctly, is unexamined.
  * The agent was asked to audit, so it knew auditing was the task. **Whether it would audit
    unprompted - when the witness arrives from its own search rather than from an adversary - is
    untested, and that is the case that matters.**
