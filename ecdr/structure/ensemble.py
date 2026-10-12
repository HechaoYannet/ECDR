"""Random ensembles of mechanical structures.

Coverage is a property of (invariant, ensemble, requirement) - not of the invariant
alone.  This module supplies ensembles so that claim can be measured rather than
asserted.

Two ensembles are provided that differ ONLY in how the number of components is drawn,
because that is the axis on which a combinatorial bound like mode counting is expected
to be degenerate or not.
"""
from __future__ import annotations

import numpy as np

from .network import Structure


def _loguniform(rng, lo, hi, size):
    return np.exp(rng.uniform(np.log(lo), np.log(hi), size))


def _loguniform_scalar(rng, lo, hi) -> float:
    """Log-uniform draw returned as a Python float, not a length-1 array."""
    return float(np.exp(rng.uniform(np.log(lo), np.log(hi))))


def random_structure(rng, n: int, ground_count=None, extra_edges: int = 0,
                     value_dist: str = "log") -> Structure:
    """A random tree on n masses, log-spread component values.

    ground_count = None draws the number of ground ties uniformly on 1..ceil(n/2).
    It MUST be variable: an earlier version always tied exactly one node, which left
    the "how many parallel paths to ground" axis with zero variance and made the
    structural-feature test silently vacuous on that axis.
    """
    masses = _loguniform(rng, 0.3, 3.0, n)

    springs = {}
    dampers = {}
    # random tree: each node k >= 1 attaches to a uniformly random earlier node
    for k in range(1, n):
        parent = int(rng.integers(0, k))
        springs[(parent, k)] = _loguniform_scalar(rng, 1e3, 1e5)
        dampers[(parent, k)] = _loguniform_scalar(rng, 1.0, 100.0)

    def draw(lo, hi):
        if value_dist == "uniform":
            return float(rng.uniform(lo, hi))
        return _loguniform_scalar(rng, lo, hi)

    # extra edges create loops, so the topology family is not just trees
    # A bounded attempt loop.  A small n has few possible non-edges - for n = 2 there is
    # exactly one - so an unbounded "while added < extra_edges" spins forever.
    added = 0
    attempts = 0
    while added < extra_edges and attempts < 20 * max(extra_edges, 1):
        attempts += 1
        i, j = sorted(rng.choice(n, size=2, replace=False).tolist())
        if (i, j) in springs:
            continue
        springs[(i, j)] = draw(1e3, 1e5)
        dampers[(i, j)] = draw(1.0, 100.0)
        added += 1

    if ground_count is None:
        ground_count = int(rng.integers(1, max(2, (n + 1) // 2 + 1)))
    g_nodes = rng.choice(n, size=min(ground_count, n), replace=False)
    ground_k = {int(g): draw(1e3, 1e5) for g in g_nodes}
    ground_c = {int(g): draw(1.0, 100.0) for g in g_nodes}
    return Structure(masses=masses, springs=springs, dampers=dampers,
                     ground_k=ground_k, ground_c=ground_c)


def ensemble(seed: int, count: int, n_lo: int = 2, n_hi: int = 8, fixed_n=None,
             ground_count=None, extra_edges: int = 0, value_dist: str = "log"):
    """Draw a batch of structures.

    fixed_n = None  -> n uniform on [n_lo, n_hi]      (size-spread)
    fixed_n = k     -> n always k                     (size-concentrated)
    """
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(count):
        n = int(fixed_n) if fixed_n is not None else int(rng.integers(n_lo, n_hi + 1))
        out.append(random_structure(rng, n, ground_count=ground_count,
                                    extra_edges=extra_edges, value_dist=value_dist))
    return out


def measure(structures):
    """Return the two sound bounds for each structure."""
    sag = []
    modes = []
    for s in structures:
        try:
            sag.append(s.static_deflection())
        except np.linalg.LinAlgError:
            sag.append(float("nan"))
        modes.append(s.mode_count())
    return np.array(sag, dtype=float), np.array(modes, dtype=int)
