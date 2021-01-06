import { withRouter } from 'umi';
import { connect } from 'dva';
import React from 'react';
import { CreateDatasetFormPage } from '@/pages/common/createDataset';

export default withRouter(connect(({ uploadFile }) => (
  { pollJobResponse: uploadFile.pollJobResponse }
))(CreateDatasetFormPage));
