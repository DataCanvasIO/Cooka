import { CheckOutlined, CloseOutlined, LoadingOutlined, MinusOutlined } from '@ant-design/icons';
import { Spin } from 'antd';
import React from 'react';

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


export const UploadStepType = {
  upload: 'upload',
  load:'load',
  analyze: 'analyzed',
};


export const ImportStepType = {
  copy: 'copy',
  load: UploadStepType.load,
  analyze: UploadStepType.analyze,
};


export const StepStatusIcon = {
  todo: (<MinusOutlined style={{ fontSize: 16, color: '#000'}}/>),
  doing: (<Spin indicator={ <LoadingOutlined style={{ fontSize: 16 }} spin /> } />),
  done: (<CheckOutlined style={{ fontSize: 16, color: 'green'}} />),
  undone: (<CloseOutlined style={{ fontSize: 16, color: 'red'}} />)
};

export const PartitionStrategy = {
  CrossValidation: 'cross_validation',
  TrainValidationHoldout: 'train_validation_holdout',
  Manual: 'manual'
};


export const PartitionClass = {
  Train: 'TRAIN',
  Test: 'TEST',
  Eval: 'EVAL'
}

export const FeatureType = {
  Categorical: 'categorical',
  Continuous: 'continuous',
  Text: 'text',
  Datetime: 'datetime'
}
