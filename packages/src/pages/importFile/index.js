import React, { useState, useEffect } from 'react';
import { Breadcrumb, Form, Input, Card, Button, Radio } from 'antd';
import { connect } from 'dva';
import { withRouter } from 'umi';
import router from 'umi/router';
import ImportFilePage from './_components/import';
import Preview from '@/pages/common/previewDataset';
import Explore from '@/pages/common/exploreDataset';
import {checkoutStepFromResponse} from '@/pages/common/createDataset';
import styles from './index.less';
import { formatMessage } from 'umi-plugin-locale';
import CreateDatasetFormPage from '@/pages/importFile/_components/createDatasetForm';
import { UploadStepType } from '@/pages/common/appConst';

const ImportFile = ({ importFile: { pollJobResponse }, dispatch }) => {


  const [form] = Form.useForm();
  const [defaultValue, setRadioValue] = useState('a');
  const [datasetNameVal, setDatasetNameVal] = useState(null);
  const [temporaryDatasetName, setTemporaryDatasetName] = useState(null);
  const [userInputDatasetName, setUserInputDatasetName] = useState(null);
  const [analyzeSucceed, setAnalyzeSucceed] = useState(false);

  // 分析结束后返回数据集名称回显
  const contentConfig = {
    a: (<ImportFilePage />),
    b: (<Preview datasetName={temporaryDatasetName} />),
    c: (<Explore datasetNameFromParam={temporaryDatasetName} isTemporary={true} />)
  }

  // 分析结束后返回数据集名称回显
  useEffect(() => {

    checkoutStepFromResponse(pollJobResponse, UploadStepType.analyze, (analyzeStep) => {
      // analyzeStep.extension.recommend_dataset_name
      if(analyzeStep.status === 'succeed'){
        setTemporaryDatasetName(pollJobResponse.data.temporary_dataset_name)
        setAnalyzeSucceed(true);
      }
    })
  }, [pollJobResponse]);


  // Create Events
  const handleCreate = () => {
    // todo check dataset name

    dispatch({
      type: 'dataset/createDataset',
      payload: {
        dataset_name: userInputDatasetName,
        temporary_dataset_name: temporaryDatasetName,
        callback: () => {
          router.push(`/lab?datasetName=${userInputDatasetName}`);
        }
      }
    })
  }
  // datasetName change events
  const handleDatasetNameChange = (e) => {
    setDatasetNameVal(e.target.value);
  }

  const datasetNameHtml = <CreateDatasetFormPage /> ;

  const handleTitleChange = (e) => {
    setRadioValue(e.target.value);
  }
  const title = (
    <Radio.Group onChange={handleTitleChange} defaultValue={defaultValue}>
      <Radio.Button value="a">{formatMessage({ id: 'import.import'})}</Radio.Button>
      {
        analyzeSucceed && (
          <>
            <Radio.Button value="b">{formatMessage({ id: 'extra.preview'})}</Radio.Button>
            <Radio.Button value="c">{formatMessage({ id: 'extra.dataExplore'})}</Radio.Button>
          </>
        )
      }
    </Radio.Group>
  )
  return (
    <Form
      form={form}
      initialValues={
        {
          n_rows: 1000
        }
      }
    >
      <div className={styles.breadcrumb}>
        <Breadcrumb>
          <Breadcrumb.Item>
            <a href="/">{formatMessage({id: 'extra.dataset'})}</a>
          </Breadcrumb.Item>
          <Breadcrumb.Item>{formatMessage({id: 'extra.new'})}</Breadcrumb.Item>
          <Breadcrumb.Item>{formatMessage({id: 'import.import'})}</Breadcrumb.Item>
        </Breadcrumb>

      </div>
      <Card title={title} extra={datasetNameHtml} style={{ paddingBottom: 60 }}>
        {contentConfig[defaultValue]}
      </Card>
    </Form>
  );
}
export default withRouter(connect(({ importFile, dataset }) => (
  { importFile, dataset }
))(ImportFile));
