# Finding 053 - Proposition 4: a heuristic is not the alternative to a certificate

Status: the roadmap's section 2.1 line 60 ("prunes identically") and section 5.2 ("certificate versus
nothing") are now one proposition with a proof and a measurement. **The answer to "certificate
versus heuristic" is that they do not differ IN SCALING at all** - a heuristic scales exactly as
enumeration does. Only the certificate's cost lacks g(N).
Reproduce: scripts/step77_proposition4.py.  Data: runs/proposition4.json
Written into: docs/ROADMAP.md section 5.3, and the section 5.6 status table.

## 1. The proposition

Let P be a predicate on a family F with abs(F) = N, and let a certificate establish P = 0 on a
subfamily C with abs(C) = g(N). Then

  1. **the certificate, a heuristic reading the same verdict, and enumeration exclude exactly C**;
  2. their costs are

         certificate   c_p + c_v             contains no N
         heuristic     g(N) * c_v_apply      Theta(g(N))
         enumeration   g(N) * c_s            Theta(g(N))

  3. so the certificate's advantage over BOTH is Theta(g(N)) and unbounded, while the heuristic's
     advantage over enumeration is the **constant** c_s / c_v_apply and nothing more.

*Proof.* (1) is immediate: all three apply the same predicate. (2) is what each procedure is. (3) by
division. **The only quantity in the three costs that can contain g(N) is g(N) itself, and it
appears in exactly two of them.**

**Consequence.** A heuristic is enumeration with a better constant, so it inherits Proposition 1:
no constant rescues a procedure that must examine every member. **That is why section 5.2's choice
is "certificate versus nothing"** - the two alternatives differ from each other by a constant and
from the certificate in kind.

## 2. The measurement

    c_s            2.1528e-03 s      c_v_apply   4.878e-08 s      c_s/c_v_apply = 44155
    c_p + c_v      2.1528e-03 s      (argument check charged one FULL evaluation - generous)

**Part 1, the pruning.** On 400 random structures the certificate covers 62, the heuristic excludes
62, enumeration excludes 62, and the three sets are equal. Identical, as the proposition says.

**Part 2, the costs.**

| n | g = N(n-1) | certificate | heuristic | enumeration | cert/enum |
|---|---|---|---|---|---|
| 3 | 4.00e+00 | 2.1528e-03 | 1.950e-07 | 8.610e-03 | 4.000e+00 |
| 5 | 6.02e+02 | 2.1528e-03 | 2.935e-05 | 1.296e+00 | 6.019e+02 |
| 7 | 1.706e+06 | 2.1528e-03 | 8.314e-02 | 3.671e+03 | 1.705e+06 |
| 10 | 3.394e+13 | 2.1528e-03 | 1.655e+06 | 7.306e+10 | **3.394e+13** |

**The certificate's cost is identical at n = 3 and n = 10.** The formula
g(N) * c_s / (c_p + c_v) reproduces the measured separation **exactly on all eight sizes**, and the
ratio cert/heuristic over cert/enumeration is exactly c_v_apply / c_s at every size, which is the
proposition's part 3.

## 3. What this settles

**"Certificate versus heuristic" is not a difference in scaling between those two.** A heuristic
scales exactly as enumeration does. It is a **constant** between a heuristic and enumeration, and a
**difference in kind** between either of them and a certificate.

**That is the precise content of section 2.1 line 60**, which recorded only that the pruning is
identical, and it closes the question raised about heuristics directly. Section 5.2's answer - that
a heuristic cannot produce certainty - is about the logic; this is the other half, that it cannot
produce it cheaply either.

## 4. Why this proposition is worth having

It is the one statement in the project that makes **"a certificate is not a faster search but a
different kind of thing"** falsifiable. If a procedure existed that read the same verdict, pruned
identically, and cost **independent of g(N)** without being a class-level argument, part 3 would
fail. No such procedure is known, and the proof says why: any procedure that examines members has
g(N) in its cost.

**And it is measured rather than merely proved**: the certificate cost being identical at n = 3 and
n = 10 is the observable content of "contains no N".

## 5. Limits

  * **c_v_argument is charged one full evaluation**, far above the true cost of checking a
    class-level argument. Every separation is a lower bound.
  * **c_p is the machine cost of counting the covered class**, not the human cost of deriving the
    invariant, which is near zero for C1. The certificate side is generously charged throughout.
  * **The scaling table uses g = N(n-1)**, a fixed fraction, which is the case section 5.4's library
    argument needs. C1 with a FIXED m covers a fixed count - Finding 050's row 1 - and Proposition 4
    is about the cost relationship, not about which row a given certificate sits in.
  * **One predicate, one ensemble, one machine.** The proof is general; the numbers are not.
  * The proposition says nothing about whether a certificate is USEFUL. A certificate that is cheap
    and covers a vanishing fraction is still decoration, which is Finding 050 and is a separate
    question from this one.
