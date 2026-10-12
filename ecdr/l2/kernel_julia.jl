# L2 kernel: steady-state transmissibility by TIME-DOMAIN integration.
#
# Independence claim, stated precisely
# -----------------------------------
# The L0 and L1 rungs solve the algebraic frequency-domain system
#
#     (K - w^2 M + i w C) X = (f + i w g)
#
# for a grid of w and take abs(X[payload]).  This kernel does something categorically
# different: it integrates the second-order ODE in the time domain,
#
#     M x'' + C x' + K x = f x_g + g x_g',      x_g(t) = sin(w t)
#
# until the transient has decayed, and measures the amplitude of the payload over the last
# period.  For a stable LTI system that amplitude IS the transmissibility magnitude.
#
# So this checks the ASSEMBLY of M, C, K, f, g and the frequency-domain algebra by a route
# that shares no formula with them.  It does NOT check the physical modelling: the equations
# of motion are the same author's.  That independence would need a different modelling
# paradigm, which is what the Modelica decision was for.

using DifferentialEquations
using LinearAlgebra

# Generic first-order state space driven by a unit sinusoidal ground displacement and
# its derivative.  Everything the project integrates reduces to this form, so one kernel
# serves the mechanical networks AND any hand-derived model written as an ODE.
#
#     y' = A y + B1 * x_g + B2 * x_g',      x_g(t) = sin(w t)
#
# Returns, for each omega, the largest absolute value of crow' * y over the last period -
# that is the steady-state amplitude of the chosen output for a unit-amplitude input.
function state_space_amplitude(A, B1, B2, crow, omegas; periods = 60,
                               samples_per_period = 400, reltol = 1e-11,
                               abstol = 1e-13)
    n = size(A, 1)
    out = zeros(length(omegas))
    for (k, w) in enumerate(omegas)
        Tp = 2 * pi / w
        function rhs!(dy, y, p, t)
            xg = sin(w * t)
            dxg = w * cos(w * t)
            @inbounds for i in 1:n
                s = 0.0
                for j in 1:n
                    s += A[i, j] * y[j]
                end
                dy[i] = s + B1[i] * xg + B2[i] * dxg
            end
        end
        prob = ODEProblem(rhs!, zeros(n), (0.0, periods * Tp))
        sol = solve(prob, Tsit5(); reltol = reltol, abstol = abstol, maxiters = 10^8)
        SciMLBase.successful_retcode(sol) ||
            error("integration failed at omega = " * string(w))
        ts = range((periods - 1) * Tp, periods * Tp; length = samples_per_period)
        best = 0.0
        for t in ts
            y = sol(t)
            s = 0.0
            for i in 1:n
                s += crow[i] * y[i]
            end
            v = abs(s)
            v > best && (best = v)
        end
        out[k] = best
    end
    return out
end


function transmissibility_time_domain(Mv, Cv, Kv, fv, gv, omegas; periods = 60,
                                      samples_per_period = 400, reltol = 1e-11,
                                      abstol = 1e-13)
    n = length(Mv)
    Minv = 1.0 ./ Mv
    A = zeros(2n, 2n)
    A[1:n, n+1:2n] = Matrix{Float64}(I, n, n)
    A[n+1:2n, 1:n] = -Minv .* Kv
    A[n+1:2n, n+1:2n] = -Minv .* Cv
    B1 = vcat(zeros(n), Minv .* fv)
    B2 = vcat(zeros(n), Minv .* gv)

    out = zeros(length(omegas))
    for (k, w) in enumerate(omegas)
        Tp = 2 * pi / w
        function rhs!(dy, y, p, t)
            xg = sin(w * t)
            dxg = w * cos(w * t)
            @inbounds for i in 1:2n
                s = 0.0
                for j in 1:2n
                    s += A[i, j] * y[j]
                end
                dy[i] = s + B1[i] * xg + B2[i] * dxg
            end
        end
        prob = ODEProblem(rhs!, zeros(2n), (0.0, periods * Tp))
        # maxiters matters: a long integration of a lightly damped system silently returns
        # an Interrupted solution whose values beyond the failure point are garbage.  One
        # such run produced 1.05e12 where the answer is 1.38.
        sol = solve(prob, Tsit5(); reltol = reltol, abstol = abstol, maxiters = 10^8)
        if !SciMLBase.successful_retcode(sol)
            error("integration failed at omega = " * string(w) *
                  " with retcode " * string(sol.retcode))
        end
        ts = range((periods - 1) * Tp, periods * Tp; length = samples_per_period)
        best = 0.0
        for t in ts
            v = abs(sol(t)[1])
            v > best && (best = v)
        end
        out[k] = best
    end
    return out
end
