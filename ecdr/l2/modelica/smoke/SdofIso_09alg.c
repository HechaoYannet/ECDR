/* Algebraic */
#include "SdofIso_model.h"

#ifdef __cplusplus
extern "C" {
#endif

/* forwarded equations */
extern void SdofIso_eqFunction_27(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_30(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_33(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_34(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_35(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_37(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_38(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_39(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_40(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_41(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_43(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_44(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_45(DATA* data, threadData_t *threadData);
extern void SdofIso_eqFunction_46(DATA* data, threadData_t *threadData);

static void functionAlg_system0(DATA *data, threadData_t *threadData)
{
  static void (*const eqFunctions[14])(DATA*, threadData_t*) = {
    SdofIso_eqFunction_27,
    SdofIso_eqFunction_30,
    SdofIso_eqFunction_33,
    SdofIso_eqFunction_34,
    SdofIso_eqFunction_35,
    SdofIso_eqFunction_37,
    SdofIso_eqFunction_38,
    SdofIso_eqFunction_39,
    SdofIso_eqFunction_40,
    SdofIso_eqFunction_41,
    SdofIso_eqFunction_43,
    SdofIso_eqFunction_44,
    SdofIso_eqFunction_45,
    SdofIso_eqFunction_46
  };
  
  if (data->simulationInfo->evalSelection) {
    for (int i = 0; i < data->simulationInfo->evalSelection->n; i++) {
      int id = data->simulationInfo->evalSelection->idx[i];
      eqFunctions[id](data, threadData);
    }
  } else {
    for (int id = 0; id < 14; id++) {
      eqFunctions[id](data, threadData);
    }
  }
}
/* for continuous time variables */
int SdofIso_functionAlgebraics(DATA *data, threadData_t *threadData)
{

#if !defined(OMC_MINIMAL_RUNTIME)
  if (measure_time_flag) rt_tick(SIM_TIMER_ALGEBRAICS);
#endif
  data->simulationInfo->callStatistics.functionAlgebraics++;

  SdofIso_function_savePreSynchronous(data, threadData);
  
  functionAlg_system0(data, threadData);

#if !defined(OMC_MINIMAL_RUNTIME)
  if (measure_time_flag) rt_accumulate(SIM_TIMER_ALGEBRAICS);
#endif

  return 0;
}

#ifdef __cplusplus
}
#endif
