import React, { useState, useEffect } from 'react';
import { Form, Upload, message, Spin} from 'antd';
import { InboxOutlined} from '@ant-design/icons';
import { connect } from 'dva';
import { withRouter } from 'umi';
import styles from '../index.less';
import { formatMessage } from 'umi-plugin-locale';
import { convertByteUnits, makeStepsDict } from '@/utils/util';
import {makeSampleDiv, makeCsvFileTip} from '@/pages/common/createDataset'
import { StepStatusIcon, UploadStepType } from '@/pages/common/appConst';


const { Dragger } = Upload;


const UploadPage = ({ dispatch, location,  uploadFile: { pollJobResponse }}) => {
  const [form] = Form.useForm();
  const [sampleStrategy, setSampleStrategy] = useState('whole_data'); // 抽样分析类型
  const [value, setValue] = useState(50); // 抽样分析value值
  const [fileName, setFileName] = useState(null);  // 设置文件上传headers里面的filename
  const [uploadStatus, setUploadStatus] = useState(StepStatusIcon['todo']);  // 上传icon状态
  const [loadingDataStatus, setLoadingDataStatus] = useState(StepStatusIcon['todo']); // 加载数据icon状态
  const [analysisDataStatus, setAnalysisDataStatus] = useState(StepStatusIcon['todo']); // 分析数据icon状态
  const [uploadTips, setUploadTips] = useState(formatMessage({id: 'upload.prepare'})); // 上传文件提示
  const [loadingDataTips, setLoadingDataTips] = useState(formatMessage({id: 'upload.prepare'})); // 加载数据提示
  const [analysisDataTips, setAnalysisDataTips] = useState(formatMessage({id: 'upload.prepare'})); // 分析数据提示

  useEffect(() => {

    if(pollJobResponse !== null && pollJobResponse !== undefined){
      const responseData = pollJobResponse.data
      const stepsObject = makeStepsDict(responseData.steps);
      const uploadStep = stepsObject[UploadStepType.upload];

      if(uploadStep !== undefined && uploadStep !== null){
        // 处理上传步骤
        if(uploadStep.status === 'succeed'){
          setUploadStatus(StepStatusIcon.done);
          setUploadTips(`${formatMessage({id: 'upload.hintUploadFile'}, {elapsed: uploadStep.took.toFixed(2), fileSize: convertByteUnits(uploadStep.extension.file_size)})}`);

          setLoadingDataStatus(StepStatusIcon.doing);  // 下一个步骤置为运行中
          setLoadingDataTips(formatMessage({id: 'upload.loading'}));

        }else{
            // todo
        }
      }

      const loadStep = stepsObject[UploadStepType.load];

      if (loadStep !== undefined && loadStep !== null) {
        if(loadStep.status === 'succeed'){
          const n_rows = loadStep['extension']['n_rows'];
          const n_cols = loadStep['extension']['n_cols'];
          const n_rows_used = loadStep['extension']['n_rows_used'];
          const loadingTook = loadStep['took'];

          setLoadingDataStatus(StepStatusIcon['done']);
          setLoadingDataTips(formatMessage({id: 'upload.hintLoadData'}, {elapsed: loadingTook.toFixed(2), nRows: n_rows, nColumns: n_cols, nRowsUsed: n_rows_used}) );

          setAnalysisDataStatus(StepStatusIcon['doing']);
          setAnalysisDataTips(formatMessage({id: 'upload.analysising'}));

        }else{
          setLoadingDataStatus(StepStatusIcon['undone']);
          setLoadingDataTips(formatMessage({id: 'upload.fail'}))
        }
      }

      const analyzeStep = stepsObject[UploadStepType.analyze];

      if(analyzeStep !== undefined && analyzeStep !== null){
        if (analyzeStep.status === 'succeed') {
          setAnalysisDataStatus(StepStatusIcon['done']);
          setLoadingDataStatus(StepStatusIcon['done']);
          // setAnalysisDataTips(`${formatMessage({id: 'upload.spend'})}${analysisTook}s，${formatMessage({id: 'upload.result'})}${continuous}${formatMessage({id: 'upload.rows'})}，${formatMessage({id: 'upload.category'})}${categorical}${formatMessage({id: 'upload.rows'})}，${formatMessage({id: 'upload.time'})}${datetime}${formatMessage({id: 'upload.rows'})}`);
          setAnalysisDataTips(`${formatMessage({id: 'upload.hintAnalysis'}, {elapsed: analyzeStep.took.toFixed(2), nContinuous: analyzeStep.extension.feature_summary.continuous, nCategorical: analyzeStep.extension.feature_summary.categorical,  nDatetime: analyzeStep.extension.feature_summary.datetime})}`);
        } else if (analyzeStep.status === 'failed') {
          setAnalysisDataStatus(StepStatusIcon['undone']);
          setAnalysisDataTips(formatMessage({id: 'upload.fail'}));
        }
      }
    }
  },[pollJobResponse]);



  const onChange = value => {
    if (isNaN(value)) {
      return;
    }
    setValue(value);
  };

  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: '.csv, .tsv',
    headers: {
      'File-Name': fileName,
    },
    action: '/api/resource',
    beforeUpload: (file) => {
      if (file.size > 128 * 1000000) {
        message.warning(formatMessage({id: 'upload.big'}));
        return false;
      }
      setFileName(file.name);
    },
    showUploadList: false,
    onChange(info) {
      const { status } = info.file;
      if (status === 'uploading') {
        setUploadStatus(StepStatusIcon['doing']);
        setUploadTips(formatMessage({id: 'upload.uploading'}));
      }
      if (status === 'done') {  // 上传成功
        // setUploadStatus(StepStatusIcon['done']);
        // setUploadTips(`${formatMessage({id: 'upload.hintUploadFile'}, {elapsed: info.file.response.data.took, fileSize: info.file.response.data.size }) }`)
        // setLoadingDataStatus(StepStatusIcon['doing']);
        // setLoadingDataTips(formatMessage({id: 'upload.loading'}));
        const filePath = info.file.response.data.path;
        const uploadTook = info.file.response.data.took;
        const text = sampleStrategy === 'random_rows' ? {
          n_rows: form.getFieldsValue().n_rows
        }: {
          percentage: value
        };
        const sourceType = location.query.sourceType;
        // 创建临时数据集
        dispatch({
          type: 'uploadFile/createTempDataset',
          payload: {
            sample_strategy:sampleStrategy,
            ...text,
            file_path: filePath,
            upload_took: uploadTook,
            source_type: sourceType,
          }
        });
        // using backend response instead
        // if (step2Status === 'succeed') {
        //   setLoadingDataStatus(StepStatusIcon['done']);
        // }
        // message.success(`${info.file.name} file uploaded successfully.`);
      } else if (status === 'error') {
        setUploadStatus(StepStatusIcon['undone']);
        setUploadTips(formatMessage({id: 'upload.uploadFail'}));
        message.error(`${info.file.name} file upload failed.`);
      }
    },
  };

  return (
    <>
      <div className={styles.main}>
          {makeSampleDiv(setSampleStrategy, sampleStrategy, form, onChange, value)}

          <div className={styles.fileUpload}>
            <dl>
              <dt>{formatMessage({id: 'upload.upload'})}</dt>
              {makeCsvFileTip()}
            </dl>

            <Dragger {...uploadProps} style={{ width: '85%'}}>
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">{formatMessage({id: 'upload.uploadBox'})}</p>
            </Dragger>

          </div>
        </div>
        <div className={styles.process}>
          <dl>
            <dt>
              { uploadStatus }
              <span className={styles.stepTitle}>1. {formatMessage({id: 'upload.uploadStep'})}</span>
            </dt>
            <dd className={styles.stepTips}>{ uploadTips }</dd>
          </dl>
          <dl>
            <dt>
              { loadingDataStatus }
              <span className={styles.stepTitle}>2. {formatMessage({id: 'upload.loadData'})}</span>
            </dt>
            <dd className={styles.stepTips}>{ loadingDataTips }</dd>
          </dl>
          <dl>
            <dt>
              { analysisDataStatus }
              <span className={styles.stepTitle}>3. {formatMessage({id: 'upload.analysisData'})}</span>
            </dt>
            <dd className={styles.stepTips}>{ analysisDataTips }</dd>
          </dl>
        </div>
    </>
  )
}
export default withRouter(connect(({ uploadFile }) => (
  { uploadFile }
))(UploadPage));
