import React, { useState, useEffect } from 'react';
import { Breadcrumb, Form, Input, Card, Button, Radio } from 'antd';
import { connect } from 'dva';
import { withRouter } from 'umi';
import Preview from '@/pages/common/previewDataset';
import Explore from '@/pages/common/exploreDataset';
import Train from './_components/train';
import Center from './_components/center';
import styles from './index.less';
import { formatMessage } from 'umi-plugin-locale';





const Lab = ({ dispatch, location: { query: { datasetName } }, train: { defaultTab } }) => {

  const contentConfig = {
    a: (<Preview datasetName={datasetName}/>),
    b: (<Explore datasetNameFromParam={datasetName} isTemporary={false}/>),
    c: (<Train />),
    d: (<Center />),
  }

  const [form] = Form.useForm();
  useEffect(() => {
    const tab = localStorage.getItem('tab') || defaultTab
    dispatch({
      type:'train/save',
      payload:{
        defaultTab:tab
      }
    })
  }, [])
  const datasetNameHtml = (
    <>
      <Form.Item style={{ float: 'left', marginRight: 10, marginTop: 20, visibility: 'hidden'}} name="datasetName" label="数据集名称">
        <Input />
      </Form.Item>
      <Button style={{float: 'right', marginTop: 20, visibility: 'hidden' }} type="primary">创建</Button>
    </>
  );
  const handleTitleChange = (e) => {
    localStorage.setItem('tab', e.target.value)
    dispatch({
      type:'train/save',
      payload:{
        defaultTab:e.target.value
      }
    })
  }
  const title = (
    <Radio.Group onChange={handleTitleChange} value={defaultTab}>
      <Radio.Button value="a">{formatMessage({id: 'extra.preview'})}</Radio.Button>
      <Radio.Button value="b">{formatMessage({id: 'extra.dataExplore'})}</Radio.Button>
      <Radio.Button value="c">{formatMessage({id: 'extra.train'})}</Radio.Button>
      <Radio.Button value="d">{formatMessage({id: 'extra.center'})}</Radio.Button>
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
          <Breadcrumb.Item>{formatMessage({id: 'extra.explore'})}</Breadcrumb.Item>
          <Breadcrumb.Item>{datasetName}</Breadcrumb.Item>
        </Breadcrumb>

      </div>
      <Card title={title} extra={datasetNameHtml}>
        {contentConfig[defaultTab]}
      </Card>
    </Form>
  );
}
export default withRouter(connect(({ dataset, train }) => (
  { dataset, train }
))(Lab));
