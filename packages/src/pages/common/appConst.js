
export const REFRESH_EXPERIMENT_LIST_TIMEOUT = 3000;  // 刷新实验列表间隔
export const REFRESH_BATCH_PREDICT_TIMEOUT = 3000;  // 刷新实验列表间隔



export const  TrainMode  = {
  Quick : "quick" ,
  Performance : "performance",
  Minimal : "minimal"
}


export const SampleStrategy = {
  RandomRows : 'random_rows',
  ByPercentage : 'by_percentage',
  WholeData: 'whole_data'
}


export const StepStatus = {
  Succeed : 'succeed',
  Failed : 'failed'
}


export const PredictStepType = {
  Upload: 'upload',
  Load: 'load',
  LoadModel: 'load_model',
  CheckDataType: 'check_data_type',
  Evaluate: 'evaluate',
  WriteResult: 'write_result',
}
