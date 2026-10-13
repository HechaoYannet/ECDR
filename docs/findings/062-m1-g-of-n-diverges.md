# Finding 062 - M1: g(N) -> infinity holds, and constant coverage is not necessary

Status: **M1's falsifier - "g(N) turns out bounded" - is triggered for one member of this library
and NOT for two others.** The modal certificate is bounded, exactly and for a structural reason.
The slow certificate has coverage that does not decay. And the fast certificate **decays and still
has g(N) -> infinity**, because the space grows super-exponentially while the decay is polynomial -
**a stronger statement than section 5.4 makes.**
Reproduce: scripts/step86_m1_growth.py, step87_m1_trend.py, step88_m1_verdict.py.
Data: runs/m1_growth.json, runs/m1_trend.json, runs/m1_verdict.json

## 1. The measurement

Structures sampled **uniformly from the space at each n** - not from a mixed ensemble, which is what
Findings 023 to 025 did and which cannot answer this question, because a fraction of a mixed
ensemble is not a fraction of the space at a given n. 1000 structures per size, n = 3 to 12.

    tau_slow = 6.409459e+03      calibrated at n = 3 to cover one half, then HELD FIXED
    tau_fast = 1.203405e+05

| n | C1 modal | C3 slow | C4 fast | binomial se |
|---|---|---|---|---|
| 3 | **1.0000** | 0.5000 | 0.5000 | 0.0158 |
| 4 | **0.0000** | 0.5760 | 0.3350 | 0.0149 |
| 6 | 0.0000 | 0.6000 | 0.1940 | 0.0125 |
| 8 | 0.0000 | 0.6160 | 0.0990 | 0.0094 |
| 10 | 0.0000 | 0.6430 | 0.0420 | 0.0063 |
| 12 | 0.0000 | **0.6370** | **0.0270** | 0.0051 |

    fitted exponent of coverage against n:  C1 -12.287   C3 +0.145   C4 -2.133

## 2. The verdict, computed from those numbers

| certificate | alpha | coverage n=3 -> n=12 | g(N) |
|---|---|---|---|
| **C1 modal** | -12.287 | 1.0000 -> **0.0000** | **BOUNDED** - section 5.4 row 1 |
| **C3 slow** | **+0.145** | 0.5000 -> 0.6370 | **-> infinity** |
| **C4 fast** | **-2.133** | 0.5000 -> 0.0270 | **-> infinity** |

**M1's falsifier is triggered for 1 of 3 members.**

## 3. The three answers, and they are three different things

**C1 modal is bounded in the strongest possible way.** Its coverage is not slowly decaying; it is
**exactly zero for every n >= 4**, because a requirement of 4 harmonics cannot be violated by a
structure that has 4 or more modes. g(N) = Theta(1). **Finding 050's row 1 stands unchanged**, and
this is the cleanest possible instance of a certificate that is cheap, sound, class-level, tagged -
and covers nothing.

**C3 slow is the member section 5.4 needs.** The Rayleigh bound omega_1^2 <= sum k_ground / sum m
covers 0.500 at n = 3 and 0.637 at n = 12, with no downward trend, across a range where the space
grows by twelve orders of magnitude. **g(N) = Theta(N(n)) -> infinity**, and the library condition -
each cut covering a constant fraction of what remains - has a scale-free invariant to stand on.

**C4 fast is the surprise.** Its coverage genuinely decays, as n**-2.13. **And g(N) still diverges**,
because N(n) = c(n)(2**n - 1) grows super-exponentially in n while the decay is polynomial.

    constant coverage  =>  g(N) -> infinity          section 5.4's condition, SUFFICIENT
    n**-2.13 coverage  =>  g(N) -> infinity          and NOT NECESSARY

**That is a stronger statement than the roadmap makes.** Section 5.4's library argument asks for a
constant fraction per step; what actually matters is that the coverage decay slower than the space
grows, and **almost any polynomial decay qualifies**. The design criterion softens accordingly:
a candidate invariant does not have to be scale-free, only not exponentially shrinking.

## 4. Two imprecisions of mine, recorded

**Step 86 decided survival with the arbitrary threshold "coverage > 0.05 at every n".** C4's
coverage came out 0.50, 0.35, 0.24, 0.18, 0.085, 0.0875 - **a decay** - and it passed because the
last point happened to sit above 0.05. A constant and a decay are told apart by an exponent, not a
threshold. **Instance nine.**

**Step 87 then printed, in its else branch, that C3's coverage "decays too, at alpha = +0.145".**
A positive exponent is not a decay. **Instance ten** - and both nine and ten came from a decision
rule I wrote after seeing the trend rather than from the data.

**And step 88 called alpha = +0.145 with a standard error of 0.0114 "indistinguishable from zero".**
It is 12.7 standard errors from zero: the coverage **rises slightly**. **The conclusion is
unaffected** - a positive exponent is bounded below by its n = 3 value either way - but the phrase
is wrong, and it is the same error in miniature: a qualitative word attached to a number that does
not support it.

## 5. What this closes and what it opens

**Closes**: M1. A certificate exists that is sound, cheap, class-level, carries a domain tag, and
has g(N) -> infinity. **It is C3, and it is not the one the project started with.**

**Opens a design rule that is easier to satisfy than the roadmap assumed**: a candidate invariant
no longer has to be scale-free. **The question becomes the exponent**, and a polynomial decay of any
order leaves the crossing intact because the space grows faster than any polynomial.

**Leaves standing**: Finding 050's classification of C1, and the observation that the cheapest
certificate is the one that covers nothing. **C3 is not free** - it sums ground stiffnesses and
masses - and it is the one that carries the growth. **The tension Finding 051 noticed in the timing
is real: the member doing the work is not the member that costs nothing.**

## 6. Limits

  * **Coverage is still a property of the (invariant, ensemble, requirement) triple** (Finding 012).
    These are 1000 samples per size from one generator, one tau calibration, one requirement.
  * **n <= 12.** The exponents are fitted over ten points; a turnover beyond n = 12 is not excluded.
  * **The structures are sampled uniformly in graph structure, not in physical plausibility.** A
    real design space is not a uniform graph ensemble, and Finding 012's caveat applies in full.
  * **C1, C3, C4 only.** The energy/passivity and band-tradeoff invariants of section 6 Layer B are
    not implemented and are not measured here.
  * **tau was calibrated once**, at n = 3 to cover one half. A different calibration changes the
    levels; whether it changes the exponents was not tested.
