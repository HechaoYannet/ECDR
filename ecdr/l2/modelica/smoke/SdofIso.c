/* Main Simulation File */

#if defined(__cplusplus)
extern "C" {
#endif

#include "SdofIso_model.h"
#include "simulation/solver/events.h"
#include "simulation/arrayIndex.h"

/* FIXME these defines are ugly and hard to read, why not use direct function pointers instead? */
#define prefixedName_performSimulation SdofIso_performSimulation
#define prefixedName_updateContinuousSystem SdofIso_updateContinuousSystem
#include <simulation/solver/perform_simulation.c.inc>

#define prefixedName_performQSSSimulation SdofIso_performQSSSimulation
#include <simulation/solver/perform_qss_simulation.c.inc>


/* dummy VARINFO and FILEINFO */
const VAR_INFO dummyVAR_INFO = omc_dummyVarInfo;

int SdofIso_input_function(DATA *data, threadData_t *threadData)
{
  
  return 0;
}

int SdofIso_input_function_init(DATA *data, threadData_t *threadData)
{
  
  return 0;
}

int SdofIso_input_function_updateStartValues(DATA *data, threadData_t *threadData)
{
  
  return 0;
}

int SdofIso_inputNames(DATA *data, char ** names){
  
  return 0;
}

int SdofIso_data_function(DATA *data, threadData_t *threadData)
{
  return 0;
}

int SdofIso_dataReconciliationInputNames(DATA *data, char ** names){
  
  return 0;
}

int SdofIso_dataReconciliationUnmeasuredVariables(DATA *data, char ** names)
{
  
  return 0;
}

int SdofIso_output_function(DATA *data, threadData_t *threadData)
{
  
  return 0;
}

int SdofIso_setc_function(DATA *data, threadData_t *threadData)
{
  
  return 0;
}

int SdofIso_setb_function(DATA *data, threadData_t *threadData)
{
  
  return 0;
}


/*
equation index: 27
type: SIMPLE_ASSIGN
spring.s_rel = damper.s_rel
*/
void SdofIso_eqFunction_27(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,27};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[26]] /* spring.s_rel variable */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[0]] /* damper.s_rel STATE(1,damper.v_rel) */);
  threadData->lastEquationSolved = 27;
}

/*
equation index: 28
type: SIMPLE_ASSIGN
spring.f = spring.c * (damper.s_rel - spring.s_rel0)
*/
void SdofIso_eqFunction_28(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,28};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[25]] /* spring.f variable */) = ((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[10]] /* spring.c PARAM */)) * ((data->localData[0]->realVars[data->simulationInfo->realVarsIndex[0]] /* damper.s_rel STATE(1,damper.v_rel) */) - (data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[11]] /* spring.s_rel0 PARAM */));
  threadData->lastEquationSolved = 28;
}

/*
equation index: 29
type: SIMPLE_ASSIGN
damper.f = damper.d * damper.v_rel
*/
void SdofIso_eqFunction_29(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,29};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[12]] /* damper.f variable */) = ((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[2]] /* damper.d PARAM */)) * ((data->localData[0]->realVars[data->simulationInfo->realVarsIndex[1]] /* damper.v_rel STATE(1) */));
  threadData->lastEquationSolved = 29;
}

/*
equation index: 30
type: SIMPLE_ASSIGN
damper.lossPower = damper.f * damper.v_rel
*/
void SdofIso_eqFunction_30(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,30};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[14]] /* damper.lossPower variable */) = ((data->localData[0]->realVars[data->simulationInfo->realVarsIndex[12]] /* damper.f variable */)) * ((data->localData[0]->realVars[data->simulationInfo->realVarsIndex[1]] /* damper.v_rel STATE(1) */));
  threadData->lastEquationSolved = 30;
}

/*
equation index: 31
type: SIMPLE_ASSIGN
gnd.flange.f = damper.f + spring.f
*/
void SdofIso_eqFunction_31(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,31};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[16]] /* gnd.flange.f variable */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[12]] /* damper.f variable */) + (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[25]] /* spring.f variable */);
  threadData->lastEquationSolved = 31;
}

/*
equation index: 32
type: SIMPLE_ASSIGN
payload.a = (-gnd.flange.f) / payload.m
*/
void SdofIso_eqFunction_32(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,32};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[19]] /* payload.a variable */) = DIVISION_SIM((-(data->localData[0]->realVars[data->simulationInfo->realVarsIndex[16]] /* gnd.flange.f variable */)),(data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[9]] /* payload.m PARAM */),"payload.m",equationIndexes);
  threadData->lastEquationSolved = 32;
}

/*
equation index: 33
type: SIMPLE_ASSIGN
$DER.payload.v = payload.a
*/
void SdofIso_eqFunction_33(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,33};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[8]] /* der(payload.v) DUMMY_DER */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[19]] /* payload.a variable */);
  threadData->lastEquationSolved = 33;
}

/*
equation index: 34
type: SIMPLE_ASSIGN
$DER.$DER.damper.flange_b.s = payload.a
*/
void SdofIso_eqFunction_34(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,34};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[4]] /* der(der(damper.flange_b.s)) DUMMY_DER */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[19]] /* payload.a variable */);
  threadData->lastEquationSolved = 34;
}

/*
equation index: 35
type: SIMPLE_ASSIGN
payload.flange_a.f = -gnd.flange.f
*/
void SdofIso_eqFunction_35(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,35};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[20]] /* payload.flange_a.f variable */) = (-(data->localData[0]->realVars[data->simulationInfo->realVarsIndex[16]] /* gnd.flange.f variable */));
  threadData->lastEquationSolved = 35;
}

/*
equation index: 36
type: SIMPLE_ASSIGN
$DER.damper.s_rel = damper.v_rel
*/
void SdofIso_eqFunction_36(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,36};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[2]] /* der(damper.s_rel) STATE_DER */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[1]] /* damper.v_rel STATE(1) */);
  threadData->lastEquationSolved = 36;
}

/*
equation index: 37
type: SIMPLE_ASSIGN
$cse2 = cos(w * time)
*/
void SdofIso_eqFunction_37(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,37};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[11]] /* $cse2 variable */) = cos(((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[12]] /* w PARAM */)) * (data->localData[0]->timeValue));
  threadData->lastEquationSolved = 37;
}

/*
equation index: 38
type: SIMPLE_ASSIGN
$DER.x_ground = A * $cse2 * w
*/
void SdofIso_eqFunction_38(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,38};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[9]] /* der(x_ground) DUMMY_DER */) = ((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[0]] /* A PARAM */)) * (((data->localData[0]->realVars[data->simulationInfo->realVarsIndex[11]] /* $cse2 variable */)) * ((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[12]] /* w PARAM */)));
  threadData->lastEquationSolved = 38;
}

/*
equation index: 39
type: SIMPLE_ASSIGN
payload.v = $DER.x_ground + damper.v_rel
*/
void SdofIso_eqFunction_39(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,39};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[24]] /* payload.v DUMMY_STATE */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[9]] /* der(x_ground) DUMMY_DER */) + (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[1]] /* damper.v_rel STATE(1) */);
  threadData->lastEquationSolved = 39;
}

/*
equation index: 40
type: SIMPLE_ASSIGN
$DER.damper.flange_b.s = payload.v
*/
void SdofIso_eqFunction_40(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,40};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[6]] /* der(damper.flange_b.s) DUMMY_DER */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[24]] /* payload.v DUMMY_STATE */);
  threadData->lastEquationSolved = 40;
}

/*
equation index: 41
type: SIMPLE_ASSIGN
$DER.payload.s = payload.v
*/
void SdofIso_eqFunction_41(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,41};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[7]] /* der(payload.s) DUMMY_DER */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[24]] /* payload.v DUMMY_STATE */);
  threadData->lastEquationSolved = 41;
}

/*
equation index: 42
type: SIMPLE_ASSIGN
$cse1 = sin(w * time)
*/
void SdofIso_eqFunction_42(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,42};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[10]] /* $cse1 variable */) = sin(((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[12]] /* w PARAM */)) * (data->localData[0]->timeValue));
  threadData->lastEquationSolved = 42;
}

/*
equation index: 43
type: SIMPLE_ASSIGN
x_ground = A * $cse1
*/
void SdofIso_eqFunction_43(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,43};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[27]] /* x_ground DUMMY_STATE */) = ((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[0]] /* A PARAM */)) * ((data->localData[0]->realVars[data->simulationInfo->realVarsIndex[10]] /* $cse1 variable */));
  threadData->lastEquationSolved = 43;
}

/*
equation index: 44
type: SIMPLE_ASSIGN
damper.flange_b.s = x_ground + damper.s_rel
*/
void SdofIso_eqFunction_44(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,44};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[13]] /* damper.flange_b.s DUMMY_STATE */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[27]] /* x_ground DUMMY_STATE */) + (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[0]] /* damper.s_rel STATE(1,damper.v_rel) */);
  threadData->lastEquationSolved = 44;
}

/*
equation index: 45
type: SIMPLE_ASSIGN
payload.s = damper.flange_b.s - (-0.5) * payload.L
*/
void SdofIso_eqFunction_45(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,45};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[23]] /* payload.s DUMMY_STATE */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[13]] /* damper.flange_b.s DUMMY_STATE */) - ((-0.5) * ((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[8]] /* payload.L PARAM */)));
  threadData->lastEquationSolved = 45;
}

/*
equation index: 46
type: SIMPLE_ASSIGN
payload.flange_b.s = payload.s + 0.5 * payload.L
*/
void SdofIso_eqFunction_46(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,46};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[22]] /* payload.flange_b.s variable */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[23]] /* payload.s DUMMY_STATE */) + (0.5) * ((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[8]] /* payload.L PARAM */));
  threadData->lastEquationSolved = 46;
}

/*
equation index: 47
type: SIMPLE_ASSIGN
$DER.$DER.x_ground = (-A) * $cse1 * w ^ 2.0
*/
void SdofIso_eqFunction_47(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,47};
  modelica_real tmp0;
  tmp0 = (data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[12]] /* w PARAM */);
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[5]] /* der(der(x_ground)) DUMMY_DER */) = ((-(data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[0]] /* A PARAM */))) * (((data->localData[0]->realVars[data->simulationInfo->realVarsIndex[10]] /* $cse1 variable */)) * ((tmp0 * tmp0)));
  threadData->lastEquationSolved = 47;
}

/*
equation index: 48
type: SIMPLE_ASSIGN
$DER.damper.v_rel = payload.a - $DER.$DER.x_ground
*/
void SdofIso_eqFunction_48(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,48};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[3]] /* der(damper.v_rel) STATE_DER */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[19]] /* payload.a variable */) - (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[5]] /* der(der(x_ground)) DUMMY_DER */);
  threadData->lastEquationSolved = 48;
}

OMC_DISABLE_OPT
int SdofIso_functionDAE(DATA *data, threadData_t *threadData)
{
  int equationIndexes[1] = {0};
#if !defined(OMC_MINIMAL_RUNTIME)
  if (measure_time_flag) rt_tick(SIM_TIMER_DAE);
#endif

  data->simulationInfo->needToIterate = 0;
  data->simulationInfo->discreteCall = 1;
  SdofIso_functionLocalKnownVars(data, threadData);
  static void (*const eqFunctions[22])(DATA*, threadData_t*) = {
    SdofIso_eqFunction_27,
    SdofIso_eqFunction_28,
    SdofIso_eqFunction_29,
    SdofIso_eqFunction_30,
    SdofIso_eqFunction_31,
    SdofIso_eqFunction_32,
    SdofIso_eqFunction_33,
    SdofIso_eqFunction_34,
    SdofIso_eqFunction_35,
    SdofIso_eqFunction_36,
    SdofIso_eqFunction_37,
    SdofIso_eqFunction_38,
    SdofIso_eqFunction_39,
    SdofIso_eqFunction_40,
    SdofIso_eqFunction_41,
    SdofIso_eqFunction_42,
    SdofIso_eqFunction_43,
    SdofIso_eqFunction_44,
    SdofIso_eqFunction_45,
    SdofIso_eqFunction_46,
    SdofIso_eqFunction_47,
    SdofIso_eqFunction_48
  };
  
  for (int id = 0; id < 22; id++) {
    eqFunctions[id](data, threadData);
  }
  data->simulationInfo->discreteCall = 0;
  
#if !defined(OMC_MINIMAL_RUNTIME)
  if (measure_time_flag) rt_accumulate(SIM_TIMER_DAE);
#endif
  return 0;
}


int SdofIso_functionLocalKnownVars(DATA *data, threadData_t *threadData)
{
  
  return 0;
}

/* forwarded equations */
extern void SdofIso_eqFunction_28(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_29(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_31(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_32(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_36(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_42(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_47(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_48(DATA* data, threadData_t *threadData);

static void functionODE_system0(DATA *data, threadData_t *threadData)
{
  static void (*const eqFunctions[8])(DATA*, threadData_t*) = {
    SdofIso_eqFunction_28,
    SdofIso_eqFunction_29,
    SdofIso_eqFunction_31,
    SdofIso_eqFunction_32,
    SdofIso_eqFunction_36,
    SdofIso_eqFunction_42,
    SdofIso_eqFunction_47,
    SdofIso_eqFunction_48
  };
  
  if (data->simulationInfo->evalSelection) {
    for (int i = 0; i < data->simulationInfo->evalSelection->n; i++) {
      int id = data->simulationInfo->evalSelection->idx[i];
      eqFunctions[id](data, threadData);
    }
  } else {
    for (int id = 0; id < 8; id++) {
      eqFunctions[id](data, threadData);
    }
  }
}

int SdofIso_functionODE(DATA *data, threadData_t *threadData)
{
#if !defined(OMC_MINIMAL_RUNTIME)
  if (measure_time_flag) rt_tick(SIM_TIMER_FUNCTION_ODE);
#endif

  
  data->simulationInfo->callStatistics.functionODE++;
  
  SdofIso_functionLocalKnownVars(data, threadData);
  functionODE_system0(data, threadData);

#if !defined(OMC_MINIMAL_RUNTIME)
  if (measure_time_flag) rt_accumulate(SIM_TIMER_FUNCTION_ODE);
#endif

  return 0;
}

void SdofIso_ODE_DAG(DATA* data, threadData_t* threadData)
{
  const size_t eqMap[] = {28, 29, 31, 32, 36, 42, 47, 48};
  buildEvalDAG_ODE(data->modelData, sizeof(eqMap)/sizeof(size_t), eqMap);
}

/* forward the main in the simulation runtime */
extern int _main_SimulationRuntime(int argc, char **argv, DATA *data, threadData_t *threadData);
extern int _main_OptimizationRuntime(int argc, char **argv, DATA *data, threadData_t *threadData);

#include "SdofIso_12jac.h"
#include "SdofIso_13opt.h"

struct OpenModelicaGeneratedFunctionCallbacks SdofIso_callback = {
  (int (*)(DATA *, threadData_t *, void *)) SdofIso_performSimulation,    /* performSimulation */
  (int (*)(DATA *, threadData_t *, void *)) SdofIso_performQSSSimulation,    /* performQSSSimulation */
  SdofIso_updateContinuousSystem,    /* updateContinuousSystem */
  SdofIso_callExternalObjectDestructors,    /* callExternalObjectDestructors */
  NULL,    /* initialNonLinearSystem */
  NULL,    /* initialLinearSystem */
  NULL,    /* initialMixedSystem */
  #if !defined(OMC_NO_STATESELECTION)
  SdofIso_initializeStateSets,
  #else
  NULL,
  #endif    /* initializeStateSets */
  SdofIso_initializeDAEmodeData,
  SdofIso_ODE_DAG,
  SdofIso_functionODE,
  SdofIso_functionAlgebraics,
  SdofIso_functionDAE,
  SdofIso_functionLocalKnownVars,
  SdofIso_input_function,
  SdofIso_input_function_init,
  SdofIso_input_function_updateStartValues,
  SdofIso_data_function,
  SdofIso_output_function,
  SdofIso_setc_function,
  SdofIso_setb_function,
  SdofIso_function_storeDelayed,
  SdofIso_function_storeSpatialDistribution,
  SdofIso_function_initSpatialDistribution,
  SdofIso_updateBoundVariableAttributes,
  SdofIso_functionInitialEquations,
  GLOBAL_EQUIDISTANT_HOMOTOPY,
  NULL,
  SdofIso_functionRemovedInitialEquations,
  SdofIso_updateBoundParameters,
  SdofIso_checkForAsserts,
  SdofIso_function_ZeroCrossingsEquations,
  SdofIso_function_ZeroCrossings,
  SdofIso_function_updateRelations,
  SdofIso_zeroCrossingDescription,
  SdofIso_relationDescription,
  SdofIso_function_initSample,
  SdofIso_INDEX_JAC_A,
  SdofIso_INDEX_JAC_ADJ,
  SdofIso_INDEX_JAC_B,
  SdofIso_INDEX_JAC_C,
  SdofIso_INDEX_JAC_D,
  SdofIso_INDEX_JAC_F,
  SdofIso_INDEX_JAC_H,
  SdofIso_initialAnalyticJacobianA,
  SdofIso_initialAnalyticJacobianADJ,
  SdofIso_initialAnalyticJacobianB,
  SdofIso_initialAnalyticJacobianC,
  SdofIso_initialAnalyticJacobianD,
  SdofIso_initialAnalyticJacobianF,
  SdofIso_initialAnalyticJacobianH,
  SdofIso_functionJacA_column,
  SdofIso_functionJacADJ_column,
  SdofIso_functionJacB_column,
  SdofIso_functionJacC_column,
  SdofIso_functionJacD_column,
  SdofIso_functionJacF_column,
  SdofIso_functionJacH_column,
  SdofIso_JacA_DAG,
  SdofIso_linear_model_frame,
  SdofIso_linear_model_datarecovery_frame,
  SdofIso_mayer,
  SdofIso_lagrange,
  SdofIso_getInputVarIndicesInOptimization,
  SdofIso_pickUpBoundsForInputsInOptimization,
  SdofIso_setInputData,
  SdofIso_getTimeGrid,
  SdofIso_symbolicInlineSystem,
  SdofIso_function_initSynchronous,
  SdofIso_function_updateSynchronous,
  SdofIso_function_equationsSynchronous,
  SdofIso_inputNames,
  SdofIso_dataReconciliationInputNames,
  SdofIso_dataReconciliationUnmeasuredVariables,
  NULL,
  NULL,
  NULL,
  NULL,
  -1,
  NULL,
  NULL,
  -1

};

#define _OMC_LIT_RESOURCE_0_name_data "Complex"
#define _OMC_LIT_RESOURCE_0_dir_data "/root/.openmodelica/libraries/Complex 4.1.0+maint.om"
static const MMC_DEFSTRINGLIT(_OMC_LIT_RESOURCE_0_name,7,_OMC_LIT_RESOURCE_0_name_data);
static const MMC_DEFSTRINGLIT(_OMC_LIT_RESOURCE_0_dir,52,_OMC_LIT_RESOURCE_0_dir_data);

#define _OMC_LIT_RESOURCE_1_name_data "Modelica"
#define _OMC_LIT_RESOURCE_1_dir_data "/root/.openmodelica/libraries/Modelica 4.1.0+maint.om"
static const MMC_DEFSTRINGLIT(_OMC_LIT_RESOURCE_1_name,8,_OMC_LIT_RESOURCE_1_name_data);
static const MMC_DEFSTRINGLIT(_OMC_LIT_RESOURCE_1_dir,53,_OMC_LIT_RESOURCE_1_dir_data);

#define _OMC_LIT_RESOURCE_2_name_data "ModelicaServices"
#define _OMC_LIT_RESOURCE_2_dir_data "/root/.openmodelica/libraries/ModelicaServices 4.1.0+maint.om"
static const MMC_DEFSTRINGLIT(_OMC_LIT_RESOURCE_2_name,16,_OMC_LIT_RESOURCE_2_name_data);
static const MMC_DEFSTRINGLIT(_OMC_LIT_RESOURCE_2_dir,61,_OMC_LIT_RESOURCE_2_dir_data);

#define _OMC_LIT_RESOURCE_3_name_data "SdofIso"
#define _OMC_LIT_RESOURCE_3_dir_data "/work"
static const MMC_DEFSTRINGLIT(_OMC_LIT_RESOURCE_3_name,7,_OMC_LIT_RESOURCE_3_name_data);
static const MMC_DEFSTRINGLIT(_OMC_LIT_RESOURCE_3_dir,5,_OMC_LIT_RESOURCE_3_dir_data);

static const MMC_DEFSTRUCTLIT(_OMC_LIT_RESOURCES,8,MMC_ARRAY_TAG) {MMC_REFSTRINGLIT(_OMC_LIT_RESOURCE_0_name), MMC_REFSTRINGLIT(_OMC_LIT_RESOURCE_0_dir), MMC_REFSTRINGLIT(_OMC_LIT_RESOURCE_1_name), MMC_REFSTRINGLIT(_OMC_LIT_RESOURCE_1_dir), MMC_REFSTRINGLIT(_OMC_LIT_RESOURCE_2_name), MMC_REFSTRINGLIT(_OMC_LIT_RESOURCE_2_dir), MMC_REFSTRINGLIT(_OMC_LIT_RESOURCE_3_name), MMC_REFSTRINGLIT(_OMC_LIT_RESOURCE_3_dir)}};
void SdofIso_setupDataStruc(DATA *data, threadData_t *threadData)
{
  assertStreamPrint(threadData,0!=data, "Error while initialize Data");
  threadData->localRoots[LOCAL_ROOT_SIMULATION_DATA] = data;
  data->callback = &SdofIso_callback;
  OpenModelica_updateUriMapping(threadData, MMC_REFSTRUCTLIT(_OMC_LIT_RESOURCES));
  data->modelData->modelName = "SdofIso";
  data->modelData->modelFilePrefix = "SdofIso";
  data->modelData->modelFileName = "SdofIso.mo";
  data->modelData->resultFileName = NULL;
  data->modelData->modelDir = "/work";
  data->modelData->modelGUID = "{2f63533e-8eb3-42a3-ae61-d14c997af003}";
  #if defined(OPENMODELICA_XML_FROM_FILE_AT_RUNTIME)
  data->modelData->initXMLData = NULL;
  data->modelData->modelDataXml.infoXMLData = NULL;
  #else
  #if defined(_MSC_VER) /* handle joke compilers */
  {
  /* for MSVC we encode a string like char x[] = {'a', 'b', 'c', '\0'} */
  /* because the string constant limit is 65535 bytes */
  static const char contents_init[] =
    #include "SdofIso_init.c"
    ;
  static const char contents_info[] =
    #include "SdofIso_info.c"
    ;
    data->modelData->initXMLData = contents_init;
    data->modelData->modelDataXml.infoXMLData = contents_info;
  }
  #else /* handle real compilers */
  data->modelData->initXMLData =
  #include "SdofIso_init.c"
    ;
  data->modelData->modelDataXml.infoXMLData =
  #include "SdofIso_info.c"
    ;
  #endif /* defined(_MSC_VER) */
  #endif /* defined(OPENMODELICA_XML_FROM_FILE_AT_RUNTIME) */
  data->modelData->modelDataXml.fileName = "SdofIso_info.json";
  data->modelData->resourcesDir = NULL;
  data->modelData->runTestsuite = 0;
  data->modelData->nStatesArray = 2;
  data->modelData->nDiscreteReal = 0;
  data->modelData->nVariablesRealArray = 28;
  data->modelData->nVariablesIntegerArray = 0;
  data->modelData->nVariablesBooleanArray = 0;
  data->modelData->nVariablesStringArray = 0;
  data->modelData->nParametersRealArray = 13;
  data->modelData->nParametersIntegerArray = 2;
  data->modelData->nParametersBooleanArray = 3;
  data->modelData->nParametersStringArray = 0;
  data->modelData->nParametersReal = 13;
  data->modelData->nParametersInteger = 2;
  data->modelData->nParametersBoolean = 3;
  data->modelData->nParametersString = 0;
  data->modelData->nAliasRealArray = 12;
  data->modelData->nAliasIntegerArray = 0;
  data->modelData->nAliasBooleanArray = 0;
  data->modelData->nAliasStringArray = 0;
  data->modelData->nInputVars = 0;
  data->modelData->nOutputVars = 0;
  data->modelData->nZeroCrossings = 0;
  data->modelData->nSamples = 0;
  data->modelData->nRelations = 0;
  data->modelData->nMathEvents = 0;
  data->modelData->nExtObjs = 0;
  data->modelData->modelDataXml.modelInfoXmlLength = 0;
  data->modelData->modelDataXml.nFunctions = 0;
  data->modelData->modelDataXml.nProfileBlocks = 0;
  data->modelData->modelDataXml.nEquations = 70;
  data->modelData->nMixedSystems = 0;
  data->modelData->nLinearSystems = 0;
  data->modelData->nNonLinearSystems = 0;
  data->modelData->nStateSets = 0;
  data->modelData->nJacobians = 7;
  data->modelData->nOptimizeConstraints = 0;
  data->modelData->nOptimizeFinalConstraints = 0;
  data->modelData->nDelayExpressions = 0;
  data->modelData->nBaseClocks = 0;
  data->modelData->nSpatialDistributions = 0;
  data->modelData->nSensitivityVars = 0;
  data->modelData->nSensitivityParamVars = 0;
  data->modelData->nSetcVars = 0;
  data->modelData->ndataReconVars = 0;
  data->modelData->nSetbVars = 0;
  data->modelData->nRelatedBoundaryConditions = 0;
  data->modelData->linearizationDumpLanguage = OMC_LINEARIZE_DUMP_LANGUAGE_MODELICA;
}

static int rml_execution_failed()
{
  fflush(NULL);
  fprintf(stderr, "Execution failed!\n");
  fflush(NULL);
  return 1;
}


#if defined(__MINGW32__) || defined(_MSC_VER)

#if !defined(_UNICODE)
#define _UNICODE
#endif
#if !defined(UNICODE)
#define UNICODE
#endif

#include <windows.h>
char** omc_fixWindowsArgv(int argc, wchar_t **wargv)
{
  char** newargv;
  /* Support for non-ASCII characters
  * Read the unicode command line arguments and translate it to char*
  */
  newargv = (char**)malloc(argc*sizeof(char*));
  for (int i = 0; i < argc; i++) {
    newargv[i] = omc_wchar_to_multibyte_str(wargv[i]);
  }
  return newargv;
}

#define OMC_MAIN wmain
#define OMC_CHAR wchar_t
#define OMC_EXPORT __declspec(dllexport) extern

#else
#define omc_fixWindowsArgv(N, A) (A)
#define OMC_MAIN main
#define OMC_CHAR char
#define OMC_EXPORT extern
#endif

#if defined(threadData)
#undef threadData
#endif
/* call the simulation runtime main from our main! */
#if defined(OMC_DLL_MAIN_DEFINE)
OMC_EXPORT int omcDllMain(int argc, OMC_CHAR **argv)
#else
int OMC_MAIN(int argc, OMC_CHAR** argv)
#endif
{
  char** newargv = omc_fixWindowsArgv(argc, argv);
  /*
    Set the error functions to be used for simulation.
    The default value for them is 'functions' version. Change it here to 'simulation' versions
  */
  omc_assert = omc_assert_simulation;
  omc_assert_withEquationIndexes = omc_assert_simulation_withEquationIndexes;

  omc_assert_warning_withEquationIndexes = omc_assert_warning_simulation_withEquationIndexes;
  omc_assert_warning = omc_assert_warning_simulation;
  omc_terminate = omc_terminate_simulation;
  omc_throw = omc_throw_simulation;

  int res;
  DATA data;
  MODEL_DATA modelData;
  SIMULATION_INFO simInfo;
  data.modelData = &modelData;
  data.simulationInfo = &simInfo;
  measure_time_flag = 0;
  compiledInDAEMode = 0;
  compiledWithSymSolver = 0;
  MMC_INIT(0);
  omc_alloc_interface.init();
  {
    MMC_TRY_TOP()
  
    MMC_TRY_STACK()
  
    SdofIso_setupDataStruc(&data, threadData);
    res = _main_initRuntimeAndSimulation(argc, newargv, &data, threadData);
    if(res == 0) {
      if (omc_flag[FLAG_MOO_OPTIMIZATION]) {
        res = _main_OptimizationRuntime(argc, newargv, &data, threadData);
      } else {
        res = _main_SimulationRuntime(argc, newargv, &data, threadData);
      }
    }
    
    MMC_ELSE()
    rml_execution_failed();
    fprintf(stderr, "Stack overflow detected and was not caught.\nSend us a bug report at https://trac.openmodelica.org/OpenModelica/newticket\n    Include the following trace:\n");
    printStacktraceMessages();
    fflush(NULL);
    return 1;
    MMC_CATCH_STACK()
    
    MMC_CATCH_TOP(return rml_execution_failed());
  }

  fflush(NULL);
  return res;
}

#ifdef __cplusplus
}
#endif


