import React, { useState, useEffect } from 'react';
import Line from './Line';
import { withRouter } from 'umi';
import { formatMessage } from 'umi-plugin-locale';
import { getTrainingList, getModelDetail, predictModel, getBatchPredictJobname } from '@/services/dataset';


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
      if (res.trails) {
        setLoading(false);
        setData(res.trails);
      }
    })
  }, [modelName])
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
