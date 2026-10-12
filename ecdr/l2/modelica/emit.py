"""Emit a Modelica model for an arbitrary structure from ecdr.structure.

This is roadmap item (3): the structure representation must be emittable as a Modelica model,
because if it cannot, L2 is a second Python model and not independent.

The emitter writes DECLARATIONS AND CONNECTIONS, never equations of motion.  Each node
becomes an MSL Mass, each edge a Spring and a Damper in parallel, each ground tie a Spring
and a Damper to a Position source that prescribes the ground motion.  The tool assembles the
equations from the component definitions.

Flange convention: an MSL Translational Mass is a node - both its flanges sit at the same
position - so every element incident on node i is connected to mass_i.flange_a.  flange_b is
left unconnected, which MSL reads as zero force.
"""
from __future__ import annotations

import numpy as np


def emit_model(structure, omega: float, name: str = "Net", amplitude: float = 1.0,
               stop_time=None, periods: float = 40.0) -> str:
    """Modelica source for a base-excited structure at a single frequency."""
    if stop_time is None:
        stop_time = periods * 2.0 * np.pi / omega

    L = []
    L.append("model " + name)
    L.append('  "Base-excited mechanical network emitted from ecdr.structure.')
    L.append('   Declarations only: no equations of motion appear anywhere in this file."')
    L.append("  import Modelica.Mechanics.Translational;")
    L.append("")
    L.append("  parameter Real A = " + repr(float(amplitude)) + ";")
    L.append("  parameter Real w = " + repr(float(omega)) + ";")
    L.append("")
    L.append("  Translational.Sources.Position gnd(exact = true);")
    L.append("")

    for i, m in enumerate(np.asarray(structure.masses, dtype=float)):
        L.append("  Translational.Components.Mass mass" + str(i) + "(m = " + repr(float(m))
                 + ", s(fixed = true, start = 0), v(fixed = true, start = 0));")

    L.append("")
    for (i, j), k in structure.springs.items():
        tag = str(i) + "_" + str(j)
        L.append("  Translational.Components.Spring spr" + tag + "(c = " + repr(float(k))
                 + ", s_rel0 = 0);")
        L.append("  Translational.Components.Damper dmp" + tag + "(d = "
                 + repr(float(structure.dampers[(i, j)])) + ");")

    L.append("")
    for g, k in structure.ground_k.items():
        L.append("  Translational.Components.Spring sprg" + str(g) + "(c = " + repr(float(k))
                 + ", s_rel0 = 0);")
        L.append("  Translational.Components.Damper dmpg" + str(g) + "(d = "
                 + repr(float(structure.ground_c.get(g, 0.0))) + ");")

    L.append("")
    L.append("  Real x_payload;")
    L.append("equation")
    L.append("  gnd.s_ref = A * sin(w * time);")

    for (i, j) in structure.springs:
        tag = str(i) + "_" + str(j)
        L.append("  connect(mass" + str(i) + ".flange_a, spr" + tag + ".flange_a);")
        L.append("  connect(spr" + tag + ".flange_b, mass" + str(j) + ".flange_a);")
        L.append("  connect(mass" + str(i) + ".flange_a, dmp" + tag + ".flange_a);")
        L.append("  connect(dmp" + tag + ".flange_b, mass" + str(j) + ".flange_a);")

    for g in structure.ground_k:
        L.append("  connect(gnd.flange, sprg" + str(g) + ".flange_a);")
        L.append("  connect(sprg" + str(g) + ".flange_b, mass" + str(g) + ".flange_a);")
        L.append("  connect(gnd.flange, dmpg" + str(g) + ".flange_a);")
        L.append("  connect(dmpg" + str(g) + ".flange_b, mass" + str(g) + ".flange_a);")

    L.append("  x_payload = mass0.s;")
    L.append("end " + name + ";")
    return "\n".join(L) + "\n"


def emit_mos(name: str, stop_time: float, intervals: int = 4000,
             tolerance: float = 1e-8) -> str:
    return "\n".join([
        "loadModel(Modelica);",
        "getErrorString();",
        'loadFile("' + name + '.mo");',
        "getErrorString();",
        "simulate(" + name + ", startTime = 0, stopTime = " + repr(float(stop_time))
        + ", numberOfIntervals = " + str(int(intervals))
        + ', outputFormat = "csv", tolerance = ' + repr(float(tolerance)) + ");",
        "getErrorString();",
        "",
    ])
