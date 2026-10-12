"""Step 66 - THE ECDR QUESTION, in a domain we did not author.

The vibration work is ours end to end, so it can show the theory stands up but not that the
method works.  This runs the actual question on heat-exchanger networks:

    requirement   hot utility <= Q*
    structure S   a set of allowed matches between hot and cold streams
    delta(S)      the shortfall of the best achievable utility under S
    CERTIFICATE   Q_H_min, computed from the STREAM DATA alone

Four things are measured, and they are the four the whole project rests on.
"""
import _bootstrap  # noqa: F401
import json
import pathlib

import numpy as np

from ecdr.heat import Stream, all_match_sets, network_lp, problem_table

line = "=" * 100
print(line)
print("M6: the capability-gap question on heat-exchanger networks")
print(line)

CASES = {
    "4-stream": [Stream("H1", 150.0, 60.0, 2.0), Stream("H2", 90.0, 60.0, 8.0),
                 Stream("C1", 20.0, 125.0, 2.5), Stream("C2", 100.0, 150.0, 3.0)],
    "2x2": [Stream("H1", 200.0, 100.0, 3.0), Stream("H2", 150.0, 80.0, 4.0),
            Stream("C1", 60.0, 180.0, 3.0), Stream("C2", 90.0, 160.0, 4.0)],
    "3x2": [Stream("H1", 220.0, 90.0, 2.0), Stream("H2", 170.0, 70.0, 3.0),
            Stream("H3", 130.0, 60.0, 4.0),
            Stream("C1", 40.0, 190.0, 2.5), Stream("C2", 80.0, 150.0, 3.5)],
}

rows = []
for tag, sts in CASES.items():
    dt_min = 10.0
    cert = problem_table(sts, dt_min)["Q_H_min"]
    full = network_lp(sts, dt_min)
    print()
    print("  " + tag + "   dt_min = " + format(dt_min, ".3g") + " C")
    print("    certificate  Q_H_min (problem table) : " + format(cert, ".8f"))
    print("    network LP, ALL matches allowed      : " + format(full["Q_H"], ".8f")
          + "   pairs = " + str(full["n_pairs"]))
    print("    difference                           : "
          + format(abs(full["Q_H"] - cert), ".3e"))

    best = np.inf
    best_set = None
    n_sets = 0
    for ms in all_match_sets(sts):
        r = network_lp(sts, dt_min, allowed=ms)
        if not r["ok"]:
            continue
        n_sets += 1
        if r["Q_H"] < best:
            best, best_set = r["Q_H"], ms
    print("    enumerating EVERY match set          : " + str(n_sets) + " networks")
    print("    best utility any network achieves    : " + format(best, ".8f"))
    print("    best == certificate                  : " + str(abs(best - cert) < 1e-6))

    qstar = 0.9 * cert
    print("    requirement Q* = 0.9 x Q_H_min       : " + format(qstar, ".4f"))
    print("    certificate rules it out             : " + str(cert > qstar))
    print("    best network meets it                : " + str(best <= qstar))
    rows.append({"case": tag, "certificate": cert, "network_all": full["Q_H"],
                 "networks_enumerated": n_sets, "best_network": float(best),
                 "Q_star": float(qstar), "certificate_rules_out": bool(cert > qstar),
                 "network_meets": bool(best <= qstar),
                 "best_matches": sorted([list(m) for m in best_set]) if best_set else None})

print()
print(line)
print("VERDICT")
print(line)
agree = all(abs(r["network_all"] - r["certificate"]) < 1e-6 for r in rows)
sound = all(r["best_network"] >= r["certificate"] - 1e-6 for r in rows)
tight = all(abs(r["best_network"] - r["certificate"]) < 1e-6 for r in rows)
# Property 4 is only testable where the certificate is POSITIVE.  A certificate of zero means
# no hot utility is needed at all, so there is no Q* below it to rule out - the case is
# VACUOUS for this property, not a failure of it.  Finding 025 met the same distinction when
# the calibration sweep drove the survivor count to zero.  Conflating the two here would have
# reported a working certificate as broken.
testable = [r for r in rows if r["certificate"] > 1e-9]
ruled = all(r["certificate_rules_out"] and not r["network_meets"] for r in testable)
print("  1. network LP reproduces the problem table (same physics) : " + str(agree))
print("  2. no enumerated network beats the certificate           : " + str(sound))
print("  3. some network ACHIEVES it, so the bound is tight       : " + str(tight))
print("  4. the certificate rules out Q* while search cannot      : " + str(ruled)
      + "   (" + str(len(testable)) + " of " + str(len(rows))
      + " cases testable; the rest have Q_H_min = 0 and are VACUOUS, not failing)")
print()
if agree and sound and tight and ruled:
    print("  This is the ECDR shape, in a domain we did not author:")
    print("    * search enumerates networks and returns the best it finds - an UPPER bound on")
    print("      what is achievable, and every failed search is equally consistent with")
    print("      'no network works' and 'I have not found it yet';")
    print("    * the certificate is computed from the STREAM DATA, does not look at a single")
    print("      network, and DECIDES the question;")
    print("    * and it is tight, so it is not merely sound-but-useless.")
else:
    print("  one of the four properties fails; do not build on this yet.")

out = pathlib.Path(__file__).resolve().parents[1] / "runs"
out.mkdir(exist_ok=True)
(out / "heat_ecdr_question.json").write_text(json.dumps({"rows": rows}, indent=1),
                                             encoding="utf-8")
print()
print("wrote runs/heat_ecdr_question.json")
