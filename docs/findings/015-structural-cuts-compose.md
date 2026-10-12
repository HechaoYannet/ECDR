# Finding 015 - Structural cuts compose; performance cuts do not

Status: Finding 013's prescription is **confirmed quantitatively**, over three
independent ensembles. The requirement's own three constraints are redundant; structural
axes are complementary.
Code: ecdr/structure/capability.py. Reproduce: scripts/step27_independence.py

## 1. The measurement

For each candidate cut, take the set of structures it rules out, and compute pairwise

    independence ratio  =  observed joint survival / (product of marginal survivals)

1.0 means independent, below 1 means the cuts overlap more than chance (redundant),
above 1 means they are complementary - a structure ruled out by one is LESS likely to be
ruled out by the other, which is exactly what a certificate library needs.

600 structures per ensemble, calibration sag <= 8 mm, peak <= 8, in-band <= 0.30.

## 2. Individual cuts are all non-trivial

| cut | rules out | fraction |
|---|---|---|
| PERF: sag | 247 | 0.4117 |
| PERF: peak | 258 | 0.4300 |
| PERF: in-band | 307 | 0.5117 |
| STR: payload grounded | 250 | 0.4167 |
| STR: >= 2 ground ties | 323 | 0.5383 |
| STR: payload degree >= 3 | 169 | 0.2817 |
| STR: n >= 6 | 269 | 0.4483 |

## 3. The pairwise structure

The most redundant pair in the whole table is a performance pair:

| pair | ratio | kind |
|---|---|---|
| PERF: sag x PERF: in-band | **0.5221** | performance-performance |
| PERF: sag x STR: payload grounded | 0.7673 | cross |
| PERF: sag x STR: >= 2 ground ties | 0.7732 | cross |
| PERF: peak x PERF: in-band | 0.8922 | performance-performance |
| PERF: peak x STR: payload grounded | 0.8872 | cross |
| PERF: sag x PERF: peak | 1.0487 | performance-performance |
| STR: payload grounded x STR: n >= 6 | 0.9322 | structural-structural |
| STR: payload grounded x STR: degree >= 3 | 0.9785 | structural-structural |
| STR: >= 2 ground ties x STR: degree >= 3 | 1.0855 | structural-structural |
| STR: degree >= 3 x STR: n >= 6 | 1.1860 | structural-structural |
| STR: payload grounded x STR: >= 2 ground ties | 1.1944 | structural-structural |
| **STR: >= 2 ground ties x STR: n >= 6** | **1.2892** | structural-structural |

| family | mean ratio | n pairs |
|---|---|---|
| performance-performance | **0.8210** | 3 |
| cross | 0.9709 | 12 |
| structural-structural | **1.1110** | 6 |

## 4. It holds across seeds

| seed | perf-perf | struct-struct | cross | direction |
|---|---|---|---|---|
| 5 | 0.8210 | 1.1110 | 0.9709 | structural more independent |
| 17 | 0.8268 | 1.0911 | 0.9524 | structural more independent |
| 29 | 0.8178 | 1.1059 | 0.9875 | structural more independent |

Mean over seeds: **0.8219 performance against 1.1027 structural.** The values are tight
and every seed agrees on the direction.

**Caveat, stated plainly:** each seed contributes only 3 performance-performance pairs and
6 structural-structural pairs. Three seeds agreeing on the DIRECTION is the evidence here,
not a significance test.

## 5. What it means

  * **The requirement's own three constraints are redundant.** sag, peak and in-band are
    all consequences of one underlying structural quality, and the worst pair (sag x
    in-band, 0.522) means one of them contributes barely half of what independence would
    give. Composing along the requirement's own axes is the weakest thing available.
  * **Structural axes are complementary.** A structure ruled out by "at least two ground
    ties" is measurably less likely to be ruled out by "at least six components" (1.289).
    These are the cuts that actually shrink the space.
  * **So the library must be built as structural axes layered on top of the requirement's
    constraints**, not as a decomposition of the requirement.

## 6. The honest gap, unchanged

**The structural predicates measured here are NOT certificates.** No sound bound has been
proved along any of them. What this finding establishes is that a certificate found along
a structural axis **would compose**, which is the precondition for looking there.

Alongside Finding 014, which produced one confirmed structural law (the payload's own
ground damping fixes the leading high-frequency behaviour, verified over 600 structures),
the picture is now:

| | certificate proved | axis type | would compose? |
|---|---|---|---|
| payload ground-damping law | yes, leading order | structural | predicted yes |
| payload grounded | no | structural | yes (1.194 with ground ties) |
| >= 2 ground ties | no | structural | yes (1.289 with n >= 6) |
| sag, peak, in-band | yes, but they ARE the requirement | performance | no (0.82) |

The next certificate should be looked for on a structural axis, and its independence
against the payload ground-damping law must be reported.

## 7. Limits

  * Two to six pairs per family per seed. The direction is robust; the magnitudes are not
    precise.
  * One ensemble family (random trees, log-uniform component values) and one calibration.
    Independence ratios depend on the calibration, which was not swept.
  * The structural predicates are binary thresholds chosen by hand; a different threshold
    on the same feature would give a different ratio.
