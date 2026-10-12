#if defined(__cplusplus)
  extern "C" {
#endif
  int SdofIso_mayer(DATA* data, modelica_real** res, short*);
  int SdofIso_lagrange(DATA* data, modelica_real** res, short *, short *);
  int SdofIso_getInputVarIndicesInOptimization(DATA* data, int* input_var_indices);
  int SdofIso_pickUpBoundsForInputsInOptimization(DATA* data, modelica_real* min, modelica_real* max, modelica_real*nominal, modelica_boolean *useNominal, char ** name, modelica_real * start, modelica_real * startTimeOpt);
  int SdofIso_setInputData(DATA *data, const modelica_boolean file);
  int SdofIso_getTimeGrid(DATA *data, modelica_integer * nsi, modelica_real**t);
#if defined(__cplusplus)
}
#endif
