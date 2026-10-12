/* Initialization */
#include "SdofIso_model.h"
#include "SdofIso_11mix.h"
#include "SdofIso_12jac.h"
#if defined(__cplusplus)
extern "C" {
#endif

void SdofIso_functionInitialEquations_0(DATA *data, threadData_t *threadData);

/*
equation index: 1
type: SIMPLE_ASSIGN
gnd.v = 0.0
*/
void SdofIso_eqFunction_1(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,1};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[18]] /* gnd.v variable */) = 0.0;
  threadData->lastEquationSolved = 1;
}

/*
equation index: 2
type: SIMPLE_ASSIGN
gnd.a = 0.0
*/
void SdofIso_eqFunction_2(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,2};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[15]] /* gnd.a variable */) = 0.0;
  threadData->lastEquationSolved = 2;
}

/*
equation index: 3
type: SIMPLE_ASSIGN
payload.flange_b.f = 0.0
*/
void SdofIso_eqFunction_3(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,3};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[21]] /* payload.flange_b.f variable */) = 0.0;
  threadData->lastEquationSolved = 3;
}

/*
equation index: 4
type: SIMPLE_ASSIGN
gnd.s_support = 0.0
*/
void SdofIso_eqFunction_4(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,4};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[17]] /* gnd.s_support variable */) = 0.0;
  threadData->lastEquationSolved = 4;
}

/*
equation index: 5
type: SIMPLE_ASSIGN
$DER.$DER.x_ground = (-A) * sin(w * time) * w ^ 2.0
*/
void SdofIso_eqFunction_5(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,5};
  modelica_real tmp0;
  tmp0 = (data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[12]] /* w PARAM */);
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[5]] /* der(der(x_ground)) DUMMY_DER */) = ((-(data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[0]] /* A PARAM */))) * ((sin(((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[12]] /* w PARAM */)) * (data->localData[0]->timeValue))) * ((tmp0 * tmp0)));
  threadData->lastEquationSolved = 5;
}

/*
equation index: 6
type: SIMPLE_ASSIGN
$DER.x_ground = A * cos(w * time) * w
*/
void SdofIso_eqFunction_6(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,6};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[9]] /* der(x_ground) DUMMY_DER */) = ((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[0]] /* A PARAM */)) * ((cos(((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[12]] /* w PARAM */)) * (data->localData[0]->timeValue))) * ((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[12]] /* w PARAM */)));
  threadData->lastEquationSolved = 6;
}

/*
equation index: 7
type: SIMPLE_ASSIGN
x_ground = A * sin(w * time)
*/
void SdofIso_eqFunction_7(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,7};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[27]] /* x_ground DUMMY_STATE */) = ((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[0]] /* A PARAM */)) * (sin(((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[12]] /* w PARAM */)) * (data->localData[0]->timeValue)));
  threadData->lastEquationSolved = 7;
}

/*
equation index: 8
type: SIMPLE_ASSIGN
payload.s = $START.payload.s
*/
void SdofIso_eqFunction_8(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,8};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[23]] /* payload.s DUMMY_STATE */) = ((modelica_real *)((data->modelData->realVarsData[23] /* payload.s DUMMY_STATE */).attribute .start.data))[0];
  threadData->lastEquationSolved = 8;
}

/*
equation index: 9
type: SIMPLE_ASSIGN
damper.flange_b.s = payload.s + (-0.5) * payload.L
*/
void SdofIso_eqFunction_9(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,9};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[13]] /* damper.flange_b.s DUMMY_STATE */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[23]] /* payload.s DUMMY_STATE */) + (-0.5) * ((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[8]] /* payload.L PARAM */));
  threadData->lastEquationSolved = 9;
}

/*
equation index: 10
type: SIMPLE_ASSIGN
damper.s_rel = damper.flange_b.s - x_ground
*/
void SdofIso_eqFunction_10(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,10};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[0]] /* damper.s_rel STATE(1,damper.v_rel) */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[13]] /* damper.flange_b.s DUMMY_STATE */) - (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[27]] /* x_ground DUMMY_STATE */);
  threadData->lastEquationSolved = 10;
}
extern void SdofIso_eqFunction_27(DATA *data, threadData_t *threadData);


/*
equation index: 12
type: SIMPLE_ASSIGN
spring.f = spring.c * (spring.s_rel - spring.s_rel0)
*/
void SdofIso_eqFunction_12(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,12};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[25]] /* spring.f variable */) = ((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[10]] /* spring.c PARAM */)) * ((data->localData[0]->realVars[data->simulationInfo->realVarsIndex[26]] /* spring.s_rel variable */) - (data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[11]] /* spring.s_rel0 PARAM */));
  threadData->lastEquationSolved = 12;
}
extern void SdofIso_eqFunction_46(DATA *data, threadData_t *threadData);


/*
equation index: 14
type: SIMPLE_ASSIGN
payload.v = $START.payload.v
*/
void SdofIso_eqFunction_14(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,14};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[24]] /* payload.v DUMMY_STATE */) = ((modelica_real *)((data->modelData->realVarsData[24] /* payload.v DUMMY_STATE */).attribute .start.data))[0];
  threadData->lastEquationSolved = 14;
}
extern void SdofIso_eqFunction_40(DATA *data, threadData_t *threadData);


/*
equation index: 16
type: SIMPLE_ASSIGN
damper.v_rel = $DER.damper.flange_b.s - $DER.x_ground
*/
void SdofIso_eqFunction_16(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,16};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[1]] /* damper.v_rel STATE(1) */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[6]] /* der(damper.flange_b.s) DUMMY_DER */) - (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[9]] /* der(x_ground) DUMMY_DER */);
  threadData->lastEquationSolved = 16;
}
extern void SdofIso_eqFunction_36(DATA *data, threadData_t *threadData);

extern void SdofIso_eqFunction_29(DATA *data, threadData_t *threadData);

extern void SdofIso_eqFunction_30(DATA *data, threadData_t *threadData);


/*
equation index: 20
type: SIMPLE_ASSIGN
payload.flange_a.f = (-damper.f) - spring.f
*/
void SdofIso_eqFunction_20(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,20};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[20]] /* payload.flange_a.f variable */) = (-(data->localData[0]->realVars[data->simulationInfo->realVarsIndex[12]] /* damper.f variable */)) - (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[25]] /* spring.f variable */);
  threadData->lastEquationSolved = 20;
}

/*
equation index: 21
type: SIMPLE_ASSIGN
payload.a = payload.flange_a.f / payload.m
*/
void SdofIso_eqFunction_21(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,21};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[19]] /* payload.a variable */) = DIVISION_SIM((data->localData[0]->realVars[data->simulationInfo->realVarsIndex[20]] /* payload.flange_a.f variable */),(data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[9]] /* payload.m PARAM */),"payload.m",equationIndexes);
  threadData->lastEquationSolved = 21;
}
extern void SdofIso_eqFunction_34(DATA *data, threadData_t *threadData);


/*
equation index: 23
type: SIMPLE_ASSIGN
$DER.damper.v_rel = $DER.$DER.damper.flange_b.s - $DER.$DER.x_ground
*/
void SdofIso_eqFunction_23(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,23};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[3]] /* der(damper.v_rel) STATE_DER */) = (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[4]] /* der(der(damper.flange_b.s)) DUMMY_DER */) - (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[5]] /* der(der(x_ground)) DUMMY_DER */);
  threadData->lastEquationSolved = 23;
}
extern void SdofIso_eqFunction_33(DATA *data, threadData_t *threadData);


/*
equation index: 25
type: SIMPLE_ASSIGN
gnd.flange.f = -payload.flange_a.f
*/
void SdofIso_eqFunction_25(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,25};
  (data->localData[0]->realVars[data->simulationInfo->realVarsIndex[16]] /* gnd.flange.f variable */) = (-(data->localData[0]->realVars[data->simulationInfo->realVarsIndex[20]] /* payload.flange_a.f variable */));
  threadData->lastEquationSolved = 25;
}
extern void SdofIso_eqFunction_41(DATA *data, threadData_t *threadData);

OMC_DISABLE_OPT
void SdofIso_functionInitialEquations_0(DATA *data, threadData_t *threadData)
{
  static void (*const eqFunctions[26])(DATA*, threadData_t*) = {
    SdofIso_eqFunction_1,
    SdofIso_eqFunction_2,
    SdofIso_eqFunction_3,
    SdofIso_eqFunction_4,
    SdofIso_eqFunction_5,
    SdofIso_eqFunction_6,
    SdofIso_eqFunction_7,
    SdofIso_eqFunction_8,
    SdofIso_eqFunction_9,
    SdofIso_eqFunction_10,
    SdofIso_eqFunction_27,
    SdofIso_eqFunction_12,
    SdofIso_eqFunction_46,
    SdofIso_eqFunction_14,
    SdofIso_eqFunction_40,
    SdofIso_eqFunction_16,
    SdofIso_eqFunction_36,
    SdofIso_eqFunction_29,
    SdofIso_eqFunction_30,
    SdofIso_eqFunction_20,
    SdofIso_eqFunction_21,
    SdofIso_eqFunction_34,
    SdofIso_eqFunction_23,
    SdofIso_eqFunction_33,
    SdofIso_eqFunction_25,
    SdofIso_eqFunction_41
  };
  
  for (int id = 0; id < 26; id++) {
    eqFunctions[id](data, threadData);
  }
}

int SdofIso_functionInitialEquations(DATA *data, threadData_t *threadData)
{
  data->simulationInfo->discreteCall = 1;
  SdofIso_functionInitialEquations_0(data, threadData);
  data->simulationInfo->discreteCall = 0;
  
  return 0;
}

/* No SdofIso_functionInitialEquations_lambda0 function */

int SdofIso_functionRemovedInitialEquations(DATA *data, threadData_t *threadData)
{
  const int *equationIndexes = NULL;
  double res = 0.0;

  
  return 0;
}


#if defined(__cplusplus)
}
#endif
