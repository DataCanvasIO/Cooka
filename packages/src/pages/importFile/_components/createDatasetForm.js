import { withRouter } from 'umi';
import { connect } from 'dva';
import { CreateDatasetFormPage } from '@/pages/common/createDataset';

export default withRouter(connect(({ importFile }) => (
  { pollJobResponse: importFile.pollJobResponse }
))(CreateDatasetFormPage));

