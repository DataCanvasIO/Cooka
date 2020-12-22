import React, { useState, useEffect } from 'react';
import { Form, Input, Card, Radio, Slider, InputNumber, Row, Col, message, Spin, Button, Tooltip } from 'antd';
import { QuestionCircleOutlined, CheckOutlined, LoadingOutlined, MinusOutlined, CloseOutlined } from '@ant-design/icons';
import { connect } from 'dva';
import { withRouter } from 'umi';
import styles from '../index.less';
import { formatMessage } from 'umi-plugin-locale';
import { makeCsvFileTip, makeSampleDiv } from '@/pages/common/createDataset';


const antIcon = <LoadingOutlined style={{ fontSize: 16 }} spin />;
const statusConfig = {
  todo: (<MinusOutlined style={{ fontSize: 16, color: '#000'}}/>),
  doing: (<Spin indicator={antIcon} />),
  done: (<CheckOutlined style={{ fontSize: 16, color: 'green'}} />),
  undone: (<CloseOutlined style={{ fontSize: 16, color: 'red'}} />)
};



/**
 * 带有tip提示的输入框
 */
export class TipInput extends React.Component {

  constructor(props){
    super(props);
    this.value = props.value;
    this.myOnChange = props.myOnChange;
    // this.onChange = props.onChange; //
    // this.onBlur = props.onBlur;
  };

  // '.' at the end or only '-' in the input box.
  onBlur = () => {
    const { value, onBlur, onChange } = this.props;
    // let valueTemp = value;
    // if (value.charAt(value.length - 1) === '.' || value === '-') {
    //   valueTemp = value.slice(0, -1);
    // }
    // onChange(valueTemp.replace(/0*(\d+)/, '$1'));
    // if (onBlur) {
    //   onBlur();
    // }
  };

  render() {
    return (
      <Tooltip
        trigger={['focus']}
        title={this.props.tipContent}
        color={'#FFF2F0'}
        placement="right"
        overlayClassName="numeric-input"
      >
        <Input
          style={{ width: 300} }
          value={this.props.value}
          onChange={this.myOnChange}
          onBlur={this.onBlur}
          placeholder="File path in server "
          maxLength={256}
          minLength={0}
        />
      </Tooltip>
    );
  }
}



const Uploadpage = ({dispatch, location,  importFile: { step1Status, step2Status, step3Status, uploadTook,
  n_cols, n_cols_used, n_rows, n_rows_used, loadingTook, categorical, continuous,
  datetime, analysisTook, testImportFileResponse, copyTook }}) => {

  const [form] = Form.useForm();
  const [sampleStrategy, setSampleStrategy] = useState('whole_data'); // 抽样分析类型
  const [value, setValue] = useState(50); // 抽样分析value值
  const [uploadStatus, setUploadStatus] = useState(statusConfig['todo']);  // 上传icon状态
  const [loadingDataStatus, setLoadingDataStatus] = useState(statusConfig['todo']); // 加载数据icon状态
  const [analysisDataStatus, setAnalysisDataStatus] = useState(statusConfig['todo']); // 分析数据icon状态
  const [uploadTips, setUploadTips] = useState(formatMessage({id: 'upload.prepare'})); // 上传文件提示
  const [loadingDataTips, setLoadingDataTips] = useState(formatMessage({id: 'upload.prepare'})); // 加载数据提示
  const [analysisDataTips, setAnalysisDataTips] = useState(formatMessage({id: 'upload.prepare'})); // 分析数据提示
  const [filePath, setFilePath] = useState('');


  useEffect(() => {
    if (step1Status === 'succeed') {
      setUploadStatus(statusConfig['done']);
      setUploadTips(`${formatMessage({id: 'upload.hintUploadFile'}, {elapsed: copyTook.toFixed(2), fileSize:  "10MB" }) }`) // todo fixme
      setLoadingDataStatus(statusConfig['doing']);
      setLoadingDataTips(formatMessage({id: 'upload.analysising'}))

    } else if ( step2Status === 'failed' ) {
      setLoadingDataStatus(statusConfig['undone']);
      setUploadTips(formatMessage({id: 'upload.fail'}))

    }
    if (step2Status === 'succeed') {
      setLoadingDataStatus(statusConfig['done']);
      setLoadingDataTips(`${formatMessage({id: 'upload.spend'})}${loadingTook.toFixed(2)}s，${formatMessage({id: 'upload.total'})}${n_rows}${formatMessage({id: 'upload.cols'})}${n_cols}${formatMessage({id: 'upload.rows'})}，${formatMessage({id: 'upload.loadstep'})}${n_rows_used}${formatMessage({id: 'upload.cols'})}${n_cols_used}${formatMessage({id: 'upload.rows'})}${formatMessage({id: 'upload.runAnalysis'})}`);
      setAnalysisDataStatus(statusConfig['doing']);
      setAnalysisDataStatus(formatMessage({id: 'upload.analysising'}))
    } else if ( step2Status === 'failed' ) {
      setLoadingDataStatus(statusConfig['undone']);
      setLoadingDataTips(formatMessage({id: 'upload.fail'}))

    }
    if (step3Status === 'succeed') {
      setAnalysisDataStatus(statusConfig['done']);
      setLoadingDataStatus(statusConfig['done']);
      setLoadingDataTips(`${formatMessage({id: 'upload.hintLoadData'}, {elapsed: loadingTook.toFixed(2), nRows: n_rows, nColumns: n_cols, nRowsUsed: n_rows_used})  }`);
      setAnalysisDataTips(`${formatMessage({id: 'upload.hintAnalysis'}, {elapsed: analysisTook.toFixed(2), nContinuous: continuous, nCategorical:categorical,  nDatetime: datetime})}`);
    } else if (step3Status === 'failed') {
      setAnalysisDataStatus(statusConfig['undone']);
      setAnalysisDataTips(formatMessage({id: 'import.fail'}));
    }
  },[step1Status, step2Status, step3Status, uploadTook, n_cols, n_cols_used, n_rows, n_rows_used, loadingTook, categorical, continuous, datetime, analysisTook, copyTook])



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
    setUploadStatus(statusConfig['doing']);
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

  let testImportFileReason;
  const testFileIsValid = testImportFileResponse.valid;
  if (!testFileIsValid){
    testImportFileReason = testImportFileResponse.reason;
  }else{
    testImportFileReason = null
  }

  // 处理分析按钮事件
  const handleFilePathOnChange = e => {
    const { value } = e.target;
    setFilePath(value);
    if (value != null && value.length > 0) {
      dispatch({
        type: 'importFile/testImportFile',
        payload: {
          path: value
        }
      });
    }
  };
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
            <TipInput myOnChange={handleFilePathOnChange} value={filePath} tipContent={testImportFileReason} >
            </TipInput>
            <br/>
            <Button type="primary" disabled={!testFileIsValid} style={{ marginTop: 10 }} onClick={ () => handleAnalyses()} >{formatMessage({id: 'import.analysis'})}</Button>
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
))(Uploadpage));
