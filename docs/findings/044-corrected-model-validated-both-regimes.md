# Finding 044 - The corrected model, validated in both regimes, refutes U >= N - 1 by 3 units

**INVALIDATED BY FINDING 055.** The refutation below compares a MATCHES-ONLY count against
U >= N - 1, whose N includes the utilities and whose units include the utility exchangers. The two
sides count different things, and the connectivity argument is sound graph theory applied to a
graph that is missing two nodes.

Status: `network_lp` is corrected and validated where it previously failed. Finding 036 stands
untouched. **The minimum-units bound is refuted again - but by 3 units, not 2 - and the
argument is now clean.** The agent's hand-computed floor of 150.0 is reproduced exactly.
Reproduce: scripts/step70_network_model_validated.py.  Data: runs/network_model_validated.json

## 1. The correction

Heat released by hot stream i at shifted level k may be absorbed by cold stream j at shifted
level k' whenever

    (i, j) is a match   and   k <= k'

because shifted temperatures already carry the half-pinch shift, so k <= k' is exactly
T_hot - T_cold >= dt_min. Transfer is therefore indexed by the **pair** of levels:

    x[i,j,k,k']     heat from hot i at level k to cold j at level k'
    (hot)  sum_{j, k' >= k} x[i,j,k,k'] + qC[i,k] = QH[i,k]
    (cold) sum_{i, k <= k'} x[i,j,k,k'] + qH[j,k'] = QC[j,k']

The free pool is gone. **Every kilowatt that reaches a cold stream arrives through a unit that
touches it**, which is the property the old model lacked and the agent detected.

## 2. Validated in BOTH regimes - which is the point

| case | problem table | network_lp | difference |
|---|---|---|---|
| 4-stream | 142.50000000 | 142.50000000 | **0.00e+00** |
| 2x2 | 60.00000000 | 60.00000000 | **0.00e+00** |
| 3x2 | 0.00000000 | 0.00000000 | **0.00e+00** |

**Finding 036 is unaffected**, and the reason is now explicit rather than lucky: with every match
allowed, every cold stream has a match, so the pool restriction that was missing is vacuous. The
correction leaves that regime identical.

And in the regime that matters:

    network_lp, matches H1-C1 and H2-C1 only : Q_H = 150.000000
    C2 duty, reachable by no unit             : 150.000000
    the agent's hand-computed floor           : Q_H >= 150.000000

**Exact agreement with the agent**, where the old model said 142.5.

**A model validated in one regime and used in another is not validated.** That sentence is the
whole of Finding 043, and it now has a second regime behind it.

## 3. The corrected unit-count table

Every match set of the 4-stream case, scored by the corrected model:

| units | networks | best Q_H | attains Q_H_min = 142.5 |
|---|---|---|---|
| 1 | 4 | 232.500000 | no |
| **2** | 6 | **150.000000** | **no** |
| **3** | 4 | **142.500000** | **YES** |
| 4 | 1 | 142.500000 | YES |

**The 2-unit networks bottom out at exactly 150.0 - the agent's number.** So the network I offered
as the refutation of V = 3 could not in fact reach the requirement, and the agent was right to
reject it.

**The fewest units attaining Q_H_min is 3**, against N - 1 = 4.

## 4. So U >= N - 1 IS refuted - and the argument is now clean

**N = 5** (four process streams plus the hot utility the design needs), so N - 1 = 4.

**A connected graph on 5 nodes needs at least 4 edges. Any 3-edge graph on 5 nodes is therefore
disconnected.** And a 3-unit network attains the minimum utility.

That is the whole refutation:

  * $U \ge N - 1$ would require every design to be connected.
  * **A 3-unit design cannot be connected**, and one of them attains $Q_{H,\min}$.
  * So the bound is false, and it fails for the reason Finding 037 named - a disconnected network
    needs only a spanning tree per component - even though the witness Finding 037 used was
    fictitious.

**The conclusion survived the correction; the evidence did not.** That is worth stating plainly:
had the corrected model come out the other way, the earlier finding would have been wrong in
substance and not merely in proof.

## 5. What is still not established

  * **The bound is refuted; no corrected bound is offered.** The pinch-based candidate sketched in
    Finding 037 - max over the pinch decomposition of the hot and cold stream counts on each side
    - has still never been tested, and finding 037's sketch of it was made in the same round as
    the invalid refutation.
  * The claim that a 3-unit network attaining 142.5 is physically BUILDABLE is argued from the
    model, not demonstrated by constructing one with exchanger areas and checking the temperature
    profile. The model's level-to-level transfers correspond to real exchangers, but the
    correspondence was not exhibited.
  * Only the 4-stream case was enumerated this round. The 2x2 and 3x2 unit tables have not been
    recomputed, and Finding 037's claims about them are equally affected.
  * The agent's reasoning was still not read. It reached a correct physical objection; HOW it
    got there is unexamined, and that is the question that matters for whether this behaviour is
    reproducible.
