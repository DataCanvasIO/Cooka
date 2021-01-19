import React from 'react';
import { Dropdown, Menu, Spin, Table, Tabs, Tooltip } from 'antd';
import { CheckOutlined, CloseOutlined, LoadingOutlined } from '@ant-design/icons';
import { connect } from 'dva';
import { withRouter } from 'umi';
import { convertByteUnits, getDuration, makeTableHeader, makeToolTip, makeToolTipFromMsgId } from '@/utils/util';
import Performance from './performance';
import Prediction from './prediction';
import Params from './params';
import { formatMessage } from 'umi-plugin-locale';
import { getTrainingList } from '@/services/dataset';
import * as Config from '@/pages/common/appConst';

const { TabPane } = Tabs;
const antIcon = <LoadingOutlined style={{ fontSize: 16 }} spin />;

let experimentListInterval;


class Center extends React.Component {

  batchPredictStepType = {
    upload: 'upload',
    load: 'load',
    load_model: 'load_model',
  };
  metricDisplayMapping = {
    auc: 'AUC',
    accuracy: 'Accuracy',
    rmse: 'RMSE',
  };
  formatTrainMode = {
    [Config.TrainMode.Quick]: formatMessage({ id: 'train.quick' }),
    [Config.TrainMode.Performance]: formatMessage({ id: 'train.performance' }),
    [Config.TrainMode.Minimal]: formatMessage({ id: 'train.minimal' }),
  };

  constructor(props) {
    super(props);
    this.state = {
      listData: [],
      notebookPortal: '',
    };
    this.datasetName = this.props.location.query.datasetName;
  }

  handleFetchList() {
    const datasetName = this.datasetName;

    getTrainingList(datasetName).then(response => {
      const res = response.data;
      // fix expand one item make effect to all(need a field named 'key' )
      this.setState(
        {
          listData: res.experiments.map(v => {
            v.key = v.no_experiment;
            return v;
          }),
          notebookPortal: res.notebook_portal,
        },
      );

      const statusArray = res.experiments.map(v => v.status);
      if (!statusArray.includes('running')) {
        clearInterval(experimentListInterval);
        experimentListInterval = null;
      }
    });
  }

  componentDidMount() {
    if (experimentListInterval !== null && experimentListInterval !== undefined) {
      clearInterval(experimentListInterval);  // fix multiple interval running
    }
    this.handleFetchList();
    experimentListInterval = setInterval(this.handleFetchList.bind(this), Config.REFRESH_EXPERIMENT_LIST_TIMEOUT);
  }

  componentWillUnmount() {
    if (this.timer != null) {
      clearInterval(this.timer);
    }
  }

  viewLog = (path) => {
    window.open(`/api/resource/${path}?opt=head&n=1000`);
  };

  viewSourceCode = (path) => {
    window.open(`/api/resource/${path}?opt=head&n=-1`);
  };

  viewNotebook = (path) => {
    window.open(`${this.state.notebookPortal}/notebooks/${path}`);
  };

  localTrainMode = (mode) => {
    if (mode === 'minimal') {
      return formatMessage({ id: 'train.minimal' });
    } else if (mode === 'quick') {
      return formatMessage({ id: 'train.quick' });
    } else if (mode === 'performance') {
      return formatMessage({ id: 'train.performance' });
    }
  };

  getOptionMenu = (record) => {
    return (
      <Menu>
        <Menu.Item>
             <span style={{ color: '#1890ff', cursor: 'pointer' }} onClick={() => {
               this.viewLog(record.log_file_path);
             }}>
               {formatMessage({ id: 'center.log' })}
             </span>
        </Menu.Item>
        <Menu.Item>
          <span style={{ color: '#1890ff', cursor: 'pointer' }} onClick={() => {
            this.viewSourceCode(record.train_source_code_path);
          }}>{formatMessage({ id: 'center.source' })}</span>
        </Menu.Item>
        <Menu.Item>
          <span style={{ color: '#1890ff', cursor: 'pointer' }} onClick={() => {
            this.viewNotebook(record.train_notebook_uri);
          }}>{formatMessage({ id: 'center.titleNotebook' })}</span>
        </Menu.Item>
      </Menu>
    )
  }

  columns = [
    {
      title: '',
      dataIndex: 'status',
      key: 'status',
      render: (_, record) => {
        if (record.status === 'running') {
          return (
            <Spin indicator={antIcon}/>
          );
        } else if (record.status === 'succeed') {
          return (
            <CheckOutlined style={{ fontSize: 16, color: 'green'}} />
          )
        } else if (record.status === 'failed') {
          return (
            <CloseOutlined style={{ fontSize: 16, color: 'red'}} />
          )
        }
      }
    },
    {
      title: formatMessage({id: 'center.modal'}),
      dataIndex: 'no_experiment',
      key: 'no_experiment'
    },
    {
      title: formatMessage({id: 'center.titleEngine'}),
      dataIndex: 'engine',
      key: 'engine',
    },
    {
      title: formatMessage({id: 'train.trainMode'}),
      dataIndex: 'train_mode',
      key: 'train_mode',
      render: (val) => {
        return this.formatTrainMode[val];
      }
    },
    {
      title: <>{formatMessage({id: 'center.target'})}{ makeToolTipFromMsgId('center.hintOptimizeMetric') } </>,
      dataIndex: 'score',
      key: 'score',
      render: (text, record, index) => {
        const val = record.score;
        if (val) {
          return (
            <Tooltip placement="right" color={'white'} title={formatMessage({id: 'center.hintTargetCol'}, {targetCol: record.target_col})}>
              <span>{val.toFixed(6)}({this.metricDisplayMapping[record.metric_name]})</span>
            </Tooltip>
          )
        } else {
          return (
            <span>-</span>
          )
        }
      }
    },
    {
      title: makeTableHeader('center.process', 'center.hintProgress'),
      dataIndex: 'max_train_trial_no',
      key: 'max_train_trial_no',
      render: (text, record, index) => {
        const displayContent = `${record.train_trial_no}/${record.max_train_trial_no}`
        if(record.status === 'succeed'){
          if (record.train_trial_no !== record.max_train_trial_no){
            return makeToolTip(<span style={ {color: 'orange'} }>{displayContent}</span>, formatMessage({id: 'center.hintEarlyStopping'}))
          }else {
            return <span>{displayContent}</span>
          }
        }else{
          return <span>{displayContent}</span>
        }
      }
    },
    {
      title: makeTableHeader('center.remain', 'center.hintRemainingTime'),
      dataIndex: 'estimated_remaining_time',
      key: 'estimated_remaining_time',
      render: (val) => {
        if (val === 0) {
          return (
            <span>{formatMessage({id: 'center.finished'})}</span>
          )
        } else if (val) {
          const sty = val > 3600 ? { color: 'red' } : {}
          return (
            <span style={sty}>{getDuration(val)}</span>
          )
        }else{
          return <span>-</span>
        }
      }
    },
    {
      title:  makeTableHeader('center.spend', 'center.hintElapsed'),
      dataIndex: 'escaped',
      key: 'escaped',
      render: (val) => {
        const sty = val > 3600 ? { color: 'red' } : {}
        return (
          <span style={sty}>{getDuration(val)}</span>
        )
      }
    },
    {
      title: makeTableHeader('center.size', 'center.hintModelSize'),
      dataIndex: 'model_file_size',
      key: 'model_file_size',
      render: (val) => {
        if (val) {
          return (
            <span>{convertByteUnits(val)}</span>
          )
        } else {
          return (
            <span>-</span>
          )
        }
      }
    },

    {
      title: makeTableHeader('center.titleResource', 'center.hintResource'),
      dataIndex: 'train_notebook_uri',
      align: 'center',
      key: 'train_notebook_uri',
      render: (text, record, index) => {
        return (
          <Dropdown overlay={this.getOptionMenu(record)} placement='bottomCenter'>
            <a>...</a>
          </Dropdown>
        )
      }
    },

  ];

  loadMoreContent = () => (
    <div
      style={{
        textAlign: 'center',
        paddingTop: 40,
        paddingBottom: 40,
        border: '1px solid #e8e8e8',
      }}
    >
      <Spin tip="Loading..."/>
    </div>
  );

  render() {
    return (
      <div>
        <Table
          dataSource={this.state.listData}
          columns={this.columns}
          pagination={false}
          expandable={{
            expandedRowRender: record => {
              if (record.status === 'succeed' || record.status === 'running') {
                return (
                  <Tabs onChange={(key) => console.log(key)} type="card">
                    <TabPane tab={formatMessage({ id: 'center.evaluate' })} key="1">
                      <Performance
                        modelName={record.name}
                        key={record.key}
                      />
                    </TabPane>
                    <TabPane tab={formatMessage({ id: 'center.predict' })} key="2">
                      {
                        <Prediction
                          modelName={record.name}
                          taskStatus={record.status}
                        />
                      }
                    </TabPane>
                    <TabPane tab={formatMessage({ id: 'center.param' })} key="3">
                      <Params
                        modelName={record.name}
                      />
                    </TabPane>
                  </Tabs>
                );
              } else if (record.status === 'failed') {
                return (
                  // eslint-disable-next-line react/jsx-no-target-blank
                  <div style={{ textAlign: 'center', color: '#c4c4c4' }}>{formatMessage({ id: 'center.fail' })}<a
                    onClick={() => {
                      this.viewLog(record.log_file_path);
                    }} target="_blank">{formatMessage({ id: 'center.bug' })}</a></div>
                );
              }
            },
          }}
        />
      </div>
    );
  }
}


export default withRouter(connect(({train}) => (
  {train}
))(Center));

// export default withRouter(Center);
