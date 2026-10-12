# Finding 019 - The split that matters is TOPOLOGY vs VALUE

Status: Finding 015's "structural vs performance" reading was a coincidence of which cuts
happened to be topology-derived. The real dividing line is whether a cut is keyed to the
topology or to the component values. **Both candidate certificates are value-derived and
will not compose.**
Reproduce: scripts/step40_certificate_independence.py, step41_topology_vs_value.py
Data: runs/certificate_independence.json, runs/topology_vs_value.json

## 1. The measurement that started this

Finding 014 produced a law keyed to the payload's own ground tie, and Finding 018 a
band-tradeoff law keyed to the right-half-plane zeros. Both are structural, so by Finding
015 they should have composed. They do not:

| | payload-tie law (g0/m0) vs waterbed law (W) |
|---|---|
| independence ratio | **0.6066** |
| Spearman rho | **-0.4976** (p = 6.6e-14) |

By Finding 015's own rule - a pair near 0.4 is one certificate wearing two hats - these
are one certificate wearing two hats. That falsifies the reading of Finding 015, since
both quantities are structural.

## 2. The replacement hypothesis, and the test

    TOPOLOGY cuts   are drawn INDEPENDENTLY of the component values
    VALUE cuts      are all functions of the SAME drawn component values

so value cuts share a common factor by construction, whatever they are called. Ratio
matrix over both families together, median splits, 200 networks:

| | VAL g0/m0 | VAL W | VAL sag | VAL in-band | TOP grounded | TOP >=2 ties | TOP deg>=3 | TOP n>=6 |
|---|---|---|---|---|---|---|---|---|
| VAL g0/m0 | - | 0.607 | 0.705 | 1.213 | 1.639 | 1.244 | 1.022 | 0.989 |
| VAL W | 0.607 | - | 1.360 | 0.740 | 0.607 | 1.034 | 0.945 | 1.207 |
| VAL sag | 0.705 | 1.360 | - | 0.340 | 0.705 | 0.897 | 0.904 | 1.017 |
| VAL in-band | 1.213 | 0.740 | 0.340 | - | 1.213 | 1.172 | 1.096 | 1.069 |
| TOP grounded | 1.639 | 0.607 | 0.705 | 1.213 | - | 1.244 | 1.022 | 0.989 |
| TOP >=2 ties | 1.244 | 1.034 | 0.897 | 1.172 | 1.244 | - | 1.118 | 1.268 |
| TOP deg>=3 | 1.022 | 0.945 | 0.904 | 1.096 | 1.022 | 1.118 | - | 1.157 |
| TOP n>=6 | 0.989 | 1.207 | 1.017 | 1.069 | 0.989 | 1.268 | 1.157 | - |

| family | mean ratio |
|---|---|
| value-value | **0.8274** |
| topology-topology | **1.1330** |
| cross | 1.0475 |

## 3. It reproduces both earlier results, from different cuts

| measurement | mean ratio |
|---|---|
| Finding 013, performance-performance | 0.8210 |
| **this round, value-value** | **0.8274** |
| Finding 015, structural-structural | 1.1110 |
| **this round, topology-topology** | **1.1330** |

The value-value mean lands on Finding 013's number and the topology-topology mean lands on
Finding 015's, **even though the cut lists are different**. Finding 015's structural cuts
were payload-grounded, ground-tie count, degree and node count - all topology. Finding
013's performance cuts were sag, peak and in-band - all values. So Finding 015 was
measuring topology against value and calling it structure against performance.

## 4. The design principle

> **A cut composes only if it is keyed to a part of the structure that varies
> independently of the parts the other cuts are keyed to.**

In this ensemble that means: key certificates to TOPOLOGY, not to component values.

**And this is exactly the draft's notion of structural capability.** The draft's design
object is S = (component inventory, connection topology, boundary relations) with theta in
Theta(S) the continuous parameters, and a capability gap is delta(S) > epsilon - a
statement about the STRUCTURE, holding for all theta. A certificate keyed to topology is a
statement that holds regardless of the parameters, which is precisely a capability gap in
the draft's sense.

So three things that looked separate turn out to be the same thing:

    the draft's structural capability  ==  topology-keyed certificates  ==  the cuts that compose

That is a stronger convergence than any of the individual findings, and it was not designed.

## 5. The consequence, which is unwelcome

**Both candidate certificates are value-derived.**

| certificate | keyed to | composes with the other? |
|---|---|---|
| Finding 014, payload ground-damping law | g0/m0, a VALUE | **no** (0.607) |
| Finding 018, waterbed | RHP zeros of P, which move with the VALUES | **no** (0.607) |

Neither is usable as the second member of a composing library alongside the other. The
search has to move to topology-keyed bounds.

## 6. The critical-path question, now sharp

> **Is there a sound bound keyed to topology alone, with growing coverage?**

Both halves are hard and they pull against each other:

  * **sound** - a topology-only statement must hold for EVERY parameter assignment
    compatible with that topology, which is a much stronger claim than a bound that may
    depend on the values;
  * **growing coverage** - Finding 010 eliminated mode counting, which IS topology-keyed
    and sound, precisely because its g(N) is constant (32 for every space size).

Mode counting is the cautionary case: sound, topology-keyed, and useless for the crossing.
So the requirement is not "find a topology-keyed bound" but "find one that is also
scale-free". That is the open problem.

## 7. Honest limits

  * The result is **partly by construction**. The ensemble draws topology first and
    component values afterwards, independently, so topology cuts are independent and value
    cuts are not, by the generative design. What is not by construction is the MAGNITUDE
    (0.83 against 1.13), its stability across three seeds in Findings 013 and 015, and the
    fact that two independently chosen cut lists reproduce the same two numbers.
  * One ensemble family: random trees with log-uniform component values, one band edge, one
    calibration. Whether real engineering structures have the same topology-value
    independence is untested and is a question for the M6 domain.
  * Median splits were used throughout, so all comparisons are at matched 50 percent
    marginals; the ratios would shift at other thresholds.
  * Finding 013's independence ratio at its own calibration was 0.437 for one pair; the
    0.82 quoted here is the family mean, and the two are consistent.
