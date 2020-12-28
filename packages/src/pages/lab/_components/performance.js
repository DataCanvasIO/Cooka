import React, { useState, useEffect } from 'react';
import { Table, Col, Row, List } from 'antd';
import { Hhistogram, CurveChart } from '@/components';
import { withRouter } from 'umi';
import { formatMessage } from 'umi-plugin-locale';
import { connect } from 'dva';
import styles from './index.less';
import { getTrainingList, getModelDetail, getPredictJob, batchPredict } from '@/services/dataset';
import { makeToolTipFromMsgId, makeToolTip, makeTableHeader } from '@/utils/util';

const MetricsConfig = [
  { value: 'explained_variance', name: 'EVS' },
  { value: 'neg_mean_absolute_error', name: 'MAE' }, // 下方有更新
  { value: 'neg_mean_squared_error', name: 'MSE' }, // 下方有更新
  { value: 'neg_mean_squared_log_error', name: 'MSLE' },
  { value: 'neg_median_absolute_error', name: 'MedianAE' },
  { value: 'r2', name: 'R2' },
  { value: 'accuracy', name: 'Accuracy' },
  { value: 'f1', name: 'F1' },
  { value: 'precision', name: 'Precision' },
  { value: 'recall', name: 'Recall' },
  { value: 'roc_auc', name: 'AUC' },
  { value: 'fbeta', name: 'FBeta' },
  { value: 'log_loss', name: 'Log Loss' },
  { value: 'rmse', name: 'RMSE' },
  { value: 'mse', name: 'MSE' },
  { value: 'mae', name: 'MAE' },
  { value: 'evs', name: 'EVS' },
  { value: 'msle', name: 'MSLE' },
]
const Performance = ({ modelName, location: { query: { datasetName } }, key }) => {
  const [confusion_matrix, setConfusionMatrix] = useState({});
  const [metrics, setMetrics] = useState({});
  const [roc_curve, setRocCurve] = useState({});
  const [taskType, setTaskType] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = {
      datasetName,
      modelName
    };
    getModelDetail(params).then((originRes) => {
      const res = originRes.data;
      if (res.performance) {
        setLoading(false);
        setConfusionMatrix(res.performance.confusion_matrix);
        setMetrics(res.performance.metrics);
        setRocCurve(res.performance.roc_curve);
        setTaskType(res.task_type)
      }
    })
  }, [datasetName, modelName])

  // Roc Chart Data
  let dataCurve = [];
  if (roc_curve) {
    const { false_positive_rate = [], true_positive_rate = [], thresholds = [] } = roc_curve;
    false_positive_rate.forEach(x => {
      dataCurve.push({
        x: x
      })
    });
    true_positive_rate.forEach((y, i) => {
      dataCurve[i]['y'] = y
    });
    thresholds.forEach((z, i) => {
      dataCurve[i]['z'] = z;
      dataCurve[i]['name'] = 'True positive rate';
    });
  }


  // 处理指标数据
  const dataF = [];
  Object.keys(metrics).forEach(item => {
    dataF.push({
      name: item.toLowerCase(),
      score: metrics[item],
    });
  });

  // 映射name
  const getname=(val) => {
    const result = MetricsConfig.filter((i) => i.value === val);
    if (result.length > 0) {
      return result[0].name;
    }
    return val;
  }

  const getPredictTitle = (type) => {
    if (confusion_matrix) {
      const { label = {} } = confusion_matrix;
      return (
        <div style={{ textAlign: 'center' }}>
          <span>{type === 'yes' ? label.true : label.false}</span>
        </div>
      );
    }

  }

  const getActually = (type) => {
    if (confusion_matrix) {
      const { label = {} } = confusion_matrix;
      return(
        <span>{type === 'yes' ? label.true : label.false}</span>
      );
    }
  }

  const getStyleValue = (type, value) => {
    return type === 'success' ?
     <span style={{color: '#13c2c2'}}>{value}</span>
     :
     <span style={{color: '#f5222d'}}>{value}</span>;
  }

  const metricMapping = {
    precision:'Precision',
    recall:'Recall',
    f1:'F1',
    accuracy:'Accuracy',
    roc_auc:'AUC',
  }

  const formatChartData = (matrixData) => {
    return ['accuracy', 'f1', 'recall', 'precision', 'roc_auc'].map((item, index) => ({
       y: metricMapping[item],
       x: matrixData[item] ? matrixData[item] : 0,
    }));
  }

  const chartData = formatChartData(metrics);

  const columns = [
    {
      title: '',
      children: [
        {
          title: formatMessage({id: 'center.actual'}),
          dataIndex: 'actual',
          key: 'actual',
          align: 'center',
        },
      ],
    },
    {
      title: formatMessage({id: 'center.evaluate.predict'}),
      children: [
        {
          title: getPredictTitle('yes'),
          dataIndex: "predicted_yes",
          align: 'center',
        },
        {
          title: getPredictTitle('no'),
          dataIndex: "predicted_no",
          align: 'center',
        },
        {
          title: "Total",
          dataIndex: "total",
          align: 'center',
        },
      ],

    },
  ];
  let dataSource = [];
  if (confusion_matrix ) {
    dataSource =  [
      {
        id: 'index',
        actual: getActually('yes'),
        predicted_yes: getStyleValue('success', confusion_matrix.tp),
        predicted_no: getStyleValue('failed', confusion_matrix.fn),
        total: confusion_matrix.tp + confusion_matrix.fn,
      },
      {
        id: 'index1',
        actual: getActually('no'),
        predicted_yes: getStyleValue('failed', confusion_matrix.fp),
        predicted_no: getStyleValue('success', confusion_matrix.tn),
        total: confusion_matrix.fp + confusion_matrix.tn,
      },
      {
        id: 'index2',
        actual: 'Total',
        predicted_yes: confusion_matrix.tp + confusion_matrix.fp,
        predicted_no: confusion_matrix.fn + confusion_matrix.tn,
        total: confusion_matrix.tp + confusion_matrix.fn + confusion_matrix.fp + confusion_matrix.tn,
      },
    ];
  }

  return (
    <>
      {
        !loading ? (
          <Row key={key}>
            {
              taskType === 'binary_classification' && (
                <Col span={24}>
                  <h3>{makeTableHeader('center.mix', 'center.hintConfusionMatrix')}</h3>
                  <Table
                    columns={columns}
                    dataSource={dataSource}
                    size='small'
                    bordered
                    pagination={false}
                    rowKey={record => record.actual}
                    />
                </Col>
              )
            }
            <h3 style={{ marginTop: 20 }}>{formatMessage({id: 'center.modalEvaluate'})}</h3>
            {
              taskType !== 'regression' ? (
                <Col span={24} style={{ marginTop: 10 }}>
                <Hhistogram data={chartData} />
              </Col>) : null
            }
            <Col span={24}>
              {
                dataF.length > 0 && (
                  <div className={styles.box}>
                    <List
                      dataSource={dataF}
                      renderItem={(d, i) => (
                        <List.Item>
                          <List.Item.Meta style={{ float: 'left' }} title={getname(d.name)} />
                          <div style={{ float: 'right' }}> { d.score && d.score.toFixed(4) }</div>
                        </List.Item>
                      )}
                    />
                  </div>
                )
              }
            </Col>
            {
              taskType === 'binary_classification' && (
                <Col span={24}>
                  <h3 style={{ marginTop: 20 }}>{formatMessage({id: 'center.roc'})}</h3>
                  <div style={{ width: 1000 }}>
                    <CurveChart
                      data={dataCurve}
                      height={500}
                    />
                  </div>
                </Col>
              )
            }
          </Row>
        ) : (
          <div style={{ textAlign: 'center', color: '#c4c4c4' }}>{formatMessage({id: 'center.training'})}</div>
        )
      }
    </>

  )
}
export default withRouter(connect(({ center }) => (
  { center }
))(Performance));
