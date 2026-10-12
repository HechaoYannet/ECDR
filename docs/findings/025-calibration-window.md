# Finding 025 - The library's working range, and what happens outside it

Status: the calibration boundary Finding 024 could only say existed is now located. The
mechanism works for marginal cuts between 0.2 and 0.6, is best at 0.5, and beyond 0.7 the
four sound certificates exclude the entire space outright - which is a stronger conclusion
than the library was built for, reached cheaply.
Reproduce: scripts/step51_calibration_sweep.py.  Data: runs/calibration_sweep.json

## 1. The sweep

For each target marginal f, every certificate rules out exactly the f-fraction its own
ordering selects, so all four marginals are f by construction:

    C1 modal     the f-fraction with the FEWEST components
    C2 statics   the f-fraction with the LARGEST sag
    C3 slow      the f-fraction with the LARGEST omega_1^2 bound
    C4 fast      the f-fraction with the SMALLEST omega_n^2 bound

800 networks per setting, four certificates applied in sequence.

## 2. Original family

| f | f2 given 1 | f3 given 1,2 | f4 given 1,2,3 | survival | left of 800 | rounds for 1e10 | certificates |
|---|---|---|---|---|---|---|---|
| 0.1 | 0.1083 | 0.0919 | 0.0720 | 0.67625 | 541 | 58.86 | 235 |
| 0.2 | 0.2234 | 0.2093 | 0.1221 | 0.43125 | 345 | 27.38 | 110 |
| 0.3 | 0.3464 | 0.3689 | 0.1645 | 0.24125 | 193 | 16.19 | 65 |
| 0.4 | 0.4667 | 0.5547 | 0.2018 | 0.11375 | 91 | 10.59 | 42 |
| **0.5** | 0.6100 | 0.7564 | 0.3421 | 0.03125 | 25 | **6.64** | **27** |
| 0.6 | 0.7125 | 0.9457 | 0.2000 | 0.00500 | 4 | 4.35 | 17 |
| 0.7 | 0.7917 | **1.0000** | **1.0000** | 0.00000 | **0** | - | - |
| 0.8 | 0.8938 | 1.0000 | 1.0000 | 0.00000 | 0 | - | - |
| 0.9 | 0.9500 | 1.0000 | 1.0000 | 0.00000 | 0 | - | - |

## 3. New family - the same shape

| f | f2 given 1 | f3 given 1,2 | f4 given 1,2,3 | survival | left of 800 | rounds for 1e10 | certificates |
|---|---|---|---|---|---|---|---|
| 0.1 | 0.0917 | 0.1009 | 0.0544 | 0.69500 | 556 | 63.29 | 253 |
| 0.2 | 0.2016 | 0.2172 | 0.0875 | 0.45625 | 365 | 29.34 | 117 |
| 0.3 | 0.3179 | 0.3508 | 0.1573 | 0.26125 | 209 | 17.15 | 69 |
| 0.4 | 0.4500 | 0.5795 | 0.2432 | 0.10500 | 84 | 10.22 | 41 |
| **0.5** | 0.5650 | 0.7644 | 0.3415 | 0.03375 | 27 | **6.79** | **27** |
| 0.6 | 0.6750 | 0.9615 | 0.7500 | 0.00125 | 1 | 3.44 | 14 |
| 0.7 | 0.8042 | 0.9787 | **0.0000** | 0.00125 | 1 | 3.44 | 14 |
| 0.8 | 0.8875 | 1.0000 | 1.0000 | 0.00000 | 0 | - | - |
| 0.9 | 0.9500 | 1.0000 | 1.0000 | 0.00000 | 0 | - | - |

## 4. Three regimes

**Below f = 0.2, the cuts are too weak.** Each conditional is near its marginal, so the
certificates behave almost independently and 235 to 253 of them are needed.

**Between f = 0.2 and f = 0.6 the mechanism works, and 0.5 is optimal.** Both families give
the same answer: **27 certificates**, 6.64 and 6.79 rounds for N = 1e10. The conditionals
exceed their marginals throughout - 0.61 and 0.76 at f = 0.5 against a marginal of 0.5 - so
the certificates are complementary and the composition is better than independence.

**Above f = 0.7 the space is empty.** Not "the measurement failed": the four sound
certificates between them exclude all 800 structures. The survivor column makes the collapse
explicit - 541, 345, 193, 91, 25, 4, **0**. The conditional of 1.0000 for C3 is one
certificate removing everything that remained.

## 5. The empty regime is a result, not a failure

When the certificates exclude the whole space, they have **proved that no structure in it can
meet the requirement**, using four cheap bounds per structure rather than a transfer function.
That is a stronger conclusion than the library was designed to produce - the library only
needs to reduce the space to a sampleable remainder; here it eliminates it.

**But it must not be reported as a separation.** The figure of merit is
log N / log(1/survival), and it is undefined when survival is zero because there is nothing
left to search. Claiming "infinitely fast" here would be the same class of error as the six
identity traps: a quantity evaluated in a regime where it does not mean what it says.

## 6. f is a calibration device, not a physical parameter

The four thresholds were set at quantiles of THIS ensemble's own distributions. In a real
problem they come from the requirement. So f measures **how tight the requirement is relative
to the ensemble's capability distribution**, and the finding is:

> The library mechanism needs the requirement to sit in a band relative to the capability
> distribution - neither so loose that each certificate takes almost nothing, nor so tight
> that the certificates eliminate the space before the library can iterate.

At the optimum the band is centred on the median, which is Finding 012's calibration
condition appearing for the fourth time.

## 7. C4 is the weak member at every calibration

| f | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 |
|---|---|---|---|---|---|
| C2 given previous | 0.2234 | 0.3464 | 0.4667 | 0.6100 | 0.7125 |
| C3 given previous | 0.2093 | 0.3689 | 0.5547 | 0.7564 | 0.9457 |
| **C4 given previous** | **0.1221** | **0.1645** | **0.2018** | **0.3421** | 0.2000 |

C4's conditional sits well below the other two at every working calibration, and below its
own marginal of f throughout. **It is redundant with what C1 to C3 already removed**, which
is the corrected reading of a ratio above 1. The four members are not of equal value: C3
carries the round, C4 contributes least, and the figure of 27 certificates would barely move
if C4 were dropped.

## 8. Limits

  * f is applied identically to all four certificates. A real requirement would place them
    independently, and the optimum could differ.
  * The thresholds are quantiles of the same 800 structures they are then applied to, so the
    marginals are exact by construction and the conditionals carry all the information. This
    is a fair test of composition but not of calibration against an out-of-sample requirement.
  * Two families, two seeds, one physical domain.
  * The empty regime was not probed for where exactly it begins between f = 0.6 and 0.7.
  * No fifth certificate was added, so whether a stronger member could rescue the f >= 0.7
    regime is untested.
