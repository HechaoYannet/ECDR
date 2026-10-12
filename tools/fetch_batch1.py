"""Batch 1 - the five literature themes that decide Q1 and Q2."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from arxiv import run_batch  # noqa: E402

QUERIES = {
    # A. the validated agent strength zone: search against a formal verifier
    "A1_proof_repair_lean":
        'abs:"Lean" AND abs:"proof" AND abs:"agent"',
    "A2_subgoal_decomposition_proving":
        'abs:"subgoal" AND abs:"theorem proving" AND abs:"language model"',
    "A3_critic_pruning_search":
        'abs:"search" AND abs:"verifier" AND abs:"language model" AND abs:"prune"',

    # B. candidate generation and pruning in open-ended search
    "B1_alphaevolve_funsearch":
        'all:"AlphaEvolve" OR all:"FunSearch" OR all:"evolutionary search" AND abs:"large language model"',
    "B2_quality_diversity_llm":
        'abs:"quality-diversity" AND abs:"large language model"',
    "B3_llm_scientific_discovery_hypothesis":
        'abs:"hypothesis" AND abs:"large language model" AND abs:"scientific discovery"',

    # C. infeasibility / fundamental limits / certificates
    "C1_infeasibility_certificate":
        'abs:"infeasibility" AND abs:"certificate"',
    "C2_fundamental_limits_vibration_isolation":
        'abs:"vibration isolation" AND (abs:"fundamental limit" OR abs:"trade-off" OR abs:"Bode")',

    # D. direct competitors: engineering design agents with physics
    "D1_engineering_design_agent_physics":
        'abs:"engineering design" AND abs:"agent" AND abs:"physics"',
    "D2_cad_llm_agent":
        'abs:"CAD" AND abs:"large language model" AND abs:"design"',

    # E. mechanism switching / design space revision
    "E1_design_space_adaptation":
        'abs:"design space" AND abs:"agent" AND (abs:"adapt" OR abs:"expand" OR abs:"restructure")',
    "E2_design_fixation_llm":
        'abs:"design fixation" OR abs:"creative ideation" AND abs:"large language model"',
}

if __name__ == "__main__":
    print("fetching batch 1 ...")
    run_batch(QUERIES, max_results=30)
    print("done")
