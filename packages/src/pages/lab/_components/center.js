import React, { useEffect, useState } from 'react';
import { Collapse, Dropdown, Menu, Spin, Table, Tabs, Tooltip } from 'antd';
import { random } from 'lodash';
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


const Center = ({ train: { defaultPanel = null }, location: { query: { datasetName } }}) => {
  const [rows, setRows] = useState([]);
  const [listData, setListData] = useState([]);
  const [data, setData] = useState([]);
  const [notebookPortal, setNotebookPortal] = useState('');

  const handleFetchList = async () => {
    const params = { datasetName }
    const originRes = await getTrainingList(params);
    const res = originRes.data;

    // fix expand one item make effect to all(need a field named 'key' )
    setListData(res.experiments.map(v => {
      v.key = v.no_experiment;
      return v;
    }));

    setNotebookPortal(res.notebook_portal);

    const statusArray = res.experiments.map(v => v.status)

    if(!statusArray.includes('running')) {
      clearInterval(experimentListInterval);
      experimentListInterval = null;
    }
  }

  useEffect(() => {
    handleFetchList();

    if (experimentListInterval !== null && experimentListInterval !== undefined){
      clearInterval(experimentListInterval);  // fix multiple interval running
    }

    experimentListInterval = setInterval(handleFetchList, Config.REFRESH_EXPERIMENT_LIST_TIMEOUT)
  }, [handleFetchList])  // useEffect as page init


  const callback = (key) => {
    console.log(key);
  }

  const viewLog = (path) => {
    window.open(`/api/resource/${path}?opt=head&n=1000`)
  }

  const viewSourceCode = (path) => {
    window.open(`/api/resource/${path}?opt=head&n=-1`)
  }

  const viewNotebook = (path) => {
      window.open(`${notebookPortal}/notebooks/${path}`)
  }

  const batchPredictStepType = {
    upload: 'upload',
    load: 'load',
    load_model: 'load_model'
  }

  const localTrainMode = (mode) => {
    if (mode === 'minimal') {
      return formatMessage({ id: 'train.minimal'})
    } else if (mode === 'quick') {
      return formatMessage({ id: 'train.quick'})
    } else if (mode === 'performance') {
      return formatMessage({ id: 'train.performance'})
    }
  };
  const metricDisplayMapping = {
    auc: "AUC",
    accuracy: "Accuracy",
    rmse: "RMSE"
  }

  const getOptionMenu = (record) => {
    return (
      <Menu>
        <Menu.Item>
             <span style={{ color: '#1890ff', cursor: 'pointer'}}  onClick={() => {viewLog(record.log_file_path);}} >
               {formatMessage({id: 'center.log'})}
             </span>
        </Menu.Item>
        <Menu.Item>
          <span style={{ color: '#1890ff', cursor: 'pointer'}} onClick={() => {viewSourceCode(record.train_source_code_path);}} >{formatMessage({id: 'center.source'})}</span>
        </Menu.Item>
        <Menu.Item>
          <span style={{ color: '#1890ff', cursor: 'pointer'}} onClick={() => {viewNotebook(record.train_notebook_uri);}} >{formatMessage({id: 'center.titleNotebook'})}</span>
        </Menu.Item>
      </Menu>
    )
  }

  const formatTrainMode = {
    [Config.TrainMode.Quick]: formatMessage({id: 'train.quick'}),
    [Config.TrainMode.Performance]: formatMessage({id: 'train.performance'}),
    [Config.TrainMode.Minimal]: formatMessage({id: 'train.minimal'}),
  }


  const columns = [
    {
      title: '',
      dataIndex: 'status',
      key: 'status',
      render: (_, record) => {
        if (record.status === 'running') {
          return (
            <Spin indicator={antIcon} />
          )
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
        return formatTrainMode[val];
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
              <span>{val.toFixed(6)}({metricDisplayMapping[record.metric_name]})</span>
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
      dataIndex: 'max_train_trail_no',
      key: 'max_train_trail_no',
      render: (text, record, index) => {
        const displayContent = `${record.train_trail_no}/${record.max_train_trail_no}`
        if(record.status === 'succeed'){
          if (record.train_trail_no !== record.max_train_trail_no){
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
          <Dropdown overlay={getOptionMenu(record)} placement='bottomCenter'>
            <a>...</a>
          </Dropdown>
        )
      }
    },

  ];

  const loadMoreContent = () => (
    <div
      style={{
        textAlign: 'center',
        paddingTop: 40,
        paddingBottom: 40,
        border: '1px solid #e8e8e8',
      }}
    >
      <Spin tip="Loading..." />
    </div>
  )

  const getGuid = () =>
    'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      /* eslint-disable */
      let r = (Math.random() * 16) | 0,
        v = c == 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });

  const fetchData = (startIndex = 0) =>
    new Promise(resolve => {
      setTimeout(() => {
        resolve(
          startIndex >= 500 // 总共只有500条数据
            ? []
            : Array.from({ length: 50 }).map((_, i) => {
              // 每次返回100条
              const index = startIndex + i;
              return {
                key: getGuid(),
                index: `${index}`,
                name: 'John Brown',
                age: 32,
                address: 'New York No. 1 Lake Park',
              };
            }),
        );
      }, random(0, 1.0) * 1000);
    });

  const columns1 = [
    {
      title: 'index',
      dataIndex: 'index',
      render: text => text,
      width: 50,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      width: 100,
    },
    {
      title: 'Age',
      width: 50,
      dataIndex: 'age',
    },
    {
      title: 'Address',
      width: 200,
      dataIndex: 'address',
    },
  ];
  const handleFetch = ({ page, pageSize }) => {
    console.warn('loading', { page, pageSize });

    const startIndex = (page - 1) * pageSize;

    fetchData(startIndex, pageSize).then(data =>
        {setData(data)}
    );
  };


  return (
    <div>
      <Table
        dataSource={listData}
        columns={columns}
        pagination={false}
        expandable={{
          expandedRowRender: record => {
            if (record.status === 'succeed' || record.status === 'running') {
              return (
                <Tabs onChange={callback} type="card">
                  <TabPane tab={formatMessage({id: 'center.evaluate'})} key="1">
                    <Performance
                      modelName={record.name}
                      key={record.key}
                    />
                  </TabPane>
                  <TabPane tab={formatMessage({id: 'center.predict'})} key="2">
                    {
                      <Prediction
                        modelName={record.name}
                        taskStatus={record.status}
                      />
                    }
                  </TabPane>
                  <TabPane tab={formatMessage({id: 'center.param'})} key="3">
                    <Params
                      modelName={record.name}
                    />
                  </TabPane>
                </Tabs>
              )
            } else if (record.status === 'failed') {
                return (
                  // eslint-disable-next-line react/jsx-no-target-blank
                  <div style={{ textAlign: 'center', color: '#c4c4c4' }}>{formatMessage({id: 'center.fail'})}<a onClick={() => {viewLog(record.log_file_path);}} target="_blank">{formatMessage({id: 'center.bug'})}</a></div>
                )
            }
          },
        }}
      />
    </div>
  )
}

export default withRouter(connect(({train}) => (
  {train}
))(Center));

// export default withRouter(Center);
