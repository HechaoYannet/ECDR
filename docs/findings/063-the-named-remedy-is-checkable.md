# Finding 063 - The named remedy is a declared, checkable field, and it refutes a bad certificate alone

Status: **the mechanism Finding 057 said was missing now exists, costs one enumeration (0.54 s), and
separates a false certificate from a true one WITHOUT a reader, an argument analysis or a
confidence score.** And the prose reader, given the same evidence, rejected **both** - including the
true one - so it is unreliable in both directions and should not be relied on.
Reproduce: cd orchestrator && node node_modules/cordis/bin.js --argue.
Log: runs/argue_log4.txt

## 1. What was built

A certificate's `names` field is no longer prose. It declares what the certificate **asserts**
about the remedy it names, from a controlled vocabulary:

    remedy   "cross-pinch"          the thing the certificate says is missing
    asserts  "forbidden"            NO design attaining the requirement may use it
             "required"             some design attaining the requirement DOES use it

and the harness **tests that assertion directly by enumeration**, before any reader sees the
argument. This is the third of Finding 049's three deviations from the roadmap addressed as a
mechanism rather than a demonstration.

## 2. The result

    FALSE V=6  asserts "cross-pinch is forbidden"   (its own name says the repair is impossible)
      enumerated 192 designs; 8 attain 142.5 kW; 8 of them use the remedy
      witness: 5 units, match H1-C1, 20.000 kW, Q_H = 142.500
      ** assertion_holds = false **

    TRUE  V=5  asserts "cross-pinch is required"
      enumerated 192 designs; 8 attain 142.5 kW; 8 of them use the remedy
      witness: 5 units, match H1-C1, 20.000 kW, Q_H = 142.500
      ** assertion_holds = true **

**The false certificate is refuted by its own declared field**, with a concrete witness - a 5-unit
design attaining the requirement that **uses** the exchanger it called impossible.

**This is the check Finding 059 identified and the architecture was not running.** Finding 057's
false certificate asserted, in its own name, that the repair was forbidden. One enumeration says
otherwise. **No reader, no argument analysis, no confidence score.**

## 3. And the reader failed in both directions

Given the falsification evidence - a complete enumeration, and for the false cases a concrete
counterexample - the reader returned:

| certificate | truth | reader's verdict |
|---|---|---|
| TRUE V=5 | true | **flawed at 0.85** |
| FALSE V=6 | false | flawed at 0.9 |
| AGENT V=6 | false | flawed at 0.99 |

**It called everything flawed.** Finding 057 recorded that a reader which can only read accepts
falsehoods; **this records that a reader handed the evidence still does not discriminate - it simply
rejects.** The criterion the run set for itself - "the reader must call the TRUE one sound and the
FALSE one flawed" - **FAILED**, and the run said so rather than reporting the two successes.

**One honest qualification, and it cuts against the demonstration**: the TRUE certificate's argument
text was weak. It asserted a spanning tree on six nodes and did not rule out four-unit designs, and
the reader's objection - "HENs need not connect both utilities" - is a fair criticism of **that
argument**, not of the claim. **So the reader's rejection of the true case is partly my fault**, and
a clean version would need a proper argument for V = 5 before the comparison means much.

## 4. What this settles

  * **The remedy assertion is a usable check.** It is cheap, mechanical, and it resolves exactly the
    case that defeated the prose reader. It should run **first**, and a certificate whose assertion
    fails should be refuted without consulting anything else.
  * **The prose reader is not usable**, in either direction. Kept in the repository as evidence and
    not as a component.
  * **A certificate can be wrong in its claim and right in its name** (Finding 059), so refuting the
    claim does not discard the name - and now the name is what gets tested.

## 5. A silent-failure trap, which cost two runs

The remedy test was built, run, and produced **nothing at all**: the header printed and Node exited
0. The cause was **`STREAMS` being undefined** in `argue.ts`. A ReferenceError thrown inside an
async Cordis plugin is **swallowed**, and a pending fiber does not keep Node alive, so the process
ends successfully with no output and no error.

**The fix was wrapping the plugin body in try/catch**, and it surfaced the error immediately - and
then surfaced a second, older bug (`v2 is not defined`) at the very end of the same file.

**This is the third time in this project that a silent exit 0 hid a real failure**, and the pattern is
worth recording as a property of the tool rather than an accident: **in Cordis, a throw in an async
plugin and a missing dependency look identical to success.** Any plugin whose silence could be a
failure must print something before and after its work.

## 6. Limits

  * **One domain, one remedy, one assertion vocabulary.** "Cross-pinch" is mechanically checkable
    because a transfer at two different temperature levels is a computable property. A remedy like
    "change the ground coupling topology" has no such test and M5's criterion would need a different
    operationalisation - which is the same limit Finding 059 recorded.
  * **The enumeration is over the 4-stream design space**, 192 designs, complete and small.
  * **The reader comparison is confounded** by the weak argument text for the true case, as stated.
  * **The assertion is only as good as the enumeration.** `max_units` bounds the search; a design
    using the remedy above that bound would not be found.
  * **Nothing here is a third-party check.** Both the assertion test and the enumeration are the
    project's own code; the independence in this project is the L2 tool, not this.
