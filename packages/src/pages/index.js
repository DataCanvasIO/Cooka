import { formatMessage } from 'umi-plugin-locale';
import { Redirect } from 'umi';
export default function() {
  return (
    <Redirect to='/datasetList' />
  );
}
