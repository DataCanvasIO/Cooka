import React, { useState, useEffect } from 'react';
import { Upload, Col, Row, message, Steps } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { Hhistogram } from '@/components';
import { withRouter } from 'umi';
import { formatMessage } from 'umi-plugin-locale';
import { connect } from 'dva';

const { Dragger } = Upload;
const { Step } = Steps;

const Prediction = ({ handleUpload, indexParam, modelName, taskStatus, location: { query: { datasetName } }, data: { current, step2: { loadingStatus, n_cols = '', n_rows = '', loadTook = '' }, step3: { readingStatus, readTook, loadModelSize }, step4: { predictStatus, predictTook }, step5: { resultStatus, resultTook, outputPath }, loadErrorMsg, readErrorMsg, predictErrorMsg, resultErrorMsg } }) => {
  const html = (
    <>
      <a href="">{formatMessage({id: 'center.download'})}</a>
    </>
  )
  const [fileName, setFileName] = useState(null);  // 设置文件上传headers里面的filename
  const [uploadInfo, setUploadInfo] = useState('-');
  const [loadingInfo, setloadingInfo] = useState('-');
  const [readingInfo, setreadingInfo] = useState('-');
  const [predictInfo, setpredictInfo] = useState('-');
  const [resultInfo, setresultInfo] = useState('-');
  const [status, setStatus] = useState('');

  useEffect(() => {
    if (loadingStatus === 'succeed') {
      setloadingInfo(`${formatMessage({id: 'center.readed'})}${n_cols}${formatMessage({id: 'center.rows'})}${n_rows}${formatMessage({id: 'center.cols'})}，${formatMessage({id: 'center.spend'})}${loadTook}s`)
    } else if (loadingStatus === 'failed') {
      setloadingInfo(loadErrorMsg);
      setStatus('error');
    }
    if (readingStatus === 'succeed') {
      setreadingInfo(`${formatMessage({id: 'center.modalSize'})}${loadModelSize}，${formatMessage({id: 'center.spend'})}${readTook}s`)
    } else if (readingStatus === 'failed') {
      setreadingInfo(readErrorMsg)
      setStatus('error');
    }
    if (predictStatus === 'succeed') {
      setpredictInfo(`${formatMessage({id: 'center.spend'})}${predictTook}s`)
    } else if (predictStatus === 'failed') {
      setpredictInfo(predictErrorMsg)
      setStatus('error');
    }
    if (resultStatus === 'succeed') {
      setresultInfo(
        <>
          <p>{formatMessage({id: 'center.spend'})}{resultTook}s,<a download href={`/api/resource/${outputPath}?opt=download`}>{formatMessage({id: 'center.download'})}</a></p>
        </>
      )
      setStatus('finish');
    } else if (resultStatus === 'failed') {
      setresultInfo(resultErrorMsg);
      setStatus('error');
    }
  }, [loadingStatus, n_cols, n_rows, loadTook, readingStatus, loadModelSize, readTook, predictStatus, predictTook, resultStatus, resultTook, outputPath, loadErrorMsg, readErrorMsg, predictErrorMsg, resultErrorMsg])

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
        message.success(`${info.file.name} ${formatMessage({id: 'center.success'})}`);
        setUploadInfo(`${formatMessage({id: 'center.upload'})}${info.file.name}\n${formatMessage({id: 'center.size'})}${info.file.response.data.size}，${formatMessage({id: 'center.spend'})}${info.file.response.data.took}s`);
        // setCurrent(0);
        const stepObj = {
          step1: {
            uploadInfo: `${formatMessage({id: 'center.upload'})}${info.file.name}\n${formatMessage({id: 'center.size'})}${info.file.response.data.size}，${formatMessage({id: 'center.spend'})}${info.file.response.data.took}s`
          },
          current: 0
        };
        const params = {
          datasetName,
          modelName,
            param: {
              file_path: info.file.response.data.path,
              upload_took: info.file.response.data.took
            },
        }
        handleUpload(stepObj, params, indexParam)

        // dispatch({
        //   type: 'center/getBatchPredictJobname',
        //   payload: {
        //     datasetName,
        //     modelName,
        //     param: {
        //       file_path: info.file.response.data.path,
        //       upload_took: info.file.response.data.took
        //     },
        //     callback: (res) => {
        //       dispatch({
        //         type: 'center/predictModel',
        //         payload: {
        //           datasetName,
        //           modelName,
        //           batch_predict_job_name: res
        //         }
        //       })
        //     }
        //   }
        // })
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
