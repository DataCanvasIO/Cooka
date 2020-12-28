import React, { useState } from 'react';
import { Col, message, Row, Steps, Upload } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { withRouter } from 'umi';
import { formatMessage } from 'umi-plugin-locale';
import { connect } from 'dva';
import { makeStepsDict, convertByteUnits } from '@/utils/util';
import { PredictStepType, StepStatus } from '@/pages/common/appConst';
import { showNotification } from '@/utils/notice';
import { batchPredict, getPredictJob } from '@/services/dataset';


const { Dragger } = Upload;
const { Step } = Steps;


const handleUnseenStatus = (step) => {
  showNotification('Unseen step status ' + step?.status + ' of ' + step?.type);
};


const Prediction = ({ indexParam, modelName, taskStatus, location: { query: { datasetName } } }) => {

  const [fileName, setFileName] = useState(null);  // 设置文件上传headers里面的filename
  const [uploadInfo, setUploadInfo] = useState('-');
  const [loadingInfo, setLoadingInfo] = useState('-');
  const [readingInfo, setReadingInfo] = useState('-');
  const [predictInfo, setPredictInfo] = useState('-');
  const [resultInfo, setResultInfo] = useState('-');
  const [status, setStatus] = useState('');
  const [current, setCurrent] = useState(-1);

  let predictTimer;

  const stopBatchPredictJobInterval = () => {
    if (predictTimer !== null){
      clearInterval(predictTimer);
      predictTimer = null;
    }
  };

  const checkBatchPredictJob = (datasetName, modelName, batchPredictJobName) => {
    getPredictJob(datasetName, modelName, batchPredictJobName).then(response => {

      if (response !== null && response !== undefined) {
        if (response.code === 0) {
          // 处理正常返回step信息
          const steps = response.data.steps;
          if (steps !== null && steps !== undefined) {
            const stepsDict = makeStepsDict(steps);

            // 上传数据步骤
            const uploadStep = stepsDict[PredictStepType.Upload];
            if (uploadStep !== null && uploadStep !== undefined) {
              setCurrent(0);
              if (uploadStep.status === StepStatus.Succeed) {
                setUploadInfo(formatMessage({ id: 'center.batchPredict.processTip.upload' }, {
                  fileSize: convertByteUnits(uploadStep.extension.file_size),
                  took: uploadStep.took.toFixed(2),
                }));

              } else if (uploadStep.status === StepStatus.Failed) {
                handleStepError(setUploadInfo);
              } else {
                handleUnseenStatus(uploadStep);
              }
            }

            // 加载数据
            const loadStep = stepsDict[PredictStepType.Load];
            if (loadStep !== null && loadStep !== undefined) {
              setCurrent(1);
              if (loadStep.status === StepStatus.Succeed) {
                setLoadingInfo(formatMessage({ id: 'center.batchPredict.processTip.loadData' }, {
                  nRows: loadStep.extension.n_rows,
                  nCols: loadStep.extension.n_cols,
                  took: loadStep.took.toFixed(2),
                }));
              } else if (loadStep.status === StepStatus.Failed) {
                handleStepError(setLoadingInfo);
              } else {
                handleUnseenStatus(uploadStep);
              }
            }

            // 加载模型
            const loadModelStep = stepsDict[PredictStepType.LoadModel];
            if (loadModelStep !== null && loadModelStep !== undefined) {
              setCurrent(2);
              if (loadModelStep.status === StepStatus.Succeed) {
                setReadingInfo(formatMessage({ id: 'center.batchPredict.processTip.loadModel' }, {
                  modelSize: convertByteUnits(loadModelStep.extension.model_size),
                  took: loadModelStep.took.toFixed(2),
                }));
              } else if (loadModelStep.status === StepStatus.Failed) {
                handleStepError(setReadingInfo);
              } else {
                handleUnseenStatus(loadModelStep);
              }
            }

            // 评估数据 evaluate
            const evaluateStep = stepsDict[PredictStepType.Evaluate];
            if (evaluateStep !== null && evaluateStep !== undefined) {
              setCurrent(3);
              if (evaluateStep.status === StepStatus.Succeed) {
                // setpredictInfo(`${formatMessage({id: 'center.spend'})}${evaluateStep.extension.took}s`)
                setPredictInfo(formatMessage({ id: 'center.batchPredict.processTip.evaluate'}, { took: evaluateStep.took.toFixed(2) }));
              } else if (evaluateStep.status === StepStatus.Failed) {
                handleStepError(setPredictInfo);
              } else {
                handleUnseenStatus(evaluateStep);
              }
            }

            // 写出结果
            const writeResultStep = stepsDict[PredictStepType.WriteResult];
            if (writeResultStep !== null && writeResultStep !== undefined) {
              // 如果最后一个结束了，也停止轮询，不管是否成功
              stopBatchPredictJobInterval();
              setCurrent(4);
              if (writeResultStep.status === StepStatus.Succeed) {
                setResultInfo(
                  <>
                    <p><a download
                          href={`/api/resource/${writeResultStep.extension.output_path}?opt=download`}>{formatMessage({ id: 'center.batchPredict.processTip.writeResult' })}</a>
                    </p>
                  </>,
                );
                setStatus('finish');
              } else if (writeResultStep.status === StepStatus.Failed) {
                handleStepError(setResultInfo);
              } else {
                handleUnseenStatus(writeResultStep);
              }
            }
          } else {
            showNotification('Response steps from server of prediction is null yet code is 0 ');
            stopBatchPredictJobInterval();
          }
        }else{
          // 后端返回错误，停止轮训
          stopBatchPredictJobInterval();
        }
      } else {
        showNotification('Response from server of prediction is null');
        stopBatchPredictJobInterval();
      }
    });
  };

  const handleUpload = (datasetName, modelName, file_path, upload_took) => {

    console.error("开启定时器: 11111");
    console.error("2开启定时器: " + predictTimer);

    // 构建预测请求
    const reqBatchPredictParams = {
      file_path: file_path,
      upload_took: upload_took,
    };

    // 发起预测请求
    batchPredict(datasetName, modelName, reqBatchPredictParams).then((pollResponse) => {
      const pollResponseData = pollResponse.data;
      // 轮询处理任务状态
      checkBatchPredictJob(datasetName, modelName, pollResponseData.batch_predict_job_name);

      // ensure only one running interval
      if (predictTimer !== null){
        stopBatchPredictJobInterval()
      }

      predictTimer = setInterval(() => {
        console.error("1开启定时器: " + predictTimer);
        checkBatchPredictJob(datasetName, modelName, pollResponseData.batch_predict_job_name);
      }, 1000);

      console.error("开启定时器: " + predictTimer);


    });
  };

  const handleStepError = (setInfo, errorTip = 'Failed', ) => {
    setInfo(errorTip);
    setStatus('error');
    ///有任何一个失败的Step就停止轮询
    stopBatchPredictJobInterval();
  };

  const props = {
    name: 'file',
    multiple: false,
    accept: '.csv, .tsv',
    headers: {
      'File-Name': fileName,
    },
    action: '/api/resource',
    beforeUpload: (file) => {
      if (file.size > 128 * 1000000) {
        message.warning(formatMessage({id: 'center.big'}));
        return false;
      }
      setFileName(file.name);
    },
    showUploadList: false,
    onChange(info) {
      const { status } = info.file;
      if (status !== 'uploading') {
        console.log(info.file, info.fileList);
      }
      if (status === 'done') {
        // message.success(`${info.file.name} ${formatMessage({id: 'center.success'})}`);
        setCurrent(0);
        handleUpload(datasetName, modelName, info.file.response.data.path, info.file.response.data.took);

      } else if (status === 'error') {
        message.error(`${info.file.name} ${formatMessage({id: 'center.failUpload'})}`);
        setStatus('error');
      }
    },
  };

  const batch_predict_ready =  (
    <Row>
      <Col span={24}>
      <Dragger {...props}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">{formatMessage({id: 'center.uploadBox'})}</p>
        <p className="ant-upload-hint">{formatMessage({id: 'center.uploadtips'})}</p>
      </Dragger>
      </Col>
      <Col span={24} style={{ marginTop: 24 }}>
        <Steps current={current} status={status}>
          <Step title={formatMessage({id: 'center.uploadData'})} description={uploadInfo} />
          <Step title={formatMessage({id: 'center.loadData'})} description={loadingInfo} />
          <Step title={formatMessage({id: 'center.read'})} description={readingInfo} />
          <Step title={formatMessage({id: 'center.predictData'})} description={predictInfo} />
          <Step title={formatMessage({id: 'center.result'})} description={resultInfo} />
        </Steps>
      </Col>
    </Row>
  )

  const batch_predict_not_ready = (
    <div style={{ textAlign: 'center', color: '#c4c4c4' }}>{formatMessage({id: 'center.training'})}</div>
  )

  return taskStatus === 'running' ? batch_predict_not_ready: batch_predict_ready

}
export default withRouter(connect(({ center }) => (
  { center }
))(Prediction));
