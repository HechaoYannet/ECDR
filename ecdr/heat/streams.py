"""Layer A for a SECOND domain: heat-exchanger network synthesis (M6).

Why this domain
---------------
The vibration work is ours from end to end, so it can show the theory stands up but not that
the method works (Finding 009 section 2.2).  M6 needs a scenario we did not author, with its
own requirement and its own physics.  Heat-exchanger network synthesis is that scenario, and
it maps onto ECDR term for term:

    structure S          a network of heat exchangers matching hot streams to cold streams
    capability           how much hot utility the network needs
    requirement          hot utility <= Q*
    delta(S) > epsilon   every network misses the requirement
    CERTIFICATE          Q_H_min, the thermodynamic minimum hot utility, which is a lower
                         bound over ALL networks and is computed from the STREAM DATA alone

Q_H_min is the exact analogue of the modal-dimension certificate: it is a property of the
problem, not of any design, so it rules out an unbounded family at a cost that does not grow
with the family.  And it NAMES what is missing - the pinch temperature and the heat deficit
at it - which is what a repair has to act on.

Conventions
-----------
A hot stream must be cooled, t_in > t_out.  A cold stream must be heated, t_in < t_out.
cp is a heat capacity flowrate in kW/K, so a stream's duty is cp * (t_in - t_out).
Temperatures are in degrees Celsius; only differences matter, so this is consistent.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Stream:
    name: str
    t_in: float
    t_out: float
    cp: float

    @property
    def hot(self) -> bool:
        return self.t_in > self.t_out

    @property
    def duty(self) -> float:
        return self.cp * abs(self.t_in - self.t_out)

    def shifted(self, dt_min: float):
        """Supply and target temperature after the half-pinch shift.

        Hot streams are moved DOWN by dt_min/2 and cold streams UP by dt_min/2, so that two
        streams whose shifted ranges overlap can exchange heat while respecting dt_min.
        """
        h = dt_min / 2.0
        if self.hot:
            return (self.t_in - h, self.t_out - h)
        return (self.t_in + h, self.t_out + h)


def _intervals(streams, dt_min):
    """Shifted temperature intervals, from the hottest boundary downwards."""
    edges = set()
    for s in streams:
        a, b = s.shifted(dt_min)
        edges.add(a)
        edges.add(b)
    ts = sorted(edges, reverse=True)
    return [(ts[i], ts[i + 1]) for i in range(len(ts) - 1)]


def problem_table(streams, dt_min: float) -> dict:
    """Linnhoff's problem table: the minimum hot and cold utility and the pinch.

    The cascade starts at the top with zero heat and accumulates the net surplus of each
    interval.  Its most negative value is the heat that must be supplied from hot utility
    above the pinch; the value left at the bottom is the cold utility.
    """
    ivs = _intervals(streams, dt_min)
    rows = []
    for (top, bot) in ivs:
        dt = top - bot
        cp_hot = sum(s.cp for s in streams if s.hot
                     and s.shifted(dt_min)[1] <= bot + 1e-12
                     and s.shifted(dt_min)[0] >= top - 1e-12)
        cp_cold = sum(s.cp for s in streams if (not s.hot)
                      and s.shifted(dt_min)[1] >= top - 1e-12
                      and s.shifted(dt_min)[0] <= bot + 1e-12)
        rows.append({"top": top, "bottom": bot, "dt": dt,
                     "cp_hot": cp_hot, "cp_cold": cp_cold,
                     "surplus": (cp_hot - cp_cold) * dt})

    cascade = [0.0]
    for r in rows:
        cascade.append(cascade[-1] + r["surplus"])
    cascade = cascade[1:]
    deficit = min(cascade) if cascade else 0.0
    q_h = max(0.0, -deficit)
    shifted = [c + q_h for c in cascade]
    q_c = shifted[-1] if shifted else 0.0

    pinch_shifted = None
    for i, c in enumerate(cascade):
        if abs(c - deficit) < 1e-9:
            pinch_shifted = rows[i]["top"]
            break
    return {
        "Q_H_min": float(q_h),
        "Q_C_min": float(q_c),
        "pinch_shifted_T": None if pinch_shifted is None else float(pinch_shifted),
        "intervals": rows,
    }


def min_utility_lp(streams, dt_min: float) -> dict:
    """The same minimum utility by LINEAR PROGRAMMING - an independent implementation.

    Transshipment model: let R_k be the heat carried from interval k down to k+1.  Each
    interval balances the heat its hot streams release against what its cold streams absorb,
    with the residual passed downward.  Minimising the heat supplied at the very top gives
    the minimum hot utility.

    This encodes the SAME relaxation as the problem table, so agreement checks the
    implementation rather than the physics.  The physics - that no network can beat it -
    rests on the argument stated in certificates.py, and is what the achievability question
    in the finding is about.
    """
    from scipy.optimize import linprog

    ivs = _intervals(streams, dt_min)
    K = len(ivs)
    # variables: R_0..R_{K-1} (heat passed down out of each interval) and Q_H at the top
    # balance for interval k:  Q_in(top) + hot_k = cold_k + R_k
    #   where Q_in for k=0 is Q_H and for k>0 is R_{k-1}
    A_eq = []
    b_eq = []
    for k, (top, bot) in enumerate(ivs):
        dt = top - bot
        hot = sum(s.cp * dt for s in streams if s.hot
                  and s.shifted(dt_min)[1] <= bot + 1e-12
                  and s.shifted(dt_min)[0] >= top - 1e-12)
        cold = sum(s.cp * dt for s in streams if (not s.hot)
                   and s.shifted(dt_min)[1] >= top - 1e-12
                   and s.shifted(dt_min)[0] <= bot + 1e-12)
        row = [0.0] * (K + 1)
        if k > 0:
            row[k - 1] = 1.0
        else:
            row[K] = 1.0
        row[k] = -1.0
        A_eq.append(row)
        b_eq.append(cold - hot)
    c = [0.0] * K + [1.0]
    bounds = [(0, None)] * K + [(0, None)]
    res = linprog(c, A_eq=np.array(A_eq), b_eq=np.array(b_eq), bounds=bounds,
                  method="highs")
    if not res.success:
        return {"ok": False, "message": str(res.message)}
    return {"ok": True, "Q_H_min": float(res.x[K])}
