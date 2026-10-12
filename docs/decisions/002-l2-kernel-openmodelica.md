# Decision 002 - L2 kernel: OpenModelica

Date: 2026-10-12 (this session).  Decided by the user.

## Decision

The L2 rung uses **OpenModelica**.

## Why this is the right kind of choice

L2 exists to be INDEPENDENT.  docs/decisions/001 already stated the principle: a
second implementation by the same author is not independent validation.  L0 and L1 are
both Python on the SciPy stack, sharing models and numerical machinery, so neither can
serve as the other's independent check.  OpenModelica is a different lineage - a
different language (Modelica), a different compiler, a different integrator suite -
which is what independence actually requires.

It also matches the stated goal of industrial-scale applied-physics systems, where
Modelica is an established tool for multi-domain plant modelling rather than a
research convenience.

## Consequences to work out

1. **Interface.**  The design description must cross a language boundary: the
   structural object S (component inventory, topology, boundary relations) has to be
   emitted as a Modelica model.  This is a real piece of work and it constrains how S
   is represented - a representation that cannot be emitted as a Modelica model is
   the wrong representation.
2. **Cost accounting.**  OpenModelica compile plus simulate time is the natural L2 cost
   unit, and it is much larger than an L0 evaluation.  That is a feature for the
   crossing-curve experiment, because it makes the fidelity ladder a genuine cost
   ladder.
3. **Reproducibility.**  Pin the OpenModelica version and hash it into the run manifest
   (Finding 003, integrity rule 6).
4. **Not yet started.**  L2 does not exist in the repository.  This record fixes the
   choice, not the implementation.
