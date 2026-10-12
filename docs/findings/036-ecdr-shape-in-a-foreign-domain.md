# Finding 036 - The ECDR shape reproduces in a domain we did not author

Status: with the residual chains Finding 035 identified as missing, all four properties hold
exactly. Search enumerates every network and returns an upper bound; the certificate is
computed from the stream data alone and **decides**; and the bound is **tight**. This is the
first time the project's central claim has been demonstrated outside vibration.
Reproduce: scripts/step66_heat_ecdr_question.py.  Data: runs/heat_ecdr_question.json

## 1. The fix

Finding 035 recorded a network model that was 35 to 53 percent above the certificate because
it forced every temperature interval to balance on its own. With a minimum approach
temperature a hot stream at shifted level k can give heat to a cold stream at level k **or any
lower level** - which is what it means for a hot stream cooling from 200 to 100 to heat a cold
stream from 50 to 150. The model forbade exactly that.

The corrected formulation carries heat down:

    Q_ik   hot stream i's duty in interval k
    x_ijk  heat from hot i to cold j, matched inside interval k
    RH_ik  heat from hot i in interval k carried down to k+1
    RC_jk  heat delivered to cold j in interval k from the carried pool
    qH_jk  hot utility into cold j at level k
    qC_ik  cold utility out of hot i at level k

    (hot)  sum_j x_ijk + qC_ik + RH_ik = Q_ik
    (cold) sum_i x_ijk + RC_jk + qH_jk = Q_jk
    (pool) sum_i RH_ik = sum_j RC_j,k+1
    minimise sum qH

Summing the first two over i and j and subtracting recovers the aggregate balance
R_{k-1} + H_k + qH_k = R_k + C_k + qC_k, so with every match allowed this must reproduce the
problem table - **and it does, to the last digit.**

## 2. The four properties

| case | certificate Q_H_min | network LP, all matches | difference | best over every match set |
|---|---|---|---|---|
| 4-stream | 142.50000000 | **142.50000000** | **0.000e+00** | 142.50000000 |
| 2x2 | 60.00000000 | **60.00000000** | **0.000e+00** | 60.00000000 |
| 3x2 | 0.00000000 | **0.00000000** | **0.000e+00** | 0.00000000 |

| property | holds |
|---|---|
| 1. the network LP reproduces the problem table (same physics, two models) | **yes** |
| 2. no enumerated network beats the certificate | **yes** |
| 3. some network ACHIEVES it, so the bound is tight | **yes** |
| 4. the certificate rules out Q* while search cannot | **yes** (2 of 3 cases testable) |

Networks enumerated exhaustively: **15, 15 and 63**. More than one match set attains
Q_H_min - 142.5 is reached by several - which is the non-uniqueness a designer expects.

## 3. Why this is the ECDR shape

  * **Search** enumerates match sets and returns the best utility it finds. That is an
    **upper bound** on what is achievable, and every failed search is equally consistent with
    "no network works" and "I have not found it yet". **No amount of search converts one into
    the other** - the argument the project has rested on since the beginning.
  * **The certificate** is computed from the stream data alone, never looks at a network, and
    **decides** the question. With Q* = 0.9 * Q_H_min it declares the requirement infeasible,
    and the exhaustive enumeration confirms that nothing in the space reaches it.
  * And it is **tight**, so it is not sound-but-useless. A certificate that is sound but not
    tight is still a certificate; one that is tight but unsound is worthless. Here it is both.

**This is the first demonstration of the central claim in a domain we did not author.** The
vibration work is ours from end to end and could only show the theory stands up.

## 4. An error of my own, caught in the reporting

The first run of this experiment reported property 4 as **False** and printed "one of the four
properties fails; do not build on this yet" - **while the data underneath it showed the
certificate working correctly in both cases where it could be tested.**

The cause: the verdict was an all() over cases, and the 3x2 case has Q_H_min = 0. A
certificate of zero means no hot utility is needed at all, so there is no Q* below it to rule
out. That case is **VACUOUS** for this property, not a failure of it.

This is the same distinction Finding 025 met when the calibration sweep drove the survivor
count to zero and log N / log(1/survival) became undefined: **an empty or degenerate regime is
not a separation, and it is not a failure either.** The verdict now counts testable cases
separately and says so.

Had it been left, the project would have recorded a working certificate as broken - the
eighth instance of a number being read in a regime where it does not mean what it says, this
time in my own summary line rather than in a computation.

## 5. Limits

  * **Three stream sets**, with 4, 4 and 5 streams, one dt_min each in the enumeration. Not a
    survey, and the network space enumerated is match SETS, not full flowsheets with unit
    areas, splits and stream bypasses.
  * **Only 2 of 3 cases test the rule-out property**; the third is vacuous.
  * All streams are constant-cp, single-phase, fixed supply and target temperatures. That is
    exactly the certificate's domain tag, and it is **not valid for phase change**.
  * The utility relaxation allows utility heat at any temperature level. That is standard for
    a minimum-utility bound but is not how real utilities work.
  * **No capital cost, no area, no unit count.** The requirement modelled is utility alone, so
    the minimum-units certificate - the combinatorial analogue of modal counting - is still
    unwritten and is the other half of what makes this domain interesting.
  * **The orchestrator and the LLM loop are untouched.** M6's actual success criterion - an
    agent running the whole research flow and producing a domain-tagged certificate - is not
    addressed by this round, which builds the domain it would run in.
