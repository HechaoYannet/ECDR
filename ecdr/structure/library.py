"""Certificate LIBRARIES, not single certificates.

Why the single-certificate target in roadmap 5.4 is too weak
------------------------------------------------------------
5.4 asked for one certificate with g(N) = Theta(N), covering a constant fraction.  That
is necessary for a persistent speedup but it caps the speedup at 1/(1-f), which for any
realistic f is a small constant.  Covering half the space buys a factor of two.  That
cannot be the result.

The composition argument
------------------------
Suppose a LIBRARY of certificates where certificate i rules out a fraction f_i of the
space REMAINING after certificates 1..i-1.  Then

    remaining fraction after k certificates  =  prod_i (1 - f_i)

and if every f_i >= f > 0 then remaining <= (1 - f)^k.  So

    k = O( log N / log(1/(1-f)) )

certificates reduce the space to a sampleable remainder, at total cost k * c_p against
Theta(N) * c_s for exhaustive sampling.

**Even a one percent coverage fraction gives an exponential separation**, because it is
the logarithm that grows.  That is a far weaker and far more reachable requirement than
"cover half the space", and it is the correct design target:

    not one certificate with g(N) = Theta(N),
    but a LIBRARY whose per-step coverage has a CONSTANT LOWER BOUND.

So the thing to check is not the size of any single cover but whether there exists a
sequence of certificates whose successive coverage fractions stay bounded away from zero.
"""
from __future__ import annotations

import math


def certificates_needed(N: int, f: float) -> float:
    """k such that (1-f)^k * N <= 1."""
    if N <= 1:
        return 0.0
    if not 0.0 < f < 1.0:
        raise ValueError("coverage fraction must lie strictly in (0, 1)")
    return math.log(N) / math.log(1.0 / (1.0 - f))


def separation(N: int, f: float, c_p_over_c_s: float = 1.0) -> dict:
    """Cost of the certificate library against exhaustive sampling, in units of c_s."""
    k = certificates_needed(N, f)
    return {
        "N": int(N),
        "coverage_fraction": f,
        "certificates_needed": k,
        "library_cost_in_c_s": k * c_p_over_c_s,
        "sampling_cost_in_c_s": float(N),
        "separation": N / max(k * c_p_over_c_s, 1e-12),
    }
