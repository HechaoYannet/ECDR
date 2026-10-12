model SdofIso
  "Base-excited single-degree-of-freedom isolator, built from MSL translational components.

   The point of this model is that it does NOT contain the equations of motion.  It declares
   a mass, a spring, a damper and a moving ground, and connects them; the tool assembles the
   equations.  That is what makes it a check on the MODELLING rather than on the numerics."
  import Modelica.Mechanics.Translational;

  parameter Real A = 1.0 "ground displacement amplitude [m]";
  parameter Real w = 62.83185307179586 "excitation frequency [rad/s]";
  parameter Real m_p = 1.0 "payload mass [kg]";
  parameter Real k_s = 9806.94 "support stiffness [N/m]";
  parameter Real c_s = 107.47 "support damping [N.s/m]";

  Translational.Sources.Position gnd(exact = true);
  Translational.Components.Mass payload(m = m_p,
    s(fixed = true, start = 0), v(fixed = true, start = 0));
  Translational.Components.Spring spring(c = k_s, s_rel0 = 0);
  Translational.Components.Damper damper(d = c_s);

  Real x_payload "payload displacement [m]";
  Real x_ground "ground displacement [m]";
equation
  gnd.s_ref = A * sin(w * time);
  connect(gnd.flange, spring.flange_a);
  connect(gnd.flange, damper.flange_a);
  connect(spring.flange_b, payload.flange_a);
  connect(damper.flange_b, payload.flange_a);
  x_payload = payload.s;
  x_ground = gnd.s_ref;
end SdofIso;
