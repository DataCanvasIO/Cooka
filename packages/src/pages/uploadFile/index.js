import React, { useState, useEffect } from 'react';
import { Breadcrumb, Form, Input, Card, Button, Radio, Tooltip } from 'antd';
import { connect } from 'dva';
import { withRouter } from 'umi';
import router from 'umi/router';
import UploadPage from './_components/upload';
import Preview from '@/pages/common/previewDataset'
import Explore from '@/pages/common/exploreDataset';
import styles from './index.less';
import { formatMessage } from 'umi-plugin-locale';
import CreateDatasetFromPage from '@/pages/uploadFile/_components/createDataseForm';
import { makeStepsDict } from '@/utils/util';

import { UploadStepType } from '@/pages/common/appConst';


const UploadFile = ({ uploadFile: {datasetName, pollJobResponse }, dispatch }) => {

  const [defaultValue, setRadioValue] = useState('a');
  const [analyzeSucceed, setAnalyzeSucceed] = useState(false);

  useEffect(() => {
    if (pollJobResponse !== null && pollJobResponse !== undefined) {
      const responseData = pollJobResponse.data;
      const stepsObject = makeStepsDict(responseData.steps);
      const analyzeStep = stepsObject[UploadStepType.analyze];
      if (analyzeStep !== undefined && analyzeStep !== null) {
        if ('succeed' === analyzeStep.status) {
          setAnalyzeSucceed(true);
        }
      }
    }
  }, [pollJobResponse])

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
    a: (<UploadPage />),
    b: (<Preview datasetName={datasetName}/>),
    c: (<Explore datasetNameFromParam={datasetName} isTemporary={true}/>)
  };

  const datasetNameHtml = <CreateDatasetFromPage /> ;

  return (
    <Form
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

// export default UploadFile;
