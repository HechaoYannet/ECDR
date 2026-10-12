/* update bound parameters and variable attributes (start, nominal, min, max) */
#include "SdofIso_model.h"
#if defined(__cplusplus)
extern "C" {
#endif

/*
equation index: 49
type: SIMPLE_ASSIGN
damper.s_rel = damper.s_nominal
*/
static void SdofIso_eqFunction_49(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,49};
  if (data->modelData->realVarsData[0] /* damper.s_rel */ .dimension.numberOfDimensions == 0) {
    put_real_element((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[3]] /* damper.s_nominal PARAM */), 0, &data->modelData->realVarsData[0] /* damper.s_rel */ .attribute.nominal);
  } else {
    throwStreamPrint(NULL, "Not yet implemented for array nominal.");
  }

  if (omc_useStream[OMC_LOG_INIT_V]) {
    char nominal_buffer[2048];
    real_vector_to_string(&data->modelData->realVarsData[0] /* damper.s_rel */ .attribute.nominal, data->modelData->realVarsData[0] /* damper.s_rel */ .dimension.numberOfDimensions == 0, nominal_buffer, 2048);
    infoStreamPrint(OMC_LOG_INIT_V, 0, "%s(nominal=%s)",
      data->modelData->realVarsData[0] /* damper.s_rel */ .info.name,
      nominal_buffer);
  }
  threadData->lastEquationSolved = 49;
}

OMC_DISABLE_OPT
int SdofIso_updateBoundVariableAttributes(DATA *data, threadData_t *threadData)
{
  /* min ******************************************************** */
  infoStreamPrint(OMC_LOG_INIT, 1, "updating min-values");
  messageClose(OMC_LOG_INIT);
  
  /* max ******************************************************** */
  infoStreamPrint(OMC_LOG_INIT, 1, "updating max-values");
  messageClose(OMC_LOG_INIT);
  
  /* nominal **************************************************** */
  infoStreamPrint(OMC_LOG_INIT, 1, "updating nominal-values");
  SdofIso_eqFunction_49(data, threadData);
  messageClose(OMC_LOG_INIT);
  
  /* start ****************************************************** */
  infoStreamPrint(OMC_LOG_INIT, 1, "updating primary start-values");
  messageClose(OMC_LOG_INIT);
  
  return 0;
}

void SdofIso_updateBoundParameters_0(DATA *data, threadData_t *threadData);

/*
equation index: 51
type: SIMPLE_ASSIGN
damper.d = c_s
*/
OMC_DISABLE_OPT
static void SdofIso_eqFunction_51(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,51};
  (data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[2]] /* damper.d PARAM */) = (data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[1]] /* c_s PARAM */);
  threadData->lastEquationSolved = 51;
}

/*
equation index: 53
type: SIMPLE_ASSIGN
spring.c = k_s
*/
OMC_DISABLE_OPT
static void SdofIso_eqFunction_53(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,53};
  (data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[10]] /* spring.c PARAM */) = (data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[6]] /* k_s PARAM */);
  threadData->lastEquationSolved = 53;
}

/*
equation index: 55
type: SIMPLE_ASSIGN
payload.m = m_p
*/
OMC_DISABLE_OPT
static void SdofIso_eqFunction_55(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,55};
  (data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[9]] /* payload.m PARAM */) = (data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[7]] /* m_p PARAM */);
  threadData->lastEquationSolved = 55;
}

/*
equation index: 56
type: SIMPLE_ASSIGN
gnd.w_crit = 6.283185307179586 * gnd.f_crit
*/
OMC_DISABLE_OPT
static void SdofIso_eqFunction_56(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,56};
  (data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[5]] /* gnd.w_crit PARAM */) = (6.283185307179586) * ((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[4]] /* gnd.f_crit PARAM */));
  threadData->lastEquationSolved = 56;
}
extern void SdofIso_eqFunction_4(DATA *data, threadData_t *threadData);

extern void SdofIso_eqFunction_3(DATA *data, threadData_t *threadData);

extern void SdofIso_eqFunction_2(DATA *data, threadData_t *threadData);

extern void SdofIso_eqFunction_1(DATA *data, threadData_t *threadData);


/*
equation index: 63
type: ALGORITHM

  assert(damper.d >= 0.0, "Variable violating min constraint: 0.0 <= damper.d, has value: " + String(damper.d, "g"));
*/
OMC_DISABLE_OPT
static void SdofIso_eqFunction_63(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,63};
  modelica_boolean tmp0;
  static const MMC_DEFSTRINGLIT(tmp1,63,"Variable violating min constraint: 0.0 <= damper.d, has value: ");
  modelica_string tmp2;
  modelica_metatype tmpMeta3;
  static int tmp4 = 0;
  if(!tmp4)
  {
    tmp0 = GreaterEq((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[2]] /* damper.d PARAM */),0.0);
    if(!tmp0)
    {
      tmp2 = modelica_real_to_modelica_string_format((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[2]] /* damper.d PARAM */), (modelica_string) mmc_strings_len1[103]);
      tmpMeta3 = stringAppend(MMC_REFSTRINGLIT(tmp1),tmp2);
      {
        const char* assert_cond = "(damper.d >= 0.0)";
        if (data->simulationInfo->noThrowAsserts) {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Components/Damper.mo",4,3,5,23,0};
          infoStreamPrintWithEquationIndexes(OMC_LOG_ASSERT, info, 0, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta3));
        } else {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Components/Damper.mo",4,3,5,23,0};
          omc_assert_warning_withEquationIndexes(info, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta3));
        }
      }
      tmp4 = 1;
    }
  }
  threadData->lastEquationSolved = 63;
}

/*
equation index: 64
type: ALGORITHM

  assert(damper.s_nominal >= 0.0, "Variable violating min constraint: 0.0 <= damper.s_nominal, has value: " + String(damper.s_nominal, "g"));
*/
OMC_DISABLE_OPT
static void SdofIso_eqFunction_64(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,64};
  modelica_boolean tmp5;
  static const MMC_DEFSTRINGLIT(tmp6,71,"Variable violating min constraint: 0.0 <= damper.s_nominal, has value: ");
  modelica_string tmp7;
  modelica_metatype tmpMeta8;
  static int tmp9 = 0;
  if(!tmp9)
  {
    tmp5 = GreaterEq((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[3]] /* damper.s_nominal PARAM */),0.0);
    if(!tmp5)
    {
      tmp7 = modelica_real_to_modelica_string_format((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[3]] /* damper.s_nominal PARAM */), (modelica_string) mmc_strings_len1[103]);
      tmpMeta8 = stringAppend(MMC_REFSTRINGLIT(tmp6),tmp7);
      {
        const char* assert_cond = "(damper.s_nominal >= 0.0)";
        if (data->simulationInfo->noThrowAsserts) {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Interfaces/PartialCompliantWithRelativeStates.mo",8,3,10,40,0};
          infoStreamPrintWithEquationIndexes(OMC_LOG_ASSERT, info, 0, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta8));
        } else {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Interfaces/PartialCompliantWithRelativeStates.mo",8,3,10,40,0};
          omc_assert_warning_withEquationIndexes(info, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta8));
        }
      }
      tmp9 = 1;
    }
  }
  threadData->lastEquationSolved = 64;
}

/*
equation index: 65
type: ALGORITHM

  assert(damper.stateSelect >= StateSelect.never and damper.stateSelect <= StateSelect.always, "Variable violating min/max constraint: StateSelect.never <= damper.stateSelect <= StateSelect.always, has value: " + String(damper.stateSelect, "d"));
*/
OMC_DISABLE_OPT
static void SdofIso_eqFunction_65(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,65};
  modelica_boolean tmp10;
  modelica_boolean tmp11;
  static const MMC_DEFSTRINGLIT(tmp12,113,"Variable violating min/max constraint: StateSelect.never <= damper.stateSelect <= StateSelect.always, has value: ");
  modelica_string tmp13;
  modelica_metatype tmpMeta14;
  static int tmp15 = 0;
  if(!tmp15)
  {
    tmp10 = GreaterEq((data->simulationInfo->integerParameter[data->simulationInfo->integerParamsIndex[0]] /* damper.stateSelect PARAM */),1);
    tmp11 = LessEq((data->simulationInfo->integerParameter[data->simulationInfo->integerParamsIndex[0]] /* damper.stateSelect PARAM */),5);
    if(!(tmp10 && tmp11))
    {
      tmp13 = modelica_integer_to_modelica_string_format((data->simulationInfo->integerParameter[data->simulationInfo->integerParamsIndex[0]] /* damper.stateSelect PARAM */), (modelica_string) mmc_strings_len1[100]);
      tmpMeta14 = stringAppend(MMC_REFSTRINGLIT(tmp12),tmp13);
      {
        const char* assert_cond = "(damper.stateSelect >= StateSelect.never and damper.stateSelect <= StateSelect.always)";
        if (data->simulationInfo->noThrowAsserts) {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Interfaces/PartialCompliantWithRelativeStates.mo",5,3,7,57,0};
          infoStreamPrintWithEquationIndexes(OMC_LOG_ASSERT, info, 0, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta14));
        } else {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Interfaces/PartialCompliantWithRelativeStates.mo",5,3,7,57,0};
          omc_assert_warning_withEquationIndexes(info, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta14));
        }
      }
      tmp15 = 1;
    }
  }
  threadData->lastEquationSolved = 65;
}

/*
equation index: 66
type: ALGORITHM

  assert(spring.s_rel0 >= 0.0, "Variable violating min constraint: 0.0 <= spring.s_rel0, has value: " + String(spring.s_rel0, "g"));
*/
OMC_DISABLE_OPT
static void SdofIso_eqFunction_66(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,66};
  modelica_boolean tmp16;
  static const MMC_DEFSTRINGLIT(tmp17,68,"Variable violating min constraint: 0.0 <= spring.s_rel0, has value: ");
  modelica_string tmp18;
  modelica_metatype tmpMeta19;
  static int tmp20 = 0;
  if(!tmp20)
  {
    tmp16 = GreaterEq((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[11]] /* spring.s_rel0 PARAM */),0.0);
    if(!tmp16)
    {
      tmp18 = modelica_real_to_modelica_string_format((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[11]] /* spring.s_rel0 PARAM */), (modelica_string) mmc_strings_len1[103]);
      tmpMeta19 = stringAppend(MMC_REFSTRINGLIT(tmp17),tmp18);
      {
        const char* assert_cond = "(spring.s_rel0 >= 0.0)";
        if (data->simulationInfo->noThrowAsserts) {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Components/Spring.mo",6,3,6,61,0};
          infoStreamPrintWithEquationIndexes(OMC_LOG_ASSERT, info, 0, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta19));
        } else {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Components/Spring.mo",6,3,6,61,0};
          omc_assert_warning_withEquationIndexes(info, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta19));
        }
      }
      tmp20 = 1;
    }
  }
  threadData->lastEquationSolved = 66;
}

/*
equation index: 67
type: ALGORITHM

  assert(spring.c >= 0.0, "Variable violating min constraint: 0.0 <= spring.c, has value: " + String(spring.c, "g"));
*/
OMC_DISABLE_OPT
static void SdofIso_eqFunction_67(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,67};
  modelica_boolean tmp21;
  static const MMC_DEFSTRINGLIT(tmp22,63,"Variable violating min constraint: 0.0 <= spring.c, has value: ");
  modelica_string tmp23;
  modelica_metatype tmpMeta24;
  static int tmp25 = 0;
  if(!tmp25)
  {
    tmp21 = GreaterEq((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[10]] /* spring.c PARAM */),0.0);
    if(!tmp21)
    {
      tmp23 = modelica_real_to_modelica_string_format((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[10]] /* spring.c PARAM */), (modelica_string) mmc_strings_len1[103]);
      tmpMeta24 = stringAppend(MMC_REFSTRINGLIT(tmp22),tmp23);
      {
        const char* assert_cond = "(spring.c >= 0.0)";
        if (data->simulationInfo->noThrowAsserts) {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Components/Spring.mo",4,3,5,22,0};
          infoStreamPrintWithEquationIndexes(OMC_LOG_ASSERT, info, 0, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta24));
        } else {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Components/Spring.mo",4,3,5,22,0};
          omc_assert_warning_withEquationIndexes(info, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta24));
        }
      }
      tmp25 = 1;
    }
  }
  threadData->lastEquationSolved = 67;
}

/*
equation index: 68
type: ALGORITHM

  assert(payload.stateSelect >= StateSelect.never and payload.stateSelect <= StateSelect.always, "Variable violating min/max constraint: StateSelect.never <= payload.stateSelect <= StateSelect.always, has value: " + String(payload.stateSelect, "d"));
*/
OMC_DISABLE_OPT
static void SdofIso_eqFunction_68(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,68};
  modelica_boolean tmp26;
  modelica_boolean tmp27;
  static const MMC_DEFSTRINGLIT(tmp28,114,"Variable violating min/max constraint: StateSelect.never <= payload.stateSelect <= StateSelect.always, has value: ");
  modelica_string tmp29;
  modelica_metatype tmpMeta30;
  static int tmp31 = 0;
  if(!tmp31)
  {
    tmp26 = GreaterEq((data->simulationInfo->integerParameter[data->simulationInfo->integerParamsIndex[1]] /* payload.stateSelect PARAM */),1);
    tmp27 = LessEq((data->simulationInfo->integerParameter[data->simulationInfo->integerParamsIndex[1]] /* payload.stateSelect PARAM */),5);
    if(!(tmp26 && tmp27))
    {
      tmp29 = modelica_integer_to_modelica_string_format((data->simulationInfo->integerParameter[data->simulationInfo->integerParamsIndex[1]] /* payload.stateSelect PARAM */), (modelica_string) mmc_strings_len1[100]);
      tmpMeta30 = stringAppend(MMC_REFSTRINGLIT(tmp28),tmp29);
      {
        const char* assert_cond = "(payload.stateSelect >= StateSelect.never and payload.stateSelect <= StateSelect.always)";
        if (data->simulationInfo->noThrowAsserts) {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Components/Mass.mo",4,3,5,76,0};
          infoStreamPrintWithEquationIndexes(OMC_LOG_ASSERT, info, 0, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta30));
        } else {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Components/Mass.mo",4,3,5,76,0};
          omc_assert_warning_withEquationIndexes(info, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta30));
        }
      }
      tmp31 = 1;
    }
  }
  threadData->lastEquationSolved = 68;
}

/*
equation index: 69
type: ALGORITHM

  assert(payload.m >= 0.0, "Variable violating min constraint: 0.0 <= payload.m, has value: " + String(payload.m, "g"));
*/
OMC_DISABLE_OPT
static void SdofIso_eqFunction_69(DATA *data, threadData_t *threadData)
{
  const int equationIndexes[2] = {1,69};
  modelica_boolean tmp32;
  static const MMC_DEFSTRINGLIT(tmp33,64,"Variable violating min constraint: 0.0 <= payload.m, has value: ");
  modelica_string tmp34;
  modelica_metatype tmpMeta35;
  static int tmp36 = 0;
  if(!tmp36)
  {
    tmp32 = GreaterEq((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[9]] /* payload.m PARAM */),0.0);
    if(!tmp32)
    {
      tmp34 = modelica_real_to_modelica_string_format((data->simulationInfo->realParameter[data->simulationInfo->realParamsIndex[9]] /* payload.m PARAM */), (modelica_string) mmc_strings_len1[103]);
      tmpMeta35 = stringAppend(MMC_REFSTRINGLIT(tmp33),tmp34);
      {
        const char* assert_cond = "(payload.m >= 0.0)";
        if (data->simulationInfo->noThrowAsserts) {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Components/Mass.mo",3,3,3,65,0};
          infoStreamPrintWithEquationIndexes(OMC_LOG_ASSERT, info, 0, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta35));
        } else {
          FILE_INFO info = {"/root/.openmodelica/libraries/Modelica 4.1.0+maint.om/Mechanics/Translational/Components/Mass.mo",3,3,3,65,0};
          omc_assert_warning_withEquationIndexes(info, equationIndexes, "The following assertion has been violated %sat time %f\n(%s) --> \"%s\"", initial() ? "during initialization " : "", data->localData[0]->timeValue, assert_cond, MMC_STRINGDATA(tmpMeta35));
        }
      }
      tmp36 = 1;
    }
  }
  threadData->lastEquationSolved = 69;
}
OMC_DISABLE_OPT
void SdofIso_updateBoundParameters_0(DATA *data, threadData_t *threadData)
{
  static void (*const eqFunctions[15])(DATA*, threadData_t*) = {
    SdofIso_eqFunction_51,
    SdofIso_eqFunction_53,
    SdofIso_eqFunction_55,
    SdofIso_eqFunction_56,
    SdofIso_eqFunction_4,
    SdofIso_eqFunction_3,
    SdofIso_eqFunction_2,
    SdofIso_eqFunction_1,
    SdofIso_eqFunction_63,
    SdofIso_eqFunction_64,
    SdofIso_eqFunction_65,
    SdofIso_eqFunction_66,
    SdofIso_eqFunction_67,
    SdofIso_eqFunction_68,
    SdofIso_eqFunction_69
  };
  
  for (int id = 0; id < 15; id++) {
    eqFunctions[id](data, threadData);
  }
}
OMC_DISABLE_OPT
int SdofIso_updateBoundParameters(DATA *data, threadData_t *threadData)
{
  (data->simulationInfo->booleanParameter[data->simulationInfo->booleanParamsIndex[0]] /* damper.useHeatPort PARAM */) = 0 /* false */;
  data->modelData->booleanParameterData[0].time_unvarying = 1;
  (data->simulationInfo->booleanParameter[data->simulationInfo->booleanParamsIndex[1]] /* gnd.exact PARAM */) = 1 /* true */;
  data->modelData->booleanParameterData[1].time_unvarying = 1;
  (data->simulationInfo->booleanParameter[data->simulationInfo->booleanParamsIndex[2]] /* gnd.useSupport PARAM */) = 0 /* false */;
  data->modelData->booleanParameterData[2].time_unvarying = 1;
  (data->simulationInfo->integerParameter[data->simulationInfo->integerParamsIndex[0]] /* damper.stateSelect PARAM */) = 4;
  data->modelData->integerParameterData[0].time_unvarying = 1;
  (data->simulationInfo->integerParameter[data->simulationInfo->integerParamsIndex[1]] /* payload.stateSelect PARAM */) = 3;
  data->modelData->integerParameterData[1].time_unvarying = 1;
  SdofIso_updateBoundParameters_0(data, threadData);
  return 0;
}

#if defined(__cplusplus)
}
#endif
