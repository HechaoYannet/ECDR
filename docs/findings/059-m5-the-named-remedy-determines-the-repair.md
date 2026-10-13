# Finding 059 - M5: the named remedy DOES determine the repair, and it is a cross-check

Status: **M5's criterion is met on this case.** A certificate whose claim was FALSE, whose argument
was wrong, and which Finding 057 showed an independent reader would accept - **named the one thing
the working design needed.** Acting on the name constructs a structure attaining the requirement.
And the name turns out to be a refutation test the harness was not running.
Reproduce: scripts/step81_m5_named_remedy.py.  Data: runs/m5_named_remedy.json

## 1. M5's criterion, as the roadmap states it

Section 9, milestone M5:

> the certificate names an invariant, and acting on that name constructs a working structure
> **falsified if**: the named invariant does not determine a useful repair

and section 6, Layer B (iv): a certificate that says only "impossible" is a gate, while one that
says which invariant is violated **tells the agent what to build**.

## 2. The case, and it is the awkward one

Finding 057's certificate claimed V = 6 and named "a cross-pinch exchanger" as what was missing,
while asserting in the same breath that such an exchanger is forbidden. Its claim is false: **5
units suffice** (Finding 056). Its argument rested on the assumption the name denies.

The test is therefore not whether the claim is true. It is: **does acting on the name construct a
working structure?**

## 3. The answer

    pinch (shifted) = 105.0000
    intervals 0-2 ABOVE, 3-5 BELOW

    design attaining Q_H_min with 5 units:
      process H1-C1, H1-C2, H2-C1   heater C2   cooler H2
      ** H1-C1 transfers 10.000 kW ACROSS the pinch **

**The named remedy is exactly what the working design supplies.** Allowing the cross-pinch
exchanger - acting on the name - constructs a structure that reaches Q_H_min.

**So M5's falsifier is answered: "the named invariant does not determine a useful repair" is false
here.** The name determined the repair.

**And the certificate that named it had a false claim and a bad argument.** The name was right while
both of the other fields were wrong.

## 4. Why this matters more than it looks

**A refuted certificate is not thereby useless.** Its name can be the repair, which is precisely
what Layer B (iv) is for. A library that discards a certificate on refutation loses the part that
told the agent what to build.

**And the name is a refutation test.** Finding 057's reader accepted a false certificate **whose own
name asserted the repair was forbidden**. It did not occur to the architecture to ask:

    you say a cross-pinch exchanger is missing and also that it is impossible.
    which is it?

**Asking that refutes the certificate at once, for the cost of one enumeration**, and it needs no
reader, no argument analysis and no confidence score. **The harness was checking the claim and
ignoring the name.**

## 5. My own error in this round, recorded

**The first version of this script decided M5 from the wrong quantity.** It counted designs with at
most four units attaining Q_H_min, got 0, and printed "the named remedy is not what was missing" -
**directly beneath its own evidence showing H1-C1 transferring 10 kW across the pinch.**

**That is the fourth instance in this project of a verdict not computed from the run's own data**,
and it is a standing rule I wrote down early ("never print a verdict not computed from the same
run's data"). The two questions are different: whether fewer units suffice is not whether the named
remedy is what is needed. The corrected script computes the spanning matches first and decides from
them, and keeps the four-unit count as a separate line.

## 6. Limits

  * **One certificate, one scenario, one named remedy.** M5's criterion is met once, on the case
    the project already knows best.
  * **The name was tested by enumeration, not by interpretation.** "A cross-pinch exchanger" is
    mechanically checkable here because the pinch is a computable temperature. A name like "change
    the ground coupling topology" has no such test, and M5's criterion would need a different
    operationalisation.
  * **The design space is the 4-stream case**, so the enumeration is complete and small. In a space
    too large to enumerate, testing the name would itself need a certificate or a search.
  * **The name being right does not make the certificate reliable.** Finding 057's reader gave it
    0.95. What this finding shows is that the reliability question had a cheap answer available and
    unused, not that the certificate was fine.
  * **This does not establish the agent can name a remedy.** The name here came from a model that
    simultaneously asserted the premise it denies; whether it named the right thing for the right
    reason is not shown.
