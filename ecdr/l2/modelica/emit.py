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
               stop_time=None, periods: float = 40.0, linear: bool = True,
               f_crit: float = 100000.0) -> str:
    """Modelica source for a base-excited structure.

    linear=True (the default) emits a form suitable for omc's linearize: an explicit
    RealInput and RealOutput, and a Position source with exact = false.

    exact = true imposes flange.s = s_ref as a CONSTRAINT, and omc then dumps B = 0 with a
    transfer function of 1 at every frequency - the silent failure of Finding 032.  The
    non-exact source is a second-order Bessel filter whose critical frequency is placed far
    above the band of interest.  linear=False reproduces the original time-domain form.
    """
    if stop_time is None:
        stop_time = periods * 2.0 * np.pi / omega

    L = []
    L.append("model " + name)
    L.append('  "Base-excited mechanical network emitted from ecdr.structure.')
    L.append('   Declarations only: no equations of motion appear anywhere in this file."')
    L.append("  import Modelica.Mechanics.Translational;")
    L.append("")
    if linear:
        L.append("  Modelica.Blocks.Interfaces.RealInput u;")
        L.append("  Modelica.Blocks.Interfaces.RealOutput y;")
    else:
        L.append("  parameter Real A = " + repr(float(amplitude)) + ";")
        L.append("  parameter Real w = " + repr(float(omega)) + ";")
    L.append("")
    if linear:
        L.append("  Translational.Sources.Position gnd(exact = false, f_crit = "
                 + repr(float(f_crit)) + ");")
    else:
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
    if not linear:
        L.append("  Real x_payload;")
    L.append("equation")
    if linear:
        L.append("  gnd.s_ref = u;")
    else:
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

    if linear:
        L.append("  y = mass0.s;")
    else:
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


def emit_skyhook_model(omega_n: float, zeta: float, bandwidth: float, omega: float,
                       name: str = "Sky", mass: float = 1.0) -> str:
    """Modelica for the L1 lagged sky-hook, from MSL blocks and translational components.

    The commanded force is -c_sky * v through a first-order lag, applied to the payload by a
    Force source.  No differentiator appears anywhere: v is a state of the translational
    domain, which is exactly why a component-based model is a check on the MODELLING - the
    file states what is connected, not what the equations are.

    omega is accepted so that the signature matches emit_model, but the frequency is carried
    by the input u; the model is linear and its response is evaluated by linearization.

    The explicit RealInput and RealOutputs exist so omc's linearize can pick them up.
    """
    c_sky = 2.0 * zeta * omega_n
    k = omega_n ** 2 * mass
    L = []
    L.append("model " + name)
    L.append('  "L1 lagged sky-hook: ideal sky-hook damping through a first-order lag."')
    L.append("  import Modelica.Mechanics.Translational;")
    L.append("")
    L.append("  parameter Real m_p = " + repr(float(mass)) + ";")
    L.append("  parameter Real k_s = " + repr(float(k)) + ";")
    L.append("  parameter Real c_sky = " + repr(float(c_sky)) + ";")
    L.append("  parameter Real w_a = " + repr(float(bandwidth)) + ";")
    L.append("")
    L.append("  Modelica.Blocks.Interfaces.RealInput u;")
    L.append("  Modelica.Blocks.Interfaces.RealOutput y;")
    L.append("  Modelica.Blocks.Interfaces.RealOutput yF;")
    L.append("")
    L.append("  Translational.Sources.Position gnd(exact = false, f_crit = 100000.0);")
    L.append("  Translational.Components.Mass payload(m = m_p,")
    L.append("    s(fixed = true, start = 0), v(fixed = true, start = 0));")
    L.append("  Translational.Components.Spring support(c = k_s, s_rel0 = 0);")
    L.append("  Translational.Sources.Force actuator(useSupport = false);")
    L.append("  Modelica.Blocks.Math.Gain gain(k = -c_sky);")
    L.append("  Modelica.Blocks.Continuous.FirstOrder lag(k = 1, T = 1 / w_a, y_start = 0);")
    L.append("equation")
    L.append("  gnd.s_ref = u;")
    L.append("  connect(gnd.flange, support.flange_a);")
    L.append("  connect(support.flange_b, payload.flange_a);")
    L.append("  connect(actuator.flange, payload.flange_a);")
    # payload.v is a Real VARIABLE, not a connector, so it is wired with an equation.
    # connect(payload.v, gain.u) fails with "payload.v is not a valid connector".
    L.append("  gain.u = payload.v;")
    L.append("  connect(gain.y, lag.u);")
    L.append("  actuator.f = lag.y;")
    L.append("  y = payload.s;")
    L.append("  yF = lag.y;")
    L.append("end " + name + ";")
    return "\n".join(L) + "\n"

