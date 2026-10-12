# Finding 026 - L2 exists: an independent numerical route, and what it does not give

Status: OpenModelica, the chosen L2 kernel, **cannot be installed in this environment**.
A different independent kernel was obtained instead and the L2 rung now runs and
cross-validates L0/L1. What it provides is independence of NUMERICS; independence of
MODELLING is still missing and is stated as such.
Reproduce: scripts/step52_l2_verify.py, step53_l2_convergence.py.
Data: runs/l2_crossvalidation.json, runs/l2_convergence.json

## 1. The OpenModelica blocker, in detail

docs/decisions/002 chose OpenModelica for L2, for independence and for alignment with
industrial multi-domain plant modelling. Every installation path was probed:

| path | result |
|---|---|
| conda-forge `openmodelica` | **no such package**. `ompython` exists (4.0.1, 4.1.0) but is only the Python interface and needs an `omc` compiler that is not present |
| chocolatey | **not an administrator**; `IsInRole(Administrator)` is False |
| WSL Ubuntu | present, but `sudo -n true` fails - **a password is required** |
| Docker | daemon not running: `open //./pipe/dockerDesktopLinuxEngine` - the system cannot find the file specified |
| direct install | Windows installer would need elevation |

So the intended kernel is **not obtainable here** without user action: starting Docker
Desktop, supplying the administrator password, or granting WSL sudo.

## 2. What was obtained instead

**Julia 1.11 with DifferentialEquations.jl 142 dependencies**, installed through
`uv pip install juliacall` and `Pkg.add` - no elevation needed. A different
language, a different compiler, and a different integrator suite (Tsit5 and the SciML
stack) from the SciPy machinery L0 and L1 share.

The user started the Clash Verge proxy partway through; before that, direct downloads of
the Julia registry and the micromamba/pixi artifacts worked but slowly. The proxy at
127.0.0.1:7897 returned 200 on both pkg.julialang.org and github.com once it was up.

## 3. What L2 does

L0 and L1 solve the algebraic frequency-domain system

    (K - w^2 M + i w C) X  =  (f + i w g)

for a grid of w and take abs(X[payload]). L2 does something categorically different:
it integrates

    M x'' + C x' + K x = f x_g + g x_g',        x_g(t) = sin(w t)

in the time domain until the transient has decayed, and measures the payload amplitude over
the last period. For a stable LTI system that amplitude IS the transmissibility magnitude.
**No formula is shared**, so an error in the assembly of M, C, K, f, g, in the sign of the
ground coupling, or in the frequency-domain algebra appears in one route and not the other.

## 4. The cross-validation

Twelve comparisons, four structures, frequencies below, at, and above the first resonance:

| structure | n | omega | frequency domain | time domain | rel diff |
|---|---|---|---|---|---|
| 0 | 4 | 13.7054 | 1.0084185938 | 1.0084151961 | 3.4e-06 |
| 0 | 4 | 45.6846 | 1.1048450820 | 1.1048444665 | 5.6e-07 |
| 0 | 4 | 182.738 | 1.6059243806 | 1.6056535947 | 1.7e-04 |
| 1 | 5 | 11.4021 | 1.1164433723 | 1.1164406111 | 2.5e-06 |
| 1 | 5 | 38.0071 | 3.3564088480 | 3.3564077178 | 3.4e-07 |
| 1 | 5 | 152.029 | 1.9083067690e-02 | 1.9083020670e-02 | 2.5e-06 |
| 2 | 3 | 8.98113 | 1.0755888715 | 1.0755868439 | 1.9e-06 |
| 2 | 3 | 29.9371 | 1.2323688992 | 1.2323688911 | 6.6e-09 |
| 2 | 3 | 119.748 | 1.8099833577 | 1.8099829716 | 2.1e-07 |
| 3 | 3 | 13.0421 | 1.0243421142 | 1.0243489376 | 6.7e-06 |
| 3 | 3 | **43.4737** | **1.5383468808e+01** | **1.4554589356e+01** | **5.4e-02** |
| 3 | 3 | 173.895 | 1.7281451262 | 1.7481135015 | 1.2e-02 |

**median 2.5e-06, 10 of 12 within 1e-3, two outliers 5.4e-02 and 1.2e-02** - and both
outliers are on structure 3, whose first resonance is omega_1 = 43.4737.

## 5. The outliers were an unconverged transient, and the direction proved it

At resonance the steady-state amplitude is largest and the transient decays slowest, so a
fixed number of periods can stop before steady state. **That predicts the error direction**:
the time-domain amplitude should be LOW and should RISE toward the frequency-domain value as
the integration is extended. Extending it:

| periods | omega = 43.4737, rel diff | omega = 173.895, rel diff |
|---|---|---|
| 80 | 5.390e-02 | 1.155e-02 |
| 160 | 7.912e-05 | 5.286e-03 |
| 320 | 3.315e-05 | 8.557e-04 |
| 640 | 1.495e-06 | 1.291e-04 |
| 1280 | **1.494e-06** | **1.313e-06** |

Both converge to about 1.5e-06. **The disagreement was integration time, not physics.**

## 6. Three errors of my own, caught

  * **mass matrix passed where the mass vector was expected.** The kernel does
    Minv = 1 ./ Mv and broadcasts it down rows; handing it the diagonal matrix made the
    state dimension 2n^2 and the failure was a shape error, which is at least loud.
  * **the wrong structure tested.** Step 52 printed "structure 3" for the FOURTH PICKED
    structure, which is `ens[7]]`. Step 53 tested `ens[3]` - a different
    network with omega_1 = 83.74 - and reported its good agreement as though it were the
    failing case. The printed label was a position, not an index.
  * **a silent integration failure.** The 1280-period run of that wrong test hit
    `maxiters` and Julia returned an Interrupted solution whose value was
    **1.05e+12** where the answer is 1.38. The fix is to raise maxiters and to check
    `successful_retcode` rather than trusting whatever comes back.

The third is the same class as the six identity traps and the inverted ratio: **a number
produced in a regime where it does not mean what it says, read as a finding.**

## 7. What this establishes, and what it does not

**Does**: independence of NUMERICS. Two routes sharing no formula agree to 2.5e-06 at the
median across 12 comparisons spanning three decades of frequency, and the only outliers
resolve to the same agreement when integrated long enough.

**Does not**: independence of MODELLING. Both routes solve the same
M x'' + C x' + K x = f x_g + g x_g'. If those equations are the wrong model of the physical
situation - if a real isolator has nonlinearity, friction, or a boundary condition this
formulation omits - neither route detects it. **That is exactly what the Modelica decision
was for**, and it remains unmet.

## 8. Limits

  * 12 comparisons, 4 structures, all from one ensemble family. Not a survey.
  * Only the transmissibility was cross-checked. The L1 robustness and actuator-lag
    machinery has no independent check at all.
  * L1 remains a second Python implementation by the same author, which decision 001 itself
    says is not independent validation.
  * The convergence test used 1280 periods, which is enough here but was not derived; for a
    more lightly damped structure it would not be.
