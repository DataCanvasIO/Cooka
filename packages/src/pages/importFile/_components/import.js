import React, { useEffect, useState } from 'react';
import { Button, Card, Form, Input, Tooltip } from 'antd';
import { connect } from 'dva';
import { withRouter } from 'umi';
import styles from '../index.less';
import { formatMessage } from 'umi-plugin-locale';
import { checkoutStepFromStepsDict, makeCsvFileTip, makeSampleDiv } from '@/pages/common/createDataset';
import { ImportStepType, StepStatusIcon } from '@/pages/common/appConst';
import { convertByteUnits, makeStepsDict } from '@/utils/util';
import { testImportFile } from '@/services/dataset';


const ImportFilePage = ({dispatch, location,  importFile: { pollJobResponse }}) => {

  const [form] = Form.useForm();
  const [sampleStrategy, setSampleStrategy] = useState('whole_data'); // 抽样分析类型
  const [value, setValue] = useState(50); // 抽样分析value值
  const [uploadStatus, setUploadStatus] = useState(StepStatusIcon['todo']);  // 上传icon状态
  const [loadingDataStatus, setLoadingDataStatus] = useState(StepStatusIcon['todo']); // 加载数据icon状态
  const [analysisDataStatus, setAnalysisDataStatus] = useState(StepStatusIcon['todo']); // 分析数据icon状态
  const [uploadTips, setUploadTips] = useState(formatMessage({id: 'upload.prepare'})); // 上传文件提示
  const [loadingDataTips, setLoadingDataTips] = useState(formatMessage({id: 'upload.prepare'})); // 加载数据提示
  const [analysisDataTips, setAnalysisDataTips] = useState(formatMessage({id: 'upload.prepare'})); // 分析数据提示
  const [filePath, setFilePath] = useState('');
  const [disableAnalyzeBtn, setDisableAnalyzeBtn] = useState(true);
  const [inputFilePathTip, setInputFilePathTip] = useState(null);
  const [inputFilePathTipVisible, setInputFilePathTipVisible] = useState(false);


  const showFilePathTip = (tip) => {
    setInputFilePathTip(tip);
    setInputFilePathTipVisible(true);
  }

  const clearFilePathTip = () => {
    setInputFilePathTipVisible(false);
    setInputFilePathTip(null);
  }

  useEffect(() => {

    if(pollJobResponse !== null && pollJobResponse !== undefined) {
      const responseData = pollJobResponse.data
      const stepsDict = makeStepsDict(responseData.steps);

      checkoutStepFromStepsDict(stepsDict, ImportStepType.copy, (copyStep) => {

        if(copyStep.status === 'succeed') {
          const  copyTook = copyStep['took'];
          const  copiedFileSize = copyStep.extension.file_size;

          setUploadStatus(StepStatusIcon['done']);
          setUploadTips(`${formatMessage({id: 'upload.hintUploadFile'}, {elapsed: copyTook.toFixed(2), fileSize:  convertByteUnits(copiedFileSize) }) }`) // todo fixme
          setLoadingDataStatus(StepStatusIcon['doing']);
          setLoadingDataTips(formatMessage({id: 'upload.loading'}))
        } else  {
          setLoadingDataStatus(StepStatusIcon['undone']);
          setUploadTips(formatMessage({id: 'upload.fail'}))
        }
      })

      checkoutStepFromStepsDict(stepsDict, ImportStepType.load, (loadStep) => {

        if (loadStep.status === 'succeed') {

          const  n_cols  = loadStep.extension.n_cols;
          const  n_cols_used  = loadStep.extension.n_cols_used;
          const  n_rows  = loadStep.extension.n_rows;
          const  n_rows_used  = loadStep.extension.n_rows_used;
          const  loadingTook  = loadStep.took;

          setLoadingDataStatus(StepStatusIcon['done']);
          setLoadingDataTips(`${formatMessage({id: 'upload.hintLoadData'}, {elapsed: loadingTook.toFixed(2), nRows: n_rows, nColumns: n_cols, nRowsUsed: n_rows_used})  }`);

          setAnalysisDataStatus(StepStatusIcon['doing']);
          setAnalysisDataTips(formatMessage({id: 'upload.analysising'}))

        } else {
          setLoadingDataStatus(StepStatusIcon['undone']);
          setLoadingDataTips(formatMessage({id: 'upload.fail'}))
        }
      })

      checkoutStepFromStepsDict(stepsDict, ImportStepType.analyze, (analyzeStep) => {

        if (analyzeStep.status === 'succeed') {
          const categorical = analyzeStep.extension.feature_summary.categorical;
          const continuous = analyzeStep.extension.feature_summary.continuous;
          const datetime = analyzeStep.extension.feature_summary.datetime;
          const analysisTook = analyzeStep.took;

          setAnalysisDataStatus(StepStatusIcon['done']);
          setLoadingDataStatus(StepStatusIcon['done']);
          setAnalysisDataTips(`${formatMessage({id: 'upload.hintAnalysis'}, {elapsed: analysisTook.toFixed(2), nContinuous: continuous, nCategorical:categorical,  nDatetime: datetime})}`);

        } else  {
          setAnalysisDataStatus(StepStatusIcon['undone']);
          setAnalysisDataTips(formatMessage({id: 'import.fail'}));
        }
      })
    }

  },[pollJobResponse])


  const onChange = value => {
    if (isNaN(value)) {
      return;
    }
    setValue(value);
  };



  const throttle = (fn, delay) => {
    var timer;
    return function () {
        var _this = this;
        var args = arguments;
        if (timer) {
            return;
        }
        timer = setTimeout(function () {
            fn.apply(_this, args);
            timer = null; // 在delay后执行完fn之后清空timer，此时timer为假，throttle触发可以进入计时器
        }, delay)
    }
  };

  //  Test import file
  const handleFilepathTest = (value) => {
    if (value != null && value.length > 0) {
      setFilePath(value);
      dispatch({
        type: 'importFile/testImportFile',
        payload: {
          path: value
        }
      })
    }
  };

  const throttleHandleFilepathTest = throttle(handleFilepathTest, 100);


  //  handle analysis Button
  const handleAnalyses = () => {
    setUploadStatus(StepStatusIcon['doing']);
    const text = sampleStrategy === 'random_rows' ? {
      n_rows: form.getFieldsValue().n_rows,
      percentage: '',
    }: {
      percentage: value,
      n_rows: ''
    };
    const params = {
      sample_strategy:sampleStrategy,
      ...text,
      file_path: filePath,
      source_type: location.query.sourceType,
      upload_took: 10.0
    };
    dispatch({
      type: 'importFile/createTempDataset',
      payload: params
    })
  };

  const handleFilePathOnChange = e => {
    const { value } = e.target;
    setFilePath(value);
    if (value !== null && value !== undefined && value.length > 0) {
      testImportFile(value).then(response => {
        if(response.code === 0){
          setDisableAnalyzeBtn(false);
          clearFilePathTip();
        }else{
          const testMsg = response.data.message;
          console.info("hhhhh")
          console.info(testMsg);
          console.info(inputFilePathTipVisible);

          showFilePathTip(testMsg);
          setDisableAnalyzeBtn(true);
        }
      })
    }
  };

  const handleFilePathOnBlur = e => {

  }

  return (
    <>
      <div className={styles.main}>

        {makeSampleDiv(setSampleStrategy, sampleStrategy, form, onChange, value)}

        <div className={styles.fileUpload}>
            <dl>
              <dt>{formatMessage({id: 'import.address'})}</dt>
            </dl>

          <Card style={{ width: '85%' }}>
            {makeCsvFileTip()}
            <Tooltip
            trigger={['focus']}
            title={inputFilePathTip}
            visible={inputFilePathTipVisible}
            color={'#FFF2F0'}
            placement="right">
              <Input
              style={{ width: 300} }
              onChange={handleFilePathOnChange}
              onBlur={handleFilePathOnBlur}
              placeholder="File path in server "
              maxLength={256}
              minLength={0}
              />
            </Tooltip>
            <br/>
            <Button type="primary"
                    disabled={disableAnalyzeBtn}
                    style={{ marginTop: 10 }}
                    onClick={handleAnalyses}>
              {formatMessage({id: 'import.analysis'})}
            </Button>
          </Card>
        </div>
      </div>


        <div className={styles.process}>
          <dl>
            <dt>
              { uploadStatus }
              <span className={styles.stepTitle}>1. {formatMessage({id: 'import.copy'})}</span>
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
};

export default withRouter(connect(({ importFile }) => (
  { importFile }
))(ImportFilePage));
