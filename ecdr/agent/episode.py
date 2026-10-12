"""One experimental episode: run one arm on one task under a fixed budget.

Everything except the abandonment signal is held fixed:

  * the mechanism inventory and its order (M1 -> M2 -> M3)
  * the searcher (the same (mu+lambda) evolution strategy, same seeds)
  * the total evaluation budget, shared across mechanisms
  * the objective and the constraints

Two metrics are reported, because the first version conflated them:

  escaped   did the arm produce a design meeting the isolation target, verified
            with the EXACT peak routine.  This depends on the inner search as much
            as on the decision, so a weak searcher can make a correct decision look
            bad -- and an incorrect one look good.
  wasted    evaluations spent on mechanisms whose ground-truth label says they
            cannot work.  This isolates DECISION QUALITY from search strength, and
            it is the metric the hypothesis is actually about.
"""
from __future__ import annotations

from ..bench import MechanismProblem
from ..bench.family import MECHANISM_ORDER
from ..l0 import PassiveSDOF, SkyHookActive, TunedMassDamper
from ..l1 import LaggedSkyHook, MechanismProblemL1, verify_l1
from .policies import POLICY_FACTORY
from .search import PopulationSearch

MECHANISMS = {
    "M1_passive_sdof": PassiveSDOF,
    "M2_tuned_mass_damper": TunedMassDamper,
    "M3_sky_hook_active": SkyHookActive,
}

# At L1 the active mechanism gains a finite-bandwidth actuator, so it is a
# different, strictly harder design space.
MECHANISMS_L1 = {
    "M1_passive_sdof": PassiveSDOF,
    "M2_tuned_mass_damper": TunedMassDamper,
    "M3_sky_hook_active": LaggedSkyHook,
}


def run_episode_l1(task, arm: str, feasibility: dict, budget: int = 1500,
                   max_generations_per_mechanism: int = 200, seed: int = 0,
                   rel: float = 0.06, n_pert: int = 5, order=None) -> dict:
    """Same protocol as run_episode, evaluated at L1 and verified independently.

    Success is decided by verify_l1 with MORE perturbation samples and a finer grid
    than the searcher used, so a design that only passes the search objective does
    not count.
    """
    order = order or MECHANISM_ORDER
    spent = 0
    wasted = 0
    trace = []
    result = {"task": task.name, "arm": arm, "budget": budget, "escaped": False,
              "evals_to_success": None, "mechanism_used": None,
              "wasted": 0, "reached_feasible_mechanism": None, "trace": trace}

    for mi, mech_name in enumerate(order):
        if spent >= budget:
            break
        cannot = not bool(feasibility.get(mech_name, False))
        if result["reached_feasible_mechanism"] is None and not cannot:
            result["reached_feasible_mechanism"] = mech_name

        policy = POLICY_FACTORY[arm](task, mech_name, feasibility)
        pre_state = {"history": [], "target_T": task.T_iso, "evals": spent,
                     "mechanism": mech_name}
        if policy.should_abandon(pre_state):
            trace.append({"mechanism": mech_name, "evals": spent, "generations": 0,
                          "abandoned": True, "cannot_work": cannot,
                          "pruned_before_search": True})
            continue

        mech = MECHANISMS_L1[mech_name]()
        problem = MechanismProblemL1(task, mech, rel=rel, n_pert=n_pert,
                                     seed=seed + 7 * mi)
        search = PopulationSearch(problem, seed=seed + 101 * mi)
        spent += search.evals
        if cannot:
            wasted += search.evals
        state = {"history": list(search.history), "target_T": task.T_iso,
                 "evals": spent, "mechanism": mech_name}

        abandoned = False
        gens = 0
        while spent < budget and gens < max_generations_per_mechanism:
            used = search.generation()
            spent += used
            if cannot:
                wasted += used
            gens += 1
            state["history"] = list(search.history)
            state["evals"] = spent

            if search.best_obj >= -task.T_iso:
                v = verify_l1(mech, search.best_x, task, rel=rel)
                if v["meets_isolation_target"]:
                    result.update({"escaped": True, "evals_to_success": spent,
                                   "mechanism_used": mech_name,
                                   "final_worst_in_band_T": v["worst_in_band_T"],
                                   "wasted": wasted})
                    trace.append({"mechanism": mech_name, "evals": spent,
                                  "outcome": "success"})
                    return result

            if policy.should_abandon(state):
                abandoned = True
                break

        trace.append({"mechanism": mech_name, "evals": spent, "generations": gens,
                      "abandoned": abandoned, "cannot_work": cannot})

    result["wasted"] = wasted
    return result


def run_episode(task, arm: str, feasibility: dict, budget: int = 4000,
                max_generations_per_mechanism: int = 400, seed: int = 0,
                order=None) -> dict:
    order = order or MECHANISM_ORDER
    spent = 0
    wasted = 0
    trace = []
    result = {
        "task": task.name, "arm": arm, "budget": budget,
        "escaped": False, "evals_to_success": None,
        "mechanism_used": None, "final_in_band_T": None,
        "wasted": 0, "reached_feasible_mechanism": None,
        "trace": trace,
    }

    for mi, mech_name in enumerate(order):
        if spent >= budget:
            break
        this_mech_cannot_work = not bool(feasibility.get(mech_name, False))
        if result["reached_feasible_mechanism"] is None and not this_mech_cannot_work:
            result["reached_feasible_mechanism"] = mech_name

        # Consult the policy BEFORE constructing the searcher, because constructing
        # it evaluates an initial population.  This is the entire point of a
        # certificate: it is available a priori, at microsecond cost, so it must
        # never be preceded by any search at all.  Two earlier versions checked
        # after one generation (32 wasted evaluations) and then after construction
        # (16), each time understating the exact effect the experiment exists to
        # measure.
        policy = POLICY_FACTORY[arm](task, mech_name, feasibility)
        pre_state = {"history": [], "target_T": task.T_iso,
                     "evals": spent, "mechanism": mech_name}
        if policy.should_abandon(pre_state):
            trace.append({"mechanism": mech_name, "evals": spent, "generations": 0,
                          "abandoned": True, "cannot_work": this_mech_cannot_work,
                          "pruned_before_search": True,
                          "best_in_band_T": None, "best_constraints_ok": None})
            continue

        mech = MECHANISMS[mech_name]()
        problem = MechanismProblem(task, mech)
        search = PopulationSearch(problem, seed=seed + 101 * mi)
        spent += search.evals
        if this_mech_cannot_work:
            wasted += search.evals

        state = {"history": list(search.history), "target_T": task.T_iso,
                 "evals": spent, "mechanism": mech_name}

        abandoned = False
        gens = 0
        while spent < budget and gens < max_generations_per_mechanism:
            used = search.generation()
            spent += used
            if this_mech_cannot_work:
                wasted += used
            gens += 1
            state["history"] = list(search.history)
            state["evals"] = spent

            if search.best_obj >= -task.T_iso:
                info = search.best_feasible()
                if info is not None and info["meets_isolation_target"]:
                    result.update({
                        "escaped": True, "evals_to_success": spent,
                        "mechanism_used": mech_name,
                        "final_in_band_T": info["in_band_T"],
                        "wasted": wasted,
                    })
                    trace.append({"mechanism": mech_name, "evals": spent, "outcome": "success"})
                    return result

            if policy.should_abandon(state):
                abandoned = True
                break

        info = search.best_feasible()
        trace.append({
            "mechanism": mech_name, "evals": spent, "generations": gens,
            "abandoned": abandoned, "cannot_work": this_mech_cannot_work,
            "best_in_band_T": None if info is None else info["in_band_T"],
            "best_constraints_ok": None if info is None else info["constraints_ok"],
        })

    last = trace[-1] if trace else None
    if last is not None:
        result["final_in_band_T"] = last["best_in_band_T"]
    result["wasted"] = wasted
    return result
