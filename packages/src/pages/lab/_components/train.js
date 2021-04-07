import React, { useEffect, useRef, useState } from 'react';
import { Button, Card, Col, Form, InputNumber, Radio, Row, Select, Slider } from 'antd';
import { connect } from 'dva';
import { withRouter } from 'umi';
import { formatMessage } from 'umi-plugin-locale';
import { CookaSlider } from 'components';
import LabelChart from './LabelChart/index.js';
import styles from '../index.less';
import { getDataRetrieve, getRecommendConfig, interTaskType } from '@/services/dataset';
import { makeToolTipFromMsgId } from '@/utils/util';
import { showNotification } from '@/utils/notice';
import { setLabel } from 'echarts/src/chart/bar/helper';
import { PartitionStrategy, PartitionClass, FeatureType } from '@/pages/common/appConst';


const { Option } = Select;

const defaultData = [{
  name: `${formatMessage({ id: 'extra.trainUnion' })}`,
  // name: '训练集',
  count: 80,
  color: 'rgba(49, 154, 228, 1)',
}, {
  name: `${formatMessage({id: 'extra.verifyUnion'})}`,
  // name: '验证集',
  count: 10,
  color: 'rgba(6, 194, 97, 1)',
}, {
  name: `${formatMessage({id: 'extra.testUnion'})}`,
  // name: '测试集',
  count: 10,
  color: 'rgba(225, 67, 68, 1)',
}];

const Train = ({ train: { labelName }, dispatch, location: { query: { datasetName } }}) => {

  const frameworkTypes = ['HyperGBM', 'DeepTables']  // first as default value

  const dataRef = useRef();

  const [partitionStrategy, setPartitionStrategy] = useState('train_validation_holdout');
  const [labelData, setLabelData] = useState(null);  // 标签对应的 data
  const [posLabelValues, setPosLabelValues] = useState(null);  // 正样本选择数据
  const [labelType, setLabelType] = useState('');   // 标签的 type
  const [experimentEngine, setExperimentEngine] = useState(frameworkTypes[0]);   // 标签的 type
  const [target, setTarget] = useState(labelName);  // 选择的标签列名
  const [posValue, setPosValue] = useState('');
  const [taskType, setTaskType] = useState(''); // 是否是二分类模型
  const [mode, setMode] = useState('quick');
  const [divisionNumber, setDivisionNumber] = useState(5);
  const [testPercentage, setTestPercentage] = useState(20);
  const [randomState, setRandomState] = useState(9527);
  const [dateValue, setDateValue] = useState('');
  const [partitionCol, setPartitionCol] = useState(null);
  const [labelTipVisible, setLabelTipVisible] = useState(false);
  const [binaryTipVisible, setBinaryTipVisible] = useState(false);
  const [sliderData, setSliderData] = useState(defaultData);
  const [features, setFeatures] = useState([]);

  const labelColArr = features?.filter(feature => feature.type === 'continuous' || feature.type === 'categorical') || [];
  const datetimeColArr = features?.filter(feature => feature.type === 'datetime') || [];

  const partitionColArray = features?.filter(feature => {
    if (feature.type === FeatureType.Categorical){
      if (feature.extension.value_count.length === 3){
        const labels = feature.extension.value_count.map( v => v.type);
        if (labels.indexOf(PartitionClass.Train) > -1
          && labels.indexOf(PartitionClass.Eval) > -1
          && labels.indexOf(PartitionClass.Test) > -1){
          return true
        }
      }
    }
    return false;
  }) || [];

  const hasPartitionCols = partitionColArray.length > 0 ;
  const hasDatetimeCols = datetimeColArr.length > 0 ;

  const [form] = Form.useForm();


  // 如果从数据探查的 去训练 按钮进来的 需要将该标签列以及其图表默认展示
  useEffect(() => {

    getDataRetrieve(datasetName).then((originRes) => {
      // 检查code
      if(originRes.code !== 0){
        showNotification('Response is: ' + JSON.stringify(originRes))
        return
      }

      // 检查特征
      const features = originRes.data.features;
      if(features.length  <= 0){
        showNotification('Features of  ' + datasetName + " is empty")
        return
      }

      // 包装数据
      features.forEach((item, index) => {
        item.key = index;
        if (item.type === 'continuous') {
          item.hData = [];
          item.extension.bins.map((bin) => {
            item.hData.push({
              value: [bin.begin, bin.end],
              count: bin.value
            })
          })
        } else if (item.type === 'datetime') {
          const hour = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24'];
          item.barHourData = [];
          const month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
          item.barMonthData = [];
          const week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
          item.barWeekData = [];
          item.barYearData = [];
          item.extension.by_hour.forEach((hourData, index) => {
            item.barHourData.push({
              time: hour[index],
              value: hourData
            })
          });
          item.extension.by_month.forEach((monthData, index) => {
            item.barMonthData.push({
              time: month[index],
              value: monthData
            })
          });
          item.extension.by_week.forEach((weekData, index) => {
            item.barWeekData.push({
              time: week[index],
              value: weekData,
            });
          });
          item.extension.by_year.forEach((yearData, index) => {
            item.barYearData.push({
              time: String(yearData['year']),
              value: yearData['value'],
            });
          });
        }
      });

      // 存储特征
      setFeatures(features);

      // 根据目标列和数据集和推荐参数
      getRecommendConfig(datasetName, target).then((recommendConfigResponse) => {

        if (recommendConfigResponse.code !== 0) {
          showNotification('Response is: ' + JSON.stringify(recommendConfigResponse))
          return
        }

        const config = recommendConfigResponse.data;

        setTarget(config.conf.label_col);
        setPosValue(config.conf.pos_label);
        setMode(config.conf.train_mode);
        setExperimentEngine(config.conf.engine);
        setPartitionStrategy(config.conf.partition_strategy);

        if(config.conf.partition_strategy === PartitionStrategy.Manual){
          setPartitionCol(config.conf.partition_col)
        }else if(config.conf.partition_strategy === PartitionStrategy.TrainValidationHoldout){
          defaultData[0].count = config.conf.train_validation_holdout.train_percentage;
          defaultData[1].count = config.conf.train_validation_holdout.validation_percentage;
          defaultData[2].count = config.conf.train_validation_holdout.holdout_percentage;
          setSliderData(defaultData);
          // V 0.1.1 has no random state
          const random_state = config.conf.train_validation_holdout.random_state;
          if( random_state !== undefined && random_state !== null){
            setRandomState(config.conf.train_validation_holdout.random_state);
          }
        }
        features.forEach(feature => {
          if (feature.name === config.conf.label_col) {
            setPosLabelValues(feature.extension.value_count);
            if (feature.type === 'continuous') {
              setLabelData(feature.hData);
            } else if (feature.type === 'categorical') {
              setLabelData(feature.extension.value_count);
            }
            setLabelType(feature.type);
          }
        });

        interTaskType(datasetName, config.conf.label_col).then((originRes) => {
          // todo check code
          const res = originRes.data;
          setTaskType(res.task_type);
        });

      })

    })
  }, [datasetName, target, labelName]);


  // 标签列 select
  const handleLabelChange = (val) => {
    setLabelTipVisible(false);

    // 更新标签列, 标签列更新后会重新渲染页面，包括重新按执行的目标列进行参数推荐
    setTarget(val);
  };

  const handleDateChange = (val) => {
    setDateValue(val)
  };

  const handlePartitionColChange = (val) => {
    setPartitionCol(val)
  };


  const onChange = value => {
    if (isNaN(value)) {
      return;
    }
    setDivisionNumber(value);
  };

  const onTestChange = value => {
    if (isNaN(value)) {
      return;
    }
    setTestPercentage(value);
  };

  // 数据分配标题
  const analysisTitle = (
    <>
      <Radio.Group onChange={(e) => setPartitionStrategy(e.target.value)} value={partitionStrategy} style={{ marginTop: 12 }}>
        <Radio value={PartitionStrategy.TrainValidationHoldout}>
          { formatMessage({ id: 'extra.testAndTrain' }) }
        </Radio>
        {/*<Radio value='cross_validation' style={{ marginLeft: 50 }}>{formatMessage({ id: 'train.crossVerified' })}</Radio>*/}
        {/*{<Radio value={PartitionStrategy.Manual} style={{ marginLeft: 50 }}>*/}
        {/*  { formatMessage({ id: 'train.partition.manual' }) }*/}
        {/*</Radio>}*/}
      </Radio.Group>
    </>
  );
  // 数据分配内容部分
  const getAnalysisContent = () => {
    if (partitionStrategy === PartitionStrategy.CrossValidation) {
      return (
        <>
          <dl>
            <dt>{formatMessage({ id: 'train.divisionNum' })}</dt>
          </dl>
          <Row>
            <Col span={12}>
              <Slider
                min={2}
                max={50}
                onChange={onChange}
                value={typeof divisionNumber === 'number' ? divisionNumber : 0}
                step={1}
                tooltipVisible={false}
              />
            </Col>
            <Col span={4}>
              <InputNumber
                min={2}
                max={50}
                style={{ margin: '0 16px' }}
                step={1}
                value={divisionNumber}
                // formatter={value => `${value}%`}
                onChange={onChange}
              />
            </Col>
          </Row>



          <dl>
            <dt>{formatMessage({id: 'train.testUnionPercentage'})}</dt>
          </dl>
          <Row>
            <Col span={12}>
              <Slider
                min={10}
                max={80}
                onChange={onTestChange}
                value={typeof testPercentage === 'number' ? testPercentage : 0}
                step={1}
                tooltipVisible={false}
              />
            </Col>
            <Col span={4}>
              <InputNumber
                min={10}
                max={80}
                style={{ margin: '0 16px' }}
                step={1}
                value={testPercentage}
                formatter={testPercentage => `${testPercentage}%`}
                onChange={onTestChange}
              />
            </Col>
          </Row>
          <Row>
            <Col span={18}>
              <div className={styles.barWrapper}>
                <div className={styles.cvdata} style={{ width: `${100 - testPercentage}%`, overflow: 'hidden' }}>
                  {
                    Array.apply(null,{length: divisionNumber}).map((_, index) => {
                      return (
                        <span style={{ flex: 1, backgroundColor: '#0090DC', borderRight: '1px solid #fff' }}/>
                      )
                    })
                  }
                </div>
                <div className={styles.testdata} style={{ flex: 1, width: `${testPercentage}%`, backgroundColor: '#E73B40'}}/>
              </div>
              <div className={styles.legend}>
                <div className={styles.number}>
                  <span className={styles.cvdataCir}/>
                  <span className={styles.symbol}>{formatMessage({id: 'train.cvdata'})}</span>
                </div>
                <div className={styles.type}>
                  <span className={styles.testCir}/>
                  <span className={styles.symbol}>{formatMessage({id: 'train.testUnion'})}</span>
                </div>
              </div>
            </Col>
          </Row>
        </>
      )
    } else if (partitionStrategy === PartitionStrategy.Manual) {
      // pass
      return <Select placeholder={handlePartitionColSelectorPlaceholder()} style={{ width: 300 }} disabled={!hasPartitionCols} onChange={handlePartitionColChange} value={partitionCol}>
        {
          partitionColArray.map((item, index) => {
            return (
              <Option value={item.name} key={index}>{item.name}</Option>
            )
          })
        }
      </Select>

  }else{
      return (
        <div>
          <dl>
            <dt>{formatMessage({id: 'train.random_split.seed'})}</dt>
          </dl>
          <Row>
              <InputNumber onChange={v => setRandomState(v)}  min={0} max={65535} value={randomState} style={{ width: 300 }} />
          </Row>
          <dl>
            <dt>{formatMessage({id: 'train.random_split.proportion'})}</dt>
          </dl>
          <Row style={{width: "90%"}}>
            <CookaSlider dataRef={dataRef} sliderData={sliderData}/>
          </Row>
        </div>
      )
    }
  };

  const handlePosChange = (val) => {
    setBinaryTipVisible(false);
    setPosValue(val)
  };

  const handleExperimentEngineChange = (val) => {
    setExperimentEngine(val)
  };


  // 训练
  const handleTrain = () => {

    let param =  {
      label_col: target, // 标签列
      pos_label: posValue,
      train_mode: mode, // 训练模式

      experiment_engine: experimentEngine,
      // holdout_percentage: data[2].count,  // 测试集比例
      // holdout_percentage: divisionNumber,  // 测试集比例
      datetime_series_col: dateValue // 日期列
    };
    param['partition_strategy'] = partitionStrategy;  // 数据分配模式
    if (partitionStrategy === PartitionStrategy.CrossValidation) {
      // todo add holdout
      param['cross_validation'] =  {
        n_folds: testPercentage,  // 分割数
        // holdout_percentage: data[2].count, todo add holdout_percentage to CV
      }
    } else if (partitionStrategy === PartitionStrategy.TrainValidationHoldout) {
      const data = dataRef.current.getData();
      param['train_validation_holdout'] = {
        train_percentage: data[0].count,
        validation_percentage: data[1].count,
        holdout_percentage: data[2].count,
        random_state: randomState,
      }
    }else if (partitionStrategy === PartitionStrategy.Manual) {
      param['partition_col'] = partitionCol;
    }else{
      // Handle exception
      showNotification('Unseen partition strategy: ' + partitionStrategy);
      return
    }

    const params = {
      datasetName,
      param,
    };

    if (params['param'].hasOwnProperty('label_col') && params['param']['label_col'] === undefined) {
      setLabelTipVisible(true);
      return;
    }
    if (params['param'].hasOwnProperty('pos_label') && params['param']['pos_label'] === '') {
      setBinaryTipVisible(true);
      return;
    }
    dispatch({
      type: 'train/train',
      payload: params
    })

  };

  const handleDatetimeSelectorPlaceholder = () => {
    if(hasDatetimeCols){
      return formatMessage({ id: 'train.datetimeColSelectorNoItem'})
    }else{
      return formatMessage({ id: 'train.select'})
    }
  }

  const handlePartitionColSelectorPlaceholder = () => {
    if(hasPartitionCols){
      return formatMessage({ id: 'train.partition.noPartitionCols'})
    }else{
      return formatMessage({ id: 'train.select'})
    }
  }


  const taskTypeMessageIdMapping = {
    multi_classification: "train.taskMultiClassification",
    binary_classification: "train.taskBinaryClassification",
    regression: "train.taskRegression",
  }

  const taskTypeMessageId = taskTypeMessageIdMapping[taskType]

  const makeBody = (content) => {
    return <span style={{ color: '#c4c4c4', marginLeft: 2 }}>{content}</span>
  }

   return (
    <Form form={form}>
      {/*<div className={styles.basic}>*/}

        <dl className={styles.tag}>
          <dt>
            <span>{formatMessage({id: 'train.tagCol'})}</span>
          </dt>
          <dd>
            <div>
              {makeBody(formatMessage({id: 'train.hintTarget'}))}
            </div>
            <span>
              <Select value={target} placeholder={formatMessage({id: 'train.select'})} style={{ width: 300, marginBottom: 20 }} onChange={handleLabelChange}>
                {
                  labelColArr && labelColArr.map(label => {
                    return (
                      <Option value={label.name}>{label.name}</Option>
                    )
                  })
                }
              </Select>
            </span>
            <Button type="primary" style={{ marginLeft: 10 }} onClick={handleTrain}>{formatMessage({id: 'train.train'})}</Button>
          </dd>
          {
            labelTipVisible ? (
              <div className={styles.labelTip} style={{ marginTop: -20 }}>{formatMessage({id: 'train.labelNotEmpty'})}</div>
            ) : null
          }
        </dl>
        <dl>
          {
            taskType.length !== 0 && (
              <>
                <dt>
                  {formatMessage({ id: 'train.taskType'})}
                  {makeToolTipFromMsgId('train.hintTaskType')}
                </dt>
                <dd>
                  <span style={{ color: '#c4c4c4', marginLeft: 2 }}>  {formatMessage({id: 'train.hintInferTaskType'}, {taskType: formatMessage({id: taskTypeMessageId}) })}   </span>
                </dd>
              </>
            )
          }
        </dl>
        <dl>
          <LabelChart labelType={labelType} labelData={labelData} style={ {width: 350 }} />
        </dl>
        {
          taskType === 'binary_classification' && (
            <dl className={styles.binary}>
              <dt>
                {formatMessage({id: 'train.normalSampleModal'})}
                {makeToolTipFromMsgId('train.hintPositiveLabel')}
              </dt>
              <dd>
                <Select value={posValue} placeholder={formatMessage({ id: 'train.select'})} style={{ width: 300 }} onChange={handlePosChange}>
                  {
                    posLabelValues && posLabelValues.map((item, index) => {
                      return (
                        <Option value={item.type} key={index}>{item.type}</Option>
                      )
                    })
                  }
                </Select>
              </dd>
              {
                binaryTipVisible ? (
                  <div className={styles.labelTip}>{formatMessage({id: 'train.posNotEmpty'})}</div>
                ) : null
              }
            </dl>
          )
        }
        <dl className={styles.mode}>
          <dt>{formatMessage({id: 'train.experimentEngine'})}
            {makeToolTipFromMsgId('train.hintExperimentEngine')}
          </dt>
          <dd>
            <Select value={experimentEngine} placeholder={formatMessage({ id: 'train.select'})} style={{ width: 300 }} onChange={v => {setExperimentEngine(v)}}>
              {
                frameworkTypes.map(v => {
                  return (
                    <Option value={v} key={v}>{v}</Option>
                  )
                })
              }
            </Select>
          </dd>
        </dl>
        <dl className={styles.mode}>
          <dt>{formatMessage({id: 'train.trainMode'})}
            {makeToolTipFromMsgId('train.hintTrainMode')}
          </dt>
          <dd>
            <Radio.Group onChange={e => setMode(e.target.value)} value={mode}>
              <Radio value='quick'>{formatMessage({id: 'train.quick'})}</Radio>
              <Radio value='performance'>{formatMessage({id: 'train.performance'})}</Radio>
              {/*<Radio value='minimal'>{formatMessage({id: 'train.minimal'})}</Radio>*/}
            </Radio.Group>
          </dd>
        </dl>
        <dl>
          <dt>
            {formatMessage({id: 'train.dataAllot'})}
            { makeToolTipFromMsgId('train.partition.hint') }
          </dt>
        </dl>
        <Card title={analysisTitle} style={{ width: '60%'}}>
          <div>
            {getAnalysisContent()}
          </div>
        </Card>
        <dl>
          <dt>{formatMessage({ id: 'train.datetimeCol' })}
            {makeToolTipFromMsgId('train.hintDatetimeSeriesFeature')}
          </dt>
          <dd>
            <Select placeholder={handleDatetimeSelectorPlaceholder()} style={{ width: 300 }} disabled={!hasDatetimeCols} onChange={setDateValue}>
              {
                  datetimeColArr.map((item, index) => {
                  return (
                    <Option value={item.name} key={index}>{item.name}</Option>
                  )
                })
              }
            </Select>
          </dd>
        </dl>
    </Form>
  )
}
export default withRouter(connect(({ dataset, train }) => (
  { dataset, train }
))(Train));
