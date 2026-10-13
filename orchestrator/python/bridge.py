"""JSON-in / JSON-out bridge from the orchestrator to the ECDR physics.

The orchestrator is TypeScript because Cordis is; the physics is Python because that is where
it was built and verified.  The process boundary is not only a convenience: the project's
discipline requires the certificate CHECKER to live in a separate code path from agent code,
and a separate process enforces that rather than relying on a convention inside one language.

Reads one JSON request from argv[1] and writes one JSON response to stdout.  Nothing else is
ever printed to stdout, so a stray print cannot corrupt the protocol.
"""
import json
import sys
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from ecdr.heat import Stream, all_match_sets, network_lp, problem_table  # noqa: E402


def _streams(spec):
    return [Stream(s["name"], float(s["t_in"]), float(s["t_out"]), float(s["cp"]))
            for s in spec]


def handle(req):
    op = req.get("op")
    if op == "min_utility":
        res = problem_table(_streams(req["streams"]), float(req["dt_min"]))
        return {"ok": True, "Q_H_min": res["Q_H_min"], "Q_C_min": res["Q_C_min"],
                "pinch_shifted_T": res["pinch_shifted_T"]}
    if op == "network":
        allowed = None
        if req.get("allowed") is not None:
            allowed = {(int(a), int(b)) for a, b in req["allowed"]}
        res = network_lp(_streams(req["streams"]), float(req["dt_min"]), allowed=allowed)
        if not res["ok"]:
            return {"ok": False, "error": res.get("message", "lp failed")}
        return {"ok": True, "Q_H": res["Q_H"], "n_pairs": res["n_pairs"],
                "n_vars": res["n_vars"]}
    if op == "search_units":
        # What networks exist below a unit budget that meet the requirement? The agent asks
        # for this; nothing here tells it what the answer means.
        sts = _streams(req["streams"])
        dt = float(req["dt_min"])
        qstar = float(req["requirement"])
        limit = int(req["max_units"])
        found = []
        for ms in all_match_sets(sts):
            n_units = len(ms)
            if n_units > limit:
                continue
            r = network_lp(sts, dt, allowed=ms)
            if r["ok"] and r["Q_H"] <= qstar + 1e-9:
                found.append({"units": n_units,
                              "matches": sorted([list(m) for m in ms]),
                              "Q_H": r["Q_H"]})
        found.sort(key=lambda z: z["units"])
        return {"ok": True, "networks": found, "count": len(found),
                "max_units_searched": limit}
    if op == "unit_check":
        # Claim: "no network using fewer than VALUE units can achieve hot utility <= Q*".
        # The checker enumerates EVERY match set. Sound iff no network with fewer than VALUE
        # units reaches Q*. A counterexample is returned when one exists, and it is a
        # concrete network, not a verdict - the agent has to work out what to do with it.
        sts = _streams(req["streams"])
        dt = float(req["dt_min"])
        qstar = float(req["requirement"])
        value = float(req["value"])
        best = None
        qualifying_min_units = None
        for ms in all_match_sets(sts):
            r = network_lp(sts, dt, allowed=ms)
            if not r["ok"]:
                continue
            n_units = len(ms)
            if r["Q_H"] <= qstar + 1e-9:
                if qualifying_min_units is None or n_units < qualifying_min_units:
                    qualifying_min_units = n_units
                if n_units < value - 1e-12:
                    if best is None or n_units < len(best["matches"]):
                        best = {"matches": sorted([list(m) for m in ms]),
                                "units": n_units, "Q_H": r["Q_H"]}
        return {"ok": True, "sound": best is None,
                "counterexample": best,
                "min_units_attaining": qualifying_min_units}
    if op == "enumerate":
        sts = _streams(req["streams"])
        dt = float(req["dt_min"])
        out = []
        for ms in all_match_sets(sts):
            r = network_lp(sts, dt, allowed=ms)
            if r["ok"]:
                out.append({"matches": sorted([list(m) for m in ms]), "Q_H": r["Q_H"]})
        return {"ok": True, "networks": out, "count": len(out)}
    return {"ok": False, "error": "unknown op: " + str(op)}


def main():
    try:
        req = json.loads(sys.argv[1])
        res = handle(req)
    except Exception as exc:                      # one boundary, one report
        res = {"ok": False, "error": type(exc).__name__ + ": " + str(exc)}
    sys.stdout.write(json.dumps(res))


if __name__ == "__main__":
    main()
