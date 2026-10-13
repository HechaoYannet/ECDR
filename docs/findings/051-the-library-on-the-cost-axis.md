# Finding 051 - The library on the cost axis: c_v is four numbers, and the separation is a constant

Status: the four-certificate library is **360 times cheaper than evaluating the same structures**,
measured. But **both routes are Theta(N)**, so that advantage is a **constant factor and does not
grow with N**. Section 5.4's headline separation of 2.6e6 comes from comparing the certificate
COUNT against N, which under-counts the certificate side by the whole application cost.
Reproduce: scripts/step75_library_cost.py.  Data: runs/library_cost.json

## 1. c_v is not one number

Section 5.3 writes the certificate route as c_p + c_v, as if one certificate were another. Measured
on the real code paths, over 400 structures:

| certificate | c_v per structure | c_v / c_s | what the check does |
|---|---|---|---|
| modal | 4.575e-08 | 0.000021 | reads an integer attribute |
| **statics** | **8.039e-06** | **0.003699** | builds K and solves K x = m g |
| slow | 4.538e-07 | 0.000209 | sums ground stiffnesses and masses |
| **fast** | **9.581e-06** | **0.004408** | builds K and takes row sums |

    c_s, one full transmissibility evaluation : 2.173e-03 s

**The four check costs span a factor of 209.4.** One of them is free because the mode count is an
attribute that already exists; the other three recompute something from the matrices.

## 2. The library charged sequentially, as it is actually applied

Each certificate is applied only to the survivors of the ones before it:

| step | applied to | cut | cost (s) | cumulative |
|---|---|---|---|---|
| modal | 400 | 199 | 5.580e-05 | 5.580e-05 |
| **statics** | **201** | 115 | **2.038e-03** | 2.094e-03 |
| slow | 86 | 48 | 7.338e-05 | 2.167e-03 |
| fast | 18 | 12 | 2.457e-04 | **2.413e-03** |

survivors 6 of 400, fraction 0.0150.

**The dearest check is applied to the most structures and dominates: statics alone is 84 percent of
the total.** A single averaged c_v cannot express this.

## 3. The advantage is real and constant

    library, sequential, 400 structures : 2.413e-03 s
    the same 400 by full evaluation     : 8.694e-01 s
    ratio                               : 0.002776   (360.3 times cheaper)

**That is a genuine, measured, persistent advantage.** And it is a **constant**: both routes are
linear in N, so

    library cost  =  Theta(N * c_v1 / f)        measured constant 6.03e-06 s per structure
    enumeration   =  Theta(N * c_s)             measured constant 2.173e-03 s per structure

and the ratio between them does not depend on N at all.

## 4. Which corrects section 5.4's headline number

Line 183 to 185:

> the count grows ADDITIVELY per decade of N while sampling grows MULTIPLICATIVELY. At N = 6.4e10, a
> per-step coverage of one part in a thousand gives k = 24,876 certificates against 6.4e10
> evaluations: **a separation of 2.6e6**.

**The comparison is k against N, and it charges one certificate as one unit.** But applying a
certificate is not one unit: it is one check **per surviving structure**, and the first certificate
must be applied to all N of them.

    certificate count k        = Theta( log N / log(1/(1-f)) )     additive per decade  CORRECT
    certificate APPLICATION    = Theta( N * c_v1 / f )             linear in N          OMITTED
    enumeration                = Theta( N * c_s )                  linear in N

**So the separation is not 2.6e6 and does not grow. It is the constant**

    c_v1 / (f * c_s)   =   0.003699 / 0.65   ~=  1/176      (measured overall: 1/360)

**The distinction section 5.4 draws - additive against multiplicative - is a property of the
certificate COUNT, which governs c_p, and c_p is paid once per certificate rather than once per
structure.** The per-structure cost of both routes is linear in N.

**Stated correctly**: a library buys a constant speedup of order c_s / (f * c_v), and nothing more.
That is still worth having - 360 times is 360 times - but it is a different claim from a separation
that grows without bound.

## 5. And a structural tension the numbers expose

**The cheap check is the decoration and the expensive checks do the work.**

Finding 050 measured the modal certificate - the free one, c_v = 4.6e-08 - as having g(N) = Theta(1)
and classified it as decoration. **The three that actually cut a constant fraction of what remains
cost 100 to 200 times more to check.**

So cost and coverage pull in opposite directions across this library, and the composition is
dominated by the first certificate that both costs something and cuts a lot. **Any claim about a
library's cost has to name which member is doing the cutting.**

## 6. Limits

  * **One ensemble, one calibration, four certificates.** The measured constants will move with the
    ensemble, and Finding 012 established that coverage is a property of the (invariant, ensemble,
    requirement) triple.
  * **f is not one number either.** The four cuts differ (199/400, 115/201, 48/86, 12/18); the
    scalar f in the formula is an average and the sequential sum is what was measured.
  * **Wall-clock on one machine.** The ratios are robust where the costs differ by orders of
    magnitude, but c_v1/(f*c_s) would move on a machine with a different linear-algebra path.
  * **The comparison is application against enumeration, both certain.** Sampling is a third route
    answering a probabilistic question, measured separately in Finding 050, and section 5.5 says
    the regime decides which is correct.
  * **This measures cost, not value.** A 360-times speedup on a region the requirement does not care
    about is still worthless, which is Finding 050's lesson about condition 1.
