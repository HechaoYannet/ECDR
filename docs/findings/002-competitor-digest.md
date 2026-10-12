# Competitor digest: 2608.21976 vs 2605.19717

## 1. WHAT THE PAPER ACTUALLY DOES (mechanism-level)

**2608.21976 — "The AI Engineer".** Four phases under an enforced DAG ("no later phase may commence until the preceding phase satisfies its convergence criteria with ρ_p = 0"). Phase II is a **fixed pipeline, not a search over pipelines**: import OC4 reference model → design/non-design domains in FreeCAD → BESO compliance minimisation under volume fraction (binary ρ_e ∈ {x_min,1}, x_min = 1e-3) on CalculiX → parametric upscaling → PSO sizing → Zwind 2.5 time-domain verify. Design freedom = **material layout in a fixed domain + tubular cross-sections (t, D) + one horizontal scale factor** s = s₀·x, s₀ = √(P_target/P_base), vertical dimensions "strictly preserved". Member set fixed ("columns, braces, stiffeners"); configuration inherited, never chosen. Failures go to replan(θ, F_p), "a predefined set of corrective actions" over three hierarchies (geometric/meshing anomalies; numerical solver aborts; physical limit-state violations). "Irrecoverable constraint conflicts invoke high-level design-domain backtracking" — of the *topology design domain*, not the physical mechanism. **Mechanism class is constant: a passive steel semi-submersible.**

**2605.19717 — "Physics-in-the-Loop".** LangGraph, four agents (Planner, CAD Engineer, Geometry Reviewer, Structural Reviewer), loop Generate–Simulate–Refine, **max 10 iterations**. Action space = CadQuery Python → B-Rep solid inside a fixed design domain. Physics constant (torch-fem linear static FEA, tet4, Aluminium 8081); objective constant (min volume s.t. safety factor 2.0–5.0). The Planner decomposes into a *modelling* plan, not a physical problem decomposition. **Only geometry varies.**

## 2. THE PRECISE EVIDENCE

**2608.** 20 MW FOWT foundation vs "TuQiang" human baseline (200+ researchers, 2 years): steel 255.5 vs 278 t·MW⁻¹ (−8.1%); capital cost ¥18,197 vs ¥19,800 kW⁻¹ (−8.1%). Certificate: single top-scoring candidate (S = 91, grade A) → **one** CCS AIP submission, 4-stage workflow, **three rounds of formal clarification requests**; "After iterative exchanges and **design refinements**, the candidate successfully passed all review items" — the certified artifact is not the as-generated one. Gate validated on **n = 1**. Reviewer vs an independent regulatory channel over **11 reference projects**: Spearman **ρ_S = 0.717**, MAD **3.9** points, high-agreement **89%** (both ≥60, |Δ| ≤15). Threshold S ≥ 85 = **90th percentile** of regulator-passed projects; weights [0.15, 0.30, 0.25, 0.15, 0.15]. Reviewer costs **2–5 min/candidate**, "purely analytical… without invoking any finite-element or time-domain simulations". PSO fixed at n = 100 generations. **No orchestrator ablation; "All flagship metrics are from single deterministic solver runs".**

**2605.** 20 load cases × 5 geometric scales × 5 force scales = **500 configurations**; 4 VLMs; 3 runs each; temp 0.5; context cleared per run. Execution/meshing/FEA success 96.4–97.5% / 76.3–88.2% / 81.3–86.8%. Safety factor 4.04–4.97, all near the upper limit 5.0 (over-engineering); design-space violation rate 8.7–85.7%. **Headline ablation:** FEA feedback on 49/83 = 59.0% inside target SF range vs off 6/27 = 22.2%, Fisher exact p < 0.01. Planning ablation: iterations 6.0/10.4 (Opus), 4.5/13.0 (Sonnet), Welch t-test. Topology optimisation is faster: 18.6 ± 1.2 s vs their 28.7 ± 36.9 s.

## 3. STATED AND IMPLIED LIMITATIONS

**2608, five stated items:** (1) only the top branch advanced to AIP — "The system's ability to consistently produce near-competitive designs—rather than its success rate in generating any feasible solution—must improve"; wants "more sophisticated replanning policies"; (2) extreme hydrodynamics need wave-basin/CFD — "The current framework cannot autonomously orchestrate such experimental setups"; (3) fabrication "prompt-approximated rather than CAD-CAM exact"; "Detailed design and construction remain entirely human responsibilities"; (4) LLM stochasticity → "multi-seed campaigns and strictly frozen tool schemas"; (5) "TuQiang" is a moving baseline. *Implied:* AIP is concept-level only; ρ = 0.717 leaves ~half the rank variance unexplained, so the gate is a fitted surrogate, not a proof; no ablation separating the LLM orchestrator from the deterministic pipeline; domain transfer ≈ three person-months; "verification-closed" is self-declared — deliberately **not** open-ended.

**2605:** §9.2 — "with more iterations, the results tend to become more unstable. Future work could focus on detecting stopping criteria when a CAD design becomes **unrecoverable**". §9.4 — "there are no directly comparable prior works". Conclusion — dynamics, thermal, material selection, manufacturability, cost all future work. Opus hit the iteration cap 16.3%, Sonnet 12.8%.

## 4. WHAT IT MEANS FOR ECDR

**Closed off.** Closed-loop physics feedback (both); "verification-closed regime" (2608); deterministic multi-solver orchestration; the cheap-gate / expensive-validator cascade; audit trails; "expanding the search space" as a slogan (2608: "The creative breakthrough lies in expanding the search space through BESO topology evolution and parameterized upscaling"); an external certificate validating an internal gate.

**Remains open — five claims, strongest first.**

**C1 — Certified infeasibility as a first-class action.** Both terminate on *sufficiency*: 2608 needs ρ_p = 0, PSO n = 100, S ≥ 85 with no sub-score < 60; 2605 needs all checks to pass within 10 iterations. Neither represents "this design space cannot succeed"; 2608's recovery is a lookup table, and 2605 names the gap verbatim ("unrecoverable"). ECDR's Λ = 0.2903 (bounds incompatible by a factor **3.445**) is a statement about *(mechanism, task)*, not a score about a candidate. Claim: first design agent whose route abandonment is triggered by a machine-checkable certificate rather than a threshold.

**C2 — Certificate independence.** 2608's gate is *fitted* to regulatory outcomes (ρ = 0.717 over 11 projects), validated on n = 1, and the certified artifact was revised during review. Λ is invariant to budget, search history and objective weights.

**C3 — Mechanism-class change as a distinct action.** Both action spaces are geometry/parameter-only. M1→M3 changes the transfer function's *structure* (feedthrough term present → absent), changing the achievable set, not just the optimum. Claim: first benchmark where the escaping action is provably outside the initial design space.

**C4 — Ground-truth escape ladder.** M1 provably infeasible (Λ = 0.2903); M2 not feasible in the scanned family (best in-band |T| = 0.3044 vs limit 0.1, 331,776 combinations); M3 feasible with an explicit witness (ω_n = 113.06, ζ = 2, in-band |T| = 0.0770, peak 1.0000). Neither paper has a task with *proven* infeasibility of the initial class.

**C5 — Non-monotonic search, evidence-gated pruning, diagnosis accuracy against injected ground truth.** 2608 archives alternatives but never prunes on evidence and scores no diagnosis; 2605 has no branch memory. Weak as novelty, strong as a measured ablation.

**Must not do:** position as physics-in-the-loop or verification-closed; compete on industrial scale (2608 holds a real CCS AIP and 8.1% on a real machine); use "certifiable" without distinguishing certificate types; headline "expanding the search space".

## 5. CONCRETE INGREDIENTS WORTH BORROWING

1. **Two-stage cost cascade + cost ledger.** 2608's internal gate is purely analytical at 2–5 min/candidate, no FEA. Map: Λ certificate (microseconds) = L0 screen; L1 nonlinear sim = daily gate; L2 independent validator = one-off gold standard.
2. **Composite-with-floor scoring.** S ≥ 85 AND no sub-score < 60 — a violated hard constraint is never traded for gains elsewhere. Give ECDR's task scoring the same AND structure.
3. **Percentile-calibrated thresholds.** S = 85 is the 90th percentile of regulator-passed projects. Analogously, calibrate any ECDR escape-readiness score against analytic Λ, not against other agents.
4. **Falsification as a standing artifact.** ECDR already has one (260k-point brute force over (ω_n, ζ) on 7 tasks; closed-form vs numerical root to 5.5e-14; peak attainment 1.6e-09). Ship it re-runnable — a rigor axis 2608 cannot match.
5. **Quote replan(θ, F_p) as the baseline, then add a fourth hierarchy.** Replace the "predefined set of corrective actions" with an evidence-gated selector whose fourth failure class is mechanism-class infeasibility.
6. **Ablation shape from 2605.** Disable one component, hold everything else, report a contingency test (59.0% vs 22.2%, p < 0.01). ECDR headline: disable the certificate, keep the *identical* mechanism library and budget → does escape still happen? Isolates "evidence" from "more options".
7. **Epistemic-variance protocol + audit trail.** Frozen tool schemas, pinned versions, multi-seed campaigns, low temperature; SHA-256 manifests and streamed structured logs.
8. **The sentence to quote back.** 2608: "Unlike open-ended generative AI systems…" — they explicitly chose closed. That is the boundary ECDR crosses.
