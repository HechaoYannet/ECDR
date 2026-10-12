"""Install the Julia side of L2.  Run once; safe to re-run."""

from juliacall import Main as jl

print("julia", jl.VERSION, flush=True)
jl.seval("import Pkg")
print("adding DifferentialEquations ...", flush=True)
jl.seval('Pkg.add("DifferentialEquations")')
print("loading ...", flush=True)
jl.seval("using DifferentialEquations")
print("DE_LOAD_OK", flush=True)
