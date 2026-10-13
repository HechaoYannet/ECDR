# Finding 037 - The minimum-units bound is refuted before it was used

**SUPERSEDED BY FINDING 044.** The refutation is redone on a corrected model: the fewest units
attaining Q_H_min is **3**, not 2, against N - 1 = 4. The conclusion holds - and the argument is
now clean, since a connected graph on 5 nodes needs 4 edges, so any 3-unit design is
disconnected. The witness used below (2 units) was fictitious. Read 044.

**INVALIDATED BY FINDING 043.** The networks this finding used to refute U >= N - 1 attained
the optimum only because network_lp let pool heat reach a cold stream that no unit touched.
With that barred, the 2-unit network needs 150 kW where the LP reported 142.5, so it is not a
counterexample and the bound has NOT been refuted. The text below is kept as the record of the
error; the question is open again.

Status: the candidate second certificate for the heat-exchanger domain is **not sound**. It was
refuted by exhaustive enumeration in all three cases, in the same round it was proposed.
Reproduce: scripts/step67_heat_min_units.py.  Data: runs/heat_min_units.json

## 1. The candidate

The classical result for heat exchanger networks is

    U_min = N - 1

with N the number of streams including the utilities used. It is the combinatorial analogue of
the modal-dimension certificate - a counting statement about the network graph rather than a
statement about temperatures - and it is the obvious second certificate for this domain.

The soundness argument would be: a unit connects two streams, so the network is a graph with N
stream-nodes and U unit-edges, and a connected graph on N nodes needs at least N - 1 edges.
**But that argument requires connectivity, and connectivity is not automatic.**

## 2. The refutation

Every match set was enumerated with its unit count and its minimum utility:

| case | streams | utilities | N | N - 1 | fewest units attaining Q_H_min | verdict |
|---|---|---|---|---|---|---|
| 4-stream | 4 | 1 | 5 | 4 | **2** | **REFUTED** |
| 2x2 | 4 | 1 | 5 | 4 | **3** | **REFUTED** |
| 3x2 | 5 | 0 | 5 | 4 | **3** | **REFUTED** |

with the full picture by unit count:

| case | 1 unit | 2 units | 3 units | 4 units |
|---|---|---|---|---|
| 4-stream | 157.5 | **142.5** | **142.5** | **142.5** |
| 2x2 | 200.0 | 100.0 | **60.0** | **60.0** |
| 3x2 | 135.0 | 20.0 | **0.0** | **0.0** |

(bold = attains the certificate).

In the 4-stream case a network with **two** units attains the minimum utility. Five nodes and
two edges is a graph with at least three components - **disconnected**, and each component
needs only its own spanning tree. So the bound fails for exactly the reason the connectivity
caveat predicted.

## 3. What this means

**U_min = N - 1 is an ACHIEVABILITY result, not a lower bound.** It says a minimum-utility
design with no loops can be built using N - 1 units; it does not say no design uses fewer.
The classical statement is about the optimal design, and reading it as a certificate over all
networks is a category error.

**Stating it as a certificate would have been an unsound claim of precisely the kind this
project is built to avoid** - a rule-out that rules out nothing, carrying an authority it had
not earned. The refutation cost one script and reused an enumeration that already existed.

This is the first time the project has refuted its own candidate certificate, and it is worth
noting that it happened in the SECOND domain, on the first candidate that domain suggested.
The vibration certificates survived because they were tested; this one did not, and the
difference was the test, not the care taken in proposing it.

## 4. What a sound replacement looks like

The argument that does go through uses the pinch, not connectivity:

  * Above the pinch, **no cold utility may be used** - using it would raise both utilities. So
    every hot stream present above the pinch must have its heat there absorbed by a cold
    stream, which requires at least one unit **above the pinch** touching it. Each unit touches
    at most one hot stream, so U_above >= N_h_above; symmetrically U_above >= N_c_above.
  * The same below the pinch, where no hot utility may be used.
  * Hence **U >= max(N_h_above, N_c_above, N_h_below, N_c_below)** over the whole network,
    since every unit above the pinch is also a unit of the network.

This is a counting argument over the pinch decomposition - the same character as modal
counting, cheap and independent of the network family - and it does **not** assume
connectivity. Whether it is tight, and whether it is refuted as the previous candidate was,
is untested and is the next thing to check.

## 5. Limits

  * Three stream sets, one dt_min each, 4 to 5 streams. A refutation needs only one
    counterexample per case, and there are three, so the negative result is secure; but the
    positive properties of any replacement are not.
  * The network space enumerated is match SETS. A unit here is a match between one hot and one
    cold stream; units with stream splitting or multiple shells are outside the model.
  * The unit count is the number of matches, which equals the number of physical exchangers
    only if no match needs more than one shell.
