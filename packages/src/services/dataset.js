import request from '@/utils/request';

// 获取数据集列表
export function getDatasetList(params) {
  return request.get('/api/dataset', params);
}

// 删除某条数据集
export function deleteDataset(params) {
  return request.delete(`/api/dataset/${params.name}`)
}

// 创建临时数据集
export function createTempDataset(params) {
  return request.post('/api/temporary-dataset', params);
}

// 查询文件上传后的状态
export function getRetrieveData(params) {
  return request.get(`/api/dataset/${params.temporary_dataset_name}/analyze-job/${params.analyze_job_name}`);
}

// 文件上传成功后数据预览
export function getTempDataPreview(params) {
  return request.get(`/api/dataset/${params['uriParams'].temporary_dataset_name}/preview`, params['params']);
}

// 文件上传成功后数据探查
export function getTempDateRetrieve(params) {
  return request.get(`api/dataset/${params['temporary_dataset_name']}`);
}

// 检测文件路径
export function testImportFile(path) {
  return request.post('/api/dataset/test-import-file', { path }, null, false);
}

// 创建数据集
export function createDataset(params) {
  return request.post('/api/dataset', params);
}

// 创建数据集成功后的数据预览
export function getDataPreview(params) {
  return request.get(`/api/dataset/${params['uriParams'].datasetName}/preview`, params['param']);
}

// 创建数据集成功后的数据探查
export function getDataRetrieve(datasetName) {
  const param = {
    n_top_value: 10
  };
  return request.get(`api/dataset/${datasetName}`, param);
}

// 任务类型推断
export function interTaskType(datasetName, target) {
  return request.post(`api/dataset/${datasetName}/infer-task-type`, { feature_name: target, });
}

// 模型训练
export function train(params) {
  return request.post(`api/dataset/${params['datasetName']}/feature-series/default/train-job`, params['param']);
}

// 模型训练自动选取参数
export function getRecommendConfig(datasetName, target_col) {
  return request.post(`api/dataset/${datasetName}/feature-series/default/recommend-train-conf`, { target_col: target_col })
}

// 模型中心
export function getTrainingList(datasetName) {
  return request.get(`api/dataset/${datasetName}/feature-series/default/train-job`);
}

// 模型中心 -- 性能
export function getModelDetail(params) {
  return request.get(`api/dataset/${params['datasetName']}/feature-series/default/model/${params['modelName']}`);
}

// 模型中心 -- 获取预测name
export function batchPredict(datasetName, modelName, reqParams) {
  return request.post(`api/dataset/${datasetName}/feature-series/default/model/${modelName}/batch-predict-job`, reqParams);
}

// 模型中心 -- 轮询预测状态
export function getPredictJob(datasetName, modelName, batch_predict_job_name) {
  return request.get(`api/dataset/${datasetName}/feature-series/default/model/${modelName}/batch-predict-job/${batch_predict_job_name}`);
}


export function checkDatasetName(datasetName) {
  return request.post(`/api/dataset/${datasetName}/check-name`, {}, null, false);
}
