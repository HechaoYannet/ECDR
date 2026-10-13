# Finding 050 - The cost axis exists, and it classifies C1 as decoration

Status: Layer C's one cost axis is built and measured, with all three routes charged in seconds on
the real code paths. **The project's oldest certificate, modal counting, lands in section 5.4's row
1: "no crossing ever; decoration".** And the formal crossing condition reports a crossing for it
anyway, by a factor of 4200.7, which is why condition 1 must not be used alone.
Reproduce: scripts/step74_two_routes.py.  Data: runs/two_routes.json

## 1. What was missing, and is now there

Finding 049 recorded that the harness had a flat counter of "physics calls" and a single route, so
it could not express the comparison Layer C requires - proved and unproved regions "both living on
one cost axis" (lines 368 to 370). Three routes are now charged in **seconds**, measured:

| route | cost | what it concludes |
|---|---|---|
| **B** certificate | c_p + c_v, paid once | CERTAINLY, over g(N) structures |
| **C** enumeration | g(N) * c_s | the same set, by evaluation |
| **A** sampling | M * c_s, M = Theta(1/delta) | "not found yet", confidence 1/(M+1) |

Measured constants:

    c_s  one structure evaluation      1.044866e-03 s
    c_v  one certificate check         5.348900e-08 s     (c_v / c_s = 5.1e-05)
    c_p  deriving the certificate      9.414500e-07 s

**A check is four orders of magnitude cheaper than an evaluation**, and that fact turns out to be
the source of a trap.

## 2. C1 on the axis

C1 is the modal certificate: a structure with fewer than m modes cannot produce m harmonics. With
mode_count() returning n, it rules out all structures with fewer than m masses.

| n | N(n) | g/N | B cert (s) | C enum (s) | C/B | A sampling (s) |
|---|---|---|---|---|---|---|
| 3 | 3.2e+01 | 1.250e-01 | 9.949e-07 | 4.180e-03 | 4200.7 | 1.045e-01 |
| 5 | 2.317e+04 | 1.726e-04 | 9.949e-07 | 4.180e-03 | 4200.7 | 1.045e-01 |
| 8 | 6.438e+10 | 6.213e-11 | 9.949e-07 | 4.180e-03 | 4200.7 | 1.045e-01 |
| 10 | 3.532e+16 | **1.132e-16** | 9.949e-07 | 4.180e-03 | **4200.7** | 1.045e-01 |

**g is 4. A constant.** It does not depend on N at all, because "fewer than 3 masses" is a fixed
set regardless of how large the family gets.

**The ratio C/B is 4200.7 at every scale.** The certificate is 4200 times cheaper than enumerating
what it covers, and **that advantage never improves**, because both sides of the comparison are
constants. The fraction covered falls from 1.25e-01 to 1.13e-16.

**Section 5.4's table, line 192, on Theta(1): "absolute saving bounded, relative saving -> 1,
verdict: no crossing ever; decoration."** C1 is in that row, and this is the first time it has been
put there by measurement rather than by reading.

## 3. The trap: condition 1 reports a crossing for a decoration

The crossing condition of section 5.3 is

    g(N)  >  (c_p + c_v) / c_s   =  9.5222e-04

and **g = 4 clears it by a factor of 4200.7.**

**So the formal condition declares a crossing, and section 5.4 classifies the same certificate as
decoration.** Both are correct. Condition 1 asks only whether certification is cheaper than
evaluating the covered set - and since a check costs 5.1e-05 of an evaluation, **almost any
predicate clears it, including one that covers four structures out of 3.5e+16.**

**The informative quantity is condition 2** - whether g(N) is Theta(N), so the advantage persists.
C1 fails it outright.

**Had the harness reported "a crossing exists" from the measured constants - which is exactly what
building the cost axis invites - it would have reported a true inequality that means nothing.**
This is the same class of error as Finding 025's vacuous empty regime and Finding 036's
empty-versus-failing confusion, one level up: **a condition satisfied by construction rather than
by content.**

## 4. The library survives, and has not been measured this way

Section 5.4, lines 175 to 188, already supersedes condition 2 with the **library** result of Finding
011: k = O(log N / log(1/(1-f))) certificates, growing additively per decade of N while sampling
grows multiplicatively.

**And the library's members satisfy condition 2 where C1 does not.** Findings 023 to 025 measured
per-step coverage of roughly 0.42 to 0.79 - **a constant fraction of what remains**, which for the
first certificate is g(N) = Theta(N).

**So the honest reading is not that the project has nothing. It is that the project has two
certificates in different rows of the same table, and until now neither had been placed there by
measurement.** C1 is decoration. The four-certificate library is the candidate, and **it has not
had the three-route treatment.**

## 5. What sampling costs, and what it buys

Route A costs **1.045e-01 s at every n**, confirming Proposition 3: M = Theta(1/delta) independent
of N, with delta = 0.01 and M = 100. It does not grow with the space.

**And it certifies nothing.** At 100 draws with no success the conclusion is still "not found yet",
which is consistent both with "no such structure exists" and with "one exists and I did not draw
it". That is Proposition 1, and it is why section 5.2 reframes the choice as "certificate versus
nothing".

**So on this problem the certificate is 105,018 times cheaper than sampling and rules out a set of
size 4.** Both numbers are true. **A speedup is not evidence of value; the roadmap's own table says
so, and this is the measurement that shows the table working.**

## 6. Limits

  * **One certificate, one requirement (m = 3), one ensemble family.** C1 with a larger m covers
    more, but g remains a constant in N, so the row does not change.
  * **c_p is the machine cost of computing the family's size, not the cost of a human deriving the
    theorem.** The derivation of C1 is a one-line argument and its true c_p is near zero, which
    makes the certificate look better still - and does not move it out of row 1, because row 1 is
    decided by g(N), not by cost.
  * **Wall-clock on one machine is not a portable cost unit.** The ratios are what matter and they
    are robust, since c_s and c_v differ by four orders.
  * The three routes are not alternatives for the same question: A answers a probabilistic question
    and B and C answer a certain one. **Section 5.5 says that is the whole point**, and the
    comparison is only meaningful once the required kind of conclusion is fixed.
  * **The library of Findings 023 to 025 has not been put on this axis.** That is the next
    measurement and it is the one that could show a persistent crossing.
