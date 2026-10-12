"""Layer A, first cut: a structure space whose size actually grows.

Why a graph space and not a parameter box
-----------------------------------------
Roadmap section 5.4 says a certificate is useful only if g(N) - the NUMBER of
structures it rules out - grows without bound.  A continuous parameter box cannot
exhibit that: doubling a box's extent doubles a measure, it does not multiply the
number of structures.  So the census has to run on a space whose size grows
combinatorially in the number of components.

The space
---------
A structure is
  * a CONNECTED simple graph on n labelled nodes, each node a mass, each edge a
    spring-damper pair;
  * one distinguished node, the payload (the output);
  * a NON-EMPTY subset of nodes tied to ground by a spring-damper.

Every edge type is fixed here on purpose: the census is about how many structures an
invariant covers, so the space must be countable exactly and the combinatorics must
not be confounded with component-type choices.  Component types are a later axis.

Size of the space
-----------------
    abs(S(n)) = c(n) * (2^n - 1)

with c(n) the number of connected labelled graphs on n nodes (OEIS A001187).
"""
from __future__ import annotations

from math import comb

# OEIS A001187: connected labelled graphs on n nodes, for n = 0..10
CONNECTED_LABELED_GRAPHS = [0, 1, 1, 4, 38, 728, 26704, 1866256,
                            251548592, 66296291072, 34496488594816]


def structures_with_n_nodes(n: int) -> int:
    """abs(S(n)) = connected labelled graphs times non-empty ground subsets."""
    if n < 1 or n >= len(CONNECTED_LABELED_GRAPHS):
        raise ValueError("n out of range: " + str(n))
    return CONNECTED_LABELED_GRAPHS[n] * (2 ** n - 1)


def space_size(n_max: int) -> int:
    """Total number of structures with at most n_max nodes."""
    return sum(structures_with_n_nodes(n) for n in range(1, n_max + 1))


def invariant_mode_count(n_max: int, m: int) -> int:
    """I1 - mode counting.

    A linear time-invariant structure with n degrees of freedom has a free response
    that is a sum of at most n harmonics.  A target with m distinct frequencies
    therefore needs n >= m.  This invariant rules out every structure with n < m.
    """
    return sum(structures_with_n_nodes(n) for n in range(1, min(m, n_max + 1)))


def invariant_ground_paths(n_max: int, q: int) -> int:
    """I2 - ground-path counting.

    A requirement that needs q independent paths to ground rules out every structure
    whose ground subset has fewer than q nodes.  For each n, the number of ground
    subsets of size below q is sum over j < q of C(n, j).
    """
    total = 0
    for n in range(1, n_max + 1):
        c = CONNECTED_LABELED_GRAPHS[n]
        bad = sum(comb(n, j) for j in range(1, min(q, n + 1)))
        total += c * bad
    return total


def invariant_balanced_ground(n_max: int) -> int:
    """I3 - a threshold property on a BALANCED attribute.

    Rules out structures whose ground subset has fewer than half the nodes.  Unlike a
    resource bound, this property is satisfied by an almost constant fraction of the
    space (about one half), so g(N) should be Theta(N).  It is included because the
    census has to show that all three regimes of roadmap 5.4 are reachable; if only the
    degenerate ones were reachable the crossing claim would be empty.
    """
    total = 0
    for n in range(1, n_max + 1):
        c = CONNECTED_LABELED_GRAPHS[n]
        half = n // 2
        bad = sum(comb(n, j) for j in range(1, half + 1))
        total += c * bad
    return total


def growth_table(n_max_values, m_fixed: int = 4, q_fixed: int = 3):
    """g(N) and g/N for each invariant, requirement held FIXED."""
    rows = []
    for nm in n_max_values:
        N = space_size(nm)
        g1 = invariant_mode_count(nm, m_fixed)
        g2 = invariant_ground_paths(nm, q_fixed)
        g3 = invariant_balanced_ground(nm)
        rows.append({
            "n_max": nm, "N": N,
            "g_I1": g1, "frac_I1": g1 / N,
            "g_I2": g2, "frac_I2": g2 / N,
            "g_I3": g3, "frac_I3": g3 / N,
            "speedup_I1": N / max(N - g1, 1),
            "speedup_I2": N / max(N - g2, 1),
            "speedup_I3": N / max(N - g3, 1),
        })
    return rows


def growth_table_scaling(n_max_values):
    """Same, but the requirement SCALES with the space: m = n_max // 2."""
    rows = []
    for nm in n_max_values:
        N = space_size(nm)
        m = max(2, nm // 2)
        g1 = invariant_mode_count(nm, m)
        rows.append({"n_max": nm, "N": N, "m": m,
                     "g_I1": g1, "frac_I1": g1 / N,
                     "speedup_I1": N / max(N - g1, 1)})
    return rows
