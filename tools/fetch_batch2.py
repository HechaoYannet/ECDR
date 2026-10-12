"""Batch 2 - fill the gaps batch 1 left.

Batch 1 answered "who else is doing engineering design agents".  Batch 2 has to
answer three sharper questions:
  * is the passive-isolation trade-off I derived actually classical, and where is
    the citable statement of it?  (If it is classical, the certificate is sound
    but NOT novel, and the contribution has to be its use inside an agent loop.)
  * what is the pre-LLM theory of pruning on certified conflict?
  * are there existing engineering-agent benchmarks we should plug into rather
    than invent?
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from arxiv import run_batch  # noqa: E402

QUERIES = {
    # C. performance limitations: is the trade-off classical?
    "C2b_performance_limitations_control":
        'abs:"performance limitations" AND (abs:"feedback" OR abs:"control")',
    "C2c_vibration_isolation_tradeoff":
        'abs:"vibration isolation" AND (abs:"trade-off" OR abs:"tradeoff" OR abs:"limitation")',
    "C2d_skyhook_active_isolation":
        'abs:"sky-hook" OR abs:"skyhook"',
    "C2e_bode_integral_waterbed":
        'abs:"Bode integral" OR abs:"waterbed effect" OR abs:"sensitivity integral"',

    # F. the pre-LLM theory of pruning on conflict
    "F1_minimal_unsatisfiable_subset":
        'abs:"minimal unsatisfiable subset" OR abs:"minimal unsatisfiable core"',
    "F2_conflict_directed_backjumping":
        'abs:"conflict-directed" AND abs:"backjumping"',
    "F3_explain_reduce_conflict":
        'abs:"explanation" AND abs:"constraint" AND abs:"unsatisfiable"',

    # G. engineering-agent benchmarks and representations
    "G1_llm_agent_engineering_benchmark":
        'abs:"benchmark" AND abs:"engineering design" AND abs:"language model"',
    "G2_engineering_design_optimization_llm":
        'abs:"topology optimization" AND abs:"language model"',
    "G3_mechanism_representation_design":
        'abs:"design structure" OR abs:"function structure" AND abs:"design synthesis"',

    # H. infeasibility and impossibility inside learning/agent loops
    "H1_impossibility_learning_agent":
        'abs:"impossibility" AND abs:"agent" AND abs:"proof"',
    "H2_unsat_core_learning":
        'abs:"unsat core" OR abs:"conflict clause"',
}

if __name__ == "__main__":
    print("fetching batch 2 ...")
    run_batch(QUERIES, max_results=25)
    print("done")
