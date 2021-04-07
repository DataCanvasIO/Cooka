import React, { useState, useEffect } from 'react';
import Line from './Line';
import { withRouter } from 'umi';
import { formatMessage } from 'umi-plugin-locale';
import { getTrainingList, getModelDetail, getPredictJob, batchPredict } from '@/services/dataset';


const Params = ({ modelName, location: { query: { datasetName } } }) => {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = {
      datasetName,
      modelName
    };
    getModelDetail(params).then((originRes) => {
      const res = originRes.data;
      if (res.trials) {
        setLoading(false);
        const trials = res.trials;
        trials.param_names.push('Reward metric');
        trials.data.forEach(ele => {
          ele.params.push(ele.reward)
        });
        setData(trials);
      }
    })
  }, [datasetName, modelName])
  return (
    <div>
      {
        !loading ? (
          <Line data={data} />
        ) : (
          <div style={{ textAlign: 'center', color: '#c4c4c4' }}>{formatMessage({id: 'center.training'})}</div>
        )
      }
    </div>
  )
}
export default withRouter(Params);
