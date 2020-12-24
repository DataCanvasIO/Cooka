import React, { useState, useEffect } from 'react';
import { Breadcrumb, Form, Input, Card, Button, Radio, Tooltip } from 'antd';
import { connect } from 'dva';
import { withRouter } from 'umi';
import router from 'umi/router';
import Uploadpage from './_components/upload';
import Preview from '@/pages/common/previewDataset'
import Explore from '@/pages/common/exploreDataset';
import styles from './index.less';
import { formatMessage } from 'umi-plugin-locale';
import {CreateDatasetForm} from '@/pages/common/createDataset';

/**
 * 将分析任务详情的接口返回的数据包装成 k-v形式，例如：
 * {
 *   upload: {
 *     extension: {
 *       file_size: "10KB"
 *     },
 *     took: 100
 *   }
 * }
 * @param responseData
 */
function parseStepProcess(responseData) {
  const result = {};
  for (var step of responseData.steps){
    result[step.type] = step;
  }
  return result;
}

const StepType = {
  upload: 'upload',
  load:'load',
  analyze: 'analyzed',
};

const UploadFile = ({ uploadFile: {datasetName, responseData }, dispatch }) => {
  const [form] = Form.useForm();

  const [defaultValue, setRadioValue] = useState('a');
  const [analyzeSucceed, setAnalyzeSucceed] = useState(false);

  // 分析结束后返回数据集名称回显
  useEffect(() => {

    if(responseData !== null && responseData !== undefined) {
      const stepsObject = parseStepProcess(responseData);
      const analyzeStep = stepsObject[StepType.analyze];

      if(analyzeStep !== undefined && analyzeStep !== null){
        if('succeed' === analyzeStep.status){
          setAnalyzeSucceed(true);
          form.setFieldsValue({
            btn: false,
            datasetName: datasetName,
          });
        }
      }
    }

  }, [form, datasetName, responseData]);


  // form, datasetName,
  const datasetNameHtml = <CreateDatasetForm form={form} temporaryDatasetName={datasetName} dispatch={dispatch}/> ;

  const handleTitleChange = (e) => {
    setRadioValue(e.target.value);
  };
  const title = (
    <Radio.Group onChange={handleTitleChange} defaultValue={defaultValue}>
      <Radio.Button value="a">{formatMessage({id: 'upload.upload'})}</Radio.Button>
      {
        // 上传成功后再显示预览和数据探查
        analyzeSucceed && (
          <>
            <Radio.Button value="b">{formatMessage({ id: 'extra.preview'})}</Radio.Button>
            <Radio.Button value="c">{formatMessage({ id: 'extra.dataExplore'})}</Radio.Button>
          </>
        )
      }
    </Radio.Group>
  );

  const contentConfig = {
    a: (<Uploadpage />),
    b: (<Preview datasetName={datasetName}/>),
    c: (<Explore datasetNameFromParam={datasetName} isTemporary={true}/>)
  };

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
          <Breadcrumb.Item>{formatMessage({id: 'upload.uploadStep'})}</Breadcrumb.Item>
        </Breadcrumb>

      </div>
      <Card title={title} extra={datasetNameHtml} style={{ paddingBottom: 60 }}>
        {contentConfig[defaultValue]}
      </Card>
    </Form>
  );
}
export default withRouter(connect(({ uploadFile }) => (
  { uploadFile }
))(UploadFile));
