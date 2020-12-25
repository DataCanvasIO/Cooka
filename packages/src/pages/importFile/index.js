import React, { useState, useEffect } from 'react';
import { Breadcrumb, Form, Input, Card, Button, Radio } from 'antd';
import { connect } from 'dva';
import { withRouter } from 'umi';
import router from 'umi/router';
import Importpage from './_components/import';
import Preview from '@/pages/common/previewDataset';
import Explore from '@/pages/common/exploreDataset';
import styles from './index.less';
import { formatMessage } from 'umi-plugin-locale';
import { CreateDatasetForm } from '@/pages/common/createDataset';


const ImportFile = ({ importFile: { showTitle, datasetName, step3Status, params, recommendDatasetName }, dispatch }) => {
  const contentConfig = {
    a: (<Importpage />),
    b: (<Preview datasetName={datasetName} />),
    c: (<Explore datasetNameFromParam={datasetName} isTemporary={true} />)
  }
  const [form] = Form.useForm();
  const [defaultValue, setRadioValue] = useState('a');
  const [datasetNameVal, setDatasetNameVal] = useState(datasetName);
  // 分析结束后返回数据集名称回显

  // 分析结束后返回数据集名称回显
  useEffect(() => {
    if('succeed' === step3Status){
      form.setFieldsValue({
        btn: false,
        datasetName: recommendDatasetName,
      });
    }
  }, [form, datasetName, step3Status, recommendDatasetName]);

  const isGrey = datasetName && datasetName.length > 0 ? false : true; // 创建按钮是否置灰
  // Create Events
  const handleCreate = () => {
    dispatch({
      type: 'dataset/createDataset',
      payload: {
        dataset_name: form.getFieldValue()['datasetName'],
        temporary_dataset_name: params.temporary_dataset_name,
        callback: () => {
          router.push(`/lab?datasetName=${form.getFieldValue()['datasetName']}`);
        }
      }
    })
  }
  // datasetName change events
  const handleDatasetNameChange = (e) => {
    setDatasetNameVal(e.target.value);
  }

  const datasetNameHtml = <CreateDatasetForm form={form} temporaryDatasetName={datasetName} dispatch={dispatch}/> ;

  const handleTitleChange = (e) => {
    setRadioValue(e.target.value);
  }
  const title = (
    <Radio.Group onChange={handleTitleChange} defaultValue={defaultValue}>
      <Radio.Button value="a">{formatMessage({ id: 'import.import'})}</Radio.Button>
      {
        showTitle && (
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
