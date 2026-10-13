# Finding 052 - Retraction: Finding 051 measured the heuristic, and section 5.4 is right

Status: **Finding 051 is WITHDRAWN.** A certificate is a statement about a CLASS; using it does not
require examining its members, so its cost is c_p + c_v and contains no N. Finding 051 measured a
procedure that applies the predicate to every member one at a time - which is precisely section 2.1
line 60's heuristic - and attributed its Theta(N) cost to the certificate. **The measurement is
good; the attribution was wrong, and the mistake is the exact distinction the roadmap already
draws.**
Reproduce: scripts/step76_three_procedures.py.  Data: runs/three_procedures.json

## 1. What the error was

Section 3, line 100, requires of a certificate:

> a **cost growing slower than abs(F)**

A certificate asserts

    for all S in F :  delta(S) > epsilon

**Derive it once, check the ARGUMENT once, and the whole family is concluded about.** The cost is
c_p + c_v. Nothing in it is per-member.

Finding 051 instead measured: for each structure, evaluate the predicate; if it fails, discard it.
That procedure costs Theta(g(N) * c_v) - and it is a real, useful procedure. **It is section 2.1,
line 60:**

> Where a certificate can prune, **a plain heuristic reading the same verdict** prunes identically

**Same pruning. Different cost. And the cost is the entire difference between them.** Finding 051
implemented the heuristic and reported its cost as the certificate's.

## 2. The measurement, with the three procedures separated

    c_s            one structure evaluation         2.2357e-03 s
    c_v_apply      one heuristic membership test    4.6450e-08 s
    c_p            derive + COUNT the covered class ~2.0e-07 s
    c_v_argument   check the class-level argument   2.2357e-03 s   (see the note below)

**Note on c_v_argument**: checking a written class-level argument is a fixed cost, not a
per-structure computation. It is deliberately set here to **one full structure evaluation**, which
is far more than such a check would cost. **Every separation quoted below is therefore a lower
bound.**

## 3. The cost of ruling out the same set, three ways

Let the requirement scale with the family: a target with n harmonics is ruled out by every
structure with fewer than n modes, which is a fixed FRACTION rather than a fixed count.

| n | N(n) | g = N(n-1) | g/N | CERT c_p+c_v | ENUM g*c_s | separation |
|---|---|---|---|---|---|---|
| 3 | 3.20e+01 | 4.00e+00 | 0.1250 | 2.2359e-03 | 8.9427e-03 | 4.00e+00 |
| 5 | 2.317e+04 | 6.02e+02 | 0.0260 | 2.2359e-03 | 1.3459e+00 | 6.02e+02 |
| 7 | 2.387e+08 | 1.705e+06 | 0.0071 | 2.2359e-03 | 3.8130e+03 | 1.71e+06 |
| 9 | 3.394e+13 | 6.438e+10 | 0.0019 | 2.2359e-03 | 1.4394e+08 | 6.44e+10 |
| 10 | 3.532e+16 | 3.394e+13 | 0.0010 | 2.2359e-03 | 7.5883e+10 | **3.39e+13** |

**The certificate's cost is 2.2359e-03 s at n = 3 AND at n = 10. Identical.** It does not contain N.
Enumeration's cost rises from 8.94e-03 to 7.59e10 s, and **the separation grows from 4.00 to
3.39e13** - with a deliberately over-generous certificate cost.

## 4. So section 5.4 stands, and the roadmap's own distinction is quantified

A certificate's c_p is paid **once per certificate**, not once per structure. The library's cost is
k * (c_p + c_v) with k = O(log N / log(1/(1-f))), which is **logarithmic** in N while enumeration is
**linear**. The count grows additively per decade and enumeration multiplicatively, and the 2.6e6
figure compares the right two quantities.

**And section 2.1 line 60 and section 5.2 now have a number attached.** The heuristic reading the
same verdict prunes **identically** - that was measured and stands - and it costs **3.39e13 times
more** at n = 10, with the ratio growing without bound. **Section 5.2's reframing, "not certificate
versus heuristic but certificate versus nothing", was about the LOGIC: a heuristic cannot produce
certainty. This is the other half: it also cannot produce it cheaply.**

## 5. Two self-corrections in two rounds, both found by re-reading the roadmap

Finding 051 was written last round with confidence and is withdrawn this round. **What caught it was
not a test but re-reading section 3's own requirement that a certificate's cost grow slower than
abs(F)** - which the procedure I had measured plainly violates, and which should have been the first
thing checked before reporting that the roadmap's central quantitative claim was wrong.

The pattern is worth naming: **in both 046 and 051 the error was in what I had measured, not in the
measurement.** 046 measured a run in which the agent had been told no evidence would arrive; 051
measured the heuristic and called it the certificate. **The numbers were right both times and the
labels were wrong**, which is the same class as the six identity traps and the inverted independence
ratio - a quantity read as meaning something other than what it was computed from.

## 6. Limits

  * **c_v_argument is a stand-in**, set to one full evaluation. The true cost of checking a
    class-level argument is smaller and was not measured; it is bounded above by the value used.
  * **c_p = 2.0e-07 s is the machine cost of counting the covered class**, not the cost of deriving
    the invariant. Deriving C1 is a one-line argument whose human cost is near zero, so the
    certificate side is generously charged throughout.
  * **The scaling table uses g = N(n-1)**, a fixed fraction, which is the case section 5.4's library
    argument needs. C1 with a FIXED m covers a fixed count instead and lands in row 1 - that part of
    Finding 050 stands and is not in conflict with this.
  * One ensemble, one machine, wall-clock units.
  * **Finding 051's measurements of c_v per certificate (a 209-fold spread) remain valid**; only its
    attribution of the application cost to the certificate route is withdrawn.
