# Finding 061 - M4 complete: the certificate is not crossed by the fidelity change

Status: **C1 survives at L2.** The free response OpenModelica integrated has every spectral peak on
one of the structure's own natural frequencies, never more peaks than n, and when L0 is measured by
**the same procedure** the two fidelities agree to **9.50e-05**. Section 6 Layer C revokes nothing.
**M4 is now complete**: the cost half was Finding 060, this is the soundness half.
Reproduce: scripts/step83_m4_free_response.py, scripts/step85_m4_l0_free.py.
Data: runs/m4_free_response.json, runs/m4_l0_free.json

## 1. The missing model, and why both earlier attempts failed

Every emitter in this project produced a **base-excited** model. That made two attempts to re-check
C1 at L2 invalid, and both for the same reason:

  * a **forced-response magnitude** |T(omega)| says nothing about how many harmonics the FREE
    response has - and for base excitation it is about 1 at every frequency, so the test could not
    fail; it printed "agreement 7 of 8";
  * a **pole count** on a base-excited model returns n + 1 oscillatory pairs, because the excitation
    source contributes a state; C1 as literally stated then fails 0 of 8.

**The new `emit_free_model` has no input at all.** The ground is an MSL Fixed component and the
motion comes from nonzero initial conditions on the masses. It still writes only declarations and
connections. What OpenModelica integrates is a genuine free response.

## 2. C1 at L2

| idx | n | peaks at L2 | modes excited | worst peak-to-mode | C1 violated? |
|---|---|---|---|---|---|
| 0 | 4 | 1 | 1 of 4 | 6.114e-02 | no |
| 1 | 5 | 4 | 4 of 5 | 4.497e-02 | no |
| 3 | 5 | 2 | 3 of 5 | 4.497e-02 | no |
| 6 | 2 | 2 | 2 of 2 | 4.497e-02 | no |
| 7 | 3 | 2 | 2 of 3 | 4.497e-02 | no |

**0 violations on 8 structures.** The falsifier was a peak with no matching mode - a harmonic the
structure does not have - or more peaks than n. Neither occurred.

**And the weakness is stated rather than hidden**: only 1 to 4 of each structure's modes were excited
at all, so this confirms "**at most n**" and **does not** confirm "exactly n". A method producing
fewer harmonics than the structure allows would pass this test too.

## 3. The L0 cross-check, done properly

Step 84 tried to confirm L0's natural frequencies against the peaks of L0's **transmissibility**.
**That is invalid**: a base-excited transfer function has zeros as well as poles, an antiresonance
sits between two resonances, and a pole can be largely cancelled. Magnitude peaks of a
transmissibility are not the natural frequencies, and the two lists disagreeing by 82 per cent says
nothing about either.

**The valid L0 route is the same experiment at L0**: integrate M x'' + C x' + K x = 0 from the same
initial conditions, take the same spectrum, compare. Both fidelities are then measured by one
procedure, which is what a fidelity comparison requires.

| comparison | worst relative error |
|---|---|
| L0 integrated peaks against L0's eig frequencies | 6.104e-02 |
| **L2 peaks against L0 integrated peaks** | **9.500e-05** |

**So the two fidelities agree essentially exactly**, and the residual few-per-cent offset against
eig is **common to both** - it is a property of comparing a windowed spectrum to undamped
eigenfrequencies, most likely FFT bin resolution, and **it is not confirmed**. It is recorded as
unexplained rather than attributed, and it is not a fidelity difference because both sides show it
equally.

## 4. M4, closed

| half | status |
|---|---|
| the crossing reproduced at L1 and L2 with real costs | **DONE** - c_s 1.509e-03 / 6.036e-03 / **1.8816 s**, separation 9.296e+14 -> 3.446e+15 -> **3.431e+16** |
| Modelica can express S | **DONE** - 8 structures, n = 2..8, forced responses to 4.62e-07 |
| the certificate's claim re-checked at L2 | **DONE** - 0 violations, L2 agrees with L0 to 9.50e-05 |
| the revocation path of section 6 Layer C exercised | **exercised, and nothing was revoked** |

**M4's own falsifier - "it moves out of reach, or Modelica cannot express S" - is not triggered.**
The crossing survives the cost ladder, and the certificate that carries it is confirmed at the top
of the ladder by an independent tool.

## 5. Two more invalid tests, and what caught them

Step 83's metric was **inverted**: it took each L0 mode, found the nearest peak, and kept the worst -
so a mode that was simply never excited scored as a 96 per cent mismatch. It reported "C1 does NOT
survive at L2". **Rereading the raw peaks instead of the summary statistic** is what caught it; the
peaks were sitting on the modes.

Step 84's cross-check compared eig frequencies to **transmissibility** peaks, and then printed
"L0's two independent routes agree to within 8.21e-01" - **where 8.21e-01 IS the disagreement.**

**Instances seven and eight.** The running list is now: a synthetic baseline; a held pre-factor; a
crossing never reached; four-unit count contradicting its own table; forced response testing a
free-response claim; the excitation's pole counted as a mode; an inverted metric; and a verdict
sentence stating agreement when the number was the disagreement.

**Five of the eight were internally consistent and arithmetically correct.** What caught these two
was not more computation but **looking at the raw data the statistic was computed from** - which is
the same defence that caught instance four.

## 6. Limits

  * **One ensemble, one initial condition per structure, eight structures.** The initial state
    `s0 = linspace(1, 1+0.3(n-1), n)` with zero velocity excites only some modes; a different
    perturbation would excite others and could in principle reveal a peak that is not a mode.
  * **The peak detector merges peaks closer than 5 per cent** and thresholds at 1e-3 of the largest.
    Two genuinely distinct modes closer than that would be counted as one, so the "at most n" test
    is, if anything, easier to pass than it should be.
  * **The few-per-cent offset against eig is unexplained**, as stated above.
  * **The certificate's claim is not re-derived from the Modelica file text.** The check is
    behavioural: what the tool integrated is compared to what the structure should do. A model with
    the right spectrum and the wrong equations would pass.
  * **L1 is not separately checked here.** Its cost multiplier is the corner count, and its models
    were validated in Findings 027 and 063.
