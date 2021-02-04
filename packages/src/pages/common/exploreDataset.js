import React, { useState, useEffect } from 'react';
import { Input, Table, Tooltip, Radio, Popover, Spin, Button } from 'antd';
import {
  CheckOutlined,
  CloseOutlined,
} from '@ant-design/icons';
import { connect } from 'dva';
import { withRouter } from 'umi';
import { HBChart, Pie, BarChart } from '@/components';
import { toPercent } from '@/utils/util';
import styles from './exploreDataset.less';
import { formatMessage } from 'umi-plugin-locale';
import _ from 'lodash';
import { getDataRetrieve } from '@/services/dataset';
import { makeTableHeader } from '@/utils/util';


const { Search } = Input;

const colorConfig = {
  continuous: '#00b7b6',
  categorical: '#009cea',
  datetime: '#f49431',
  text: '#7d00f9'
}

const displayFeatureType = {
  continuous: formatMessage({id:'explore.num' }),
  categorical: formatMessage({id:  'explore.category'}),
  datetime: formatMessage({id: 'explore.date'}),
  text: formatMessage({id:  'explore.text'}),
}



function getColorStyle(needColor, color){
  if (needColor){
    return {color: color}
  }else{
    return {}
  }
}


let originalData = [];


const Explore = ({ dispatch, datasetNameFromParam, isTemporary ,location: { query: { datasetName } }  }) => {

  if (datasetName == null){
    datasetName = datasetNameFromParam
  }



  const [defaultValue, setDefaultValue] = useState('year');
  const [featuresData, setFeaturesData] = useState([]);
  const [n_rows, setNrows] = useState('');
  const [number, setNumber] = useState('');
  const [type, setType] = useState('');
  const [date, setDate] = useState('');
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(true);
  const [labelCol, setLabelCol] = useState('');
  const [defaultTab, setDefaultTab] = useState('a');
  const [sampleInfo, setSampleInfo] = useState(null);
  // const [originalData, setOriginalData] = useState([]);

  useEffect(() => {

    getDataRetrieve(datasetName).then((response) => {
      const res = response.data;

      if (res) {
        setLoading(false);
        const number = res.feature_summary.continuous;
        const type = res.feature_summary.categorical;
        const date = res.feature_summary.datetime;
        const text = res.feature_summary.text;
        const features = res.features;
        const n_rows = res.n_rows;
        const labe_col = res.label_col;
        originalData = _.cloneDeep(features);

        if (features.length) {
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
                  value: weekData
                })
              });
              item.extension.by_year.forEach((yearData, index) => {
                item.barYearData.push({
                  time: String(yearData['year']),
                  value: yearData['value']
                })
              })
            }
          })
        }
        setLabelCol(labe_col);
        setFeaturesData(features);
        setNrows(n_rows);
        setNumber(number);
        setType(type);
        setDate(date);
        setText(text);

        const sampleConfData = res.extension.sample_conf;
        let sampleInfoStr;
        if (sampleConfData.sample_strategy === 'random_rows'){
          sampleInfoStr = formatMessage({id: 'explore.hintSampling'}, {samplingData: `${sampleConfData.n_rows} ${formatMessage({id: 'explore.row'})}`})
        }else if (sampleConfData.sample_strategy === 'by_percentage'){
          sampleInfoStr = formatMessage({id: 'explore.hintSampling'}, {samplingData: `${sampleConfData.percentage}%`});
        } else{
          sampleInfoStr = formatMessage({id: 'explore.hintNoSampling'});
        }
        setSampleInfo(sampleInfoStr);
      }
    })
  }, [datasetName])

  const onMouseOverHandler = (e) => {
    // console.info(e.target.lastElementChild.style.visibility)
    const lastElement = e.target.lastElementChild
    console.info(lastElement.className);
    if(lastElement.className === 'go2train'){
      const current = e.target.lastElementChild.style.visibility
      if(current !== 'visible'){
        // visible none inline hidden
        e.target.lastElementChild.style.visibility = 'visible'
      }
    }
  }

  const onMouseLeaveHandler = (e) => {
    console.info(e.target.lastElementChild)
    console.info(e.target.children)
    // const current = e.target.lastElementChild.style.visibility
    //
    // if(current !== 'hidden'){
    //   // visible none inline hidden
    //   e.target.lastElementChild.style.visibility = 'hidden'
    // }

  }

  const gotoTrain = (userTarget) => {

    dispatch({
      type: 'train/save',
      payload: {
        defaultTab: 'c',
        labelName: userTarget
      }
    })
  }

  // 过滤
  const handleSearch = (e) => {
    const val = e.target.value;
    // const originalData = _.cloneDeep(featuresData);
    if (val.length === 0) {
      setFeaturesData(originalData)
    } else {
      setFeaturesData(originalData)
      const newData = originalData.filter(item => item.name.indexOf(val) > -1);
      setFeaturesData(newData)
    }
  }
  const handleTitleChange = (e) => {
    setDefaultValue(e.target.value);
  }

  const handleChange = (e) => {
    setDefaultTab(e.target.value);
  }

  const columns = [
    {
      title: formatMessage({id: 'explore.name'}),
      dataIndex: 'name',
      render: (_, record) => {
        const datasetName = record.name;
        return isTemporary ? <span> {record.name}</span> :
          <div >
            <Tooltip placement="right"
                     arrowPointAtCenter={true}
                     title={<a onClick={v => {gotoTrain(datasetName) } }>{formatMessage({id: 'explore.goTrain'})} </a> } color={'white'}>
              <span>
                {datasetName}
              </span>
            </Tooltip>
            {
              datasetName === labelCol ? (
                <span style={{width: 65, height: 20, backgroundColor: '#cecece', borderRadius: '5px 5px 5px 5px', textAlign: 'center', marginLeft: 2}}>
                      <span style={{color: 'black'}}>{`${formatMessage({id: 'explore.labelCol'})}`}</span>
                  </span>): null
            }
          </div>
        // return <span> {record.name}</span>
      }
    },
    {
      title: makeTableHeader('explore.type', 'explore.hintType'),
      dataIndex: 'type',
      render: (text, record, index) => {
        return (
          <>
            <span style={{ display: 'inline-block', width: 8, height: 8, backgroundColor: colorConfig[record.type], borderRadius: '50%', marginRight: 4 }}/>
            <span>{displayFeatureType[record.type]}</span>
          </>
        )
      }
    },
    {
      title: makeTableHeader('explore.dataType', 'explore.hintDataType'),
      dataIndex: 'data_type',
      render: (text, record, index) => {
        return (
          <>
            <span>{record.data_type}</span>
          </>
        )
      }
    },
    {
      title: makeTableHeader('explore.missing', 'explore.hintMissing', {samplingInfo: sampleInfo}) ,
      dataIndex: 'missing',
      render: (val) => {
        const missingPercentage = val.percentage.toFixed(2);
        const makeMissingValueBlock = (redFont=false) => {
          return <span style={getColorStyle(redFont, 'red')}>{missingPercentage}%({val.value})</span>
        }
        if( val.status === 'too_high'){
          return <Tooltip placement="right" color={'white'} title={formatMessage({id: 'explore.tooMuchMissing'})}>
                  {makeMissingValueBlock(true)}
                 </Tooltip>
        }else{
          return makeMissingValueBlock(false)
        }
      }
    },
    {
      title: makeTableHeader('explore.diff', 'explore.hintUniques', {samplingInfo: sampleInfo}) ,
      dataIndex: 'unique',
      render: (val) => {

        const makeUniqueValueBlock = (redFont) => {
          return <span style={getColorStyle(redFont, 'red')}>{val.value}</span>
        }

        const makeUniqueBlock = (msgId) => {
          return <Tooltip placement="right" color={'white'} title={formatMessage({id: msgId})}>
                  {makeUniqueValueBlock(true)}
                </Tooltip>
        }

        if (val.status === 'stable'){
          return makeUniqueBlock('explore.stableFeature')
        }else if (val.status === 'ID-ness'){
          return makeUniqueBlock('explore.idNess')
        } else{
          return makeUniqueValueBlock(false)
        }
      }

    },
  ];

  const renderCorrelation = {
    title: makeTableHeader('explore.correlation', 'explore.hintCorrelation'),
    dataIndex: 'correlation',
    render: (val) => {
      const correlation = val !== null? val.value: null;

      const makeCorrelationValueBlock = () => {
        let v ;
        if(correlation !== null && correlation !== undefined){
            v = correlation.toFixed(2);
        }else{
          v = "--"
        }
        return <span>{v}</span>
      }

      const makeCorrelationBlock = (msgId) => {
        return <Tooltip placement="right" color={'white'} title={formatMessage({id: msgId})}>
                <span style={{ color: 'orange' }}>{correlation.toFixed(2)}</span>
              </Tooltip>
      }

      if (correlation !== null && correlation !== undefined){
        if(val.status === 'too_high'){
          return makeCorrelationBlock('explore.correlationTooHigh')
        }else if(val.status === 'too_low'){
          return makeCorrelationBlock('explore.correlationTooLow')
        }else{
          return makeCorrelationValueBlock()
        }
      }else {
        return makeCorrelationValueBlock()
      }
    }
  }

  if (labelCol != null && labelCol.length > 0){
    // append correlation
    columns.push(renderCorrelation)
  }


  const numberPercent = toPercent((number / (number + type + date + text)), 0);
  const typePercent = toPercent((type / (number + type + date + text)), 0);
  const datePercent = toPercent((date / (number + type + date + text)), 0);
  const textPercent = toPercent((text / (number + type + date + text)), 0);
  const typeBorderStyle = (date === 0 && text === 0) ? { borderRadius: '0px 20px 20px 0' } : '';  // 如果日期和文本为0 则给类别加 border-radius
  const dateBorderStyle = text === 0 ? { borderRadius: '0px 20px 20px 0' } : '';  // 如果文本为0 则给类别加 border-radius

  return (
    <div>
      {
        !loading ? (
          <>
            <div className={styles.bar}>
              <div className={styles.number} style={{ width: `${numberPercent}` }}>{number} {`${formatMessage({id: 'explore.cols'})}`}({numberPercent})</div>
              <div className={styles.type} style={{ width: `${typePercent}`, ...typeBorderStyle }}>{type} {`${formatMessage({id: 'explore.cols'})}`}({typePercent})</div>
              <div className={styles.date} style={{ width: `${datePercent}`, ...dateBorderStyle }}>{date} {`${formatMessage({id: 'explore.cols'})}`}({datePercent})</div>
              <div className={styles.text} style={{ width: `${textPercent}` }}>{text} {`${formatMessage({id: 'explore.cols'})}`}({textPercent})</div>
            </div>
            <div className={styles.legend}>
              <div className={styles.number}>
                <span className={styles.numberCir}></span>
                <span className={styles.symbol}>{`${formatMessage({id: 'explore.num'})}`}</span>
                <span className={styles.comment}>{number} {`${formatMessage({id: 'explore.cols'})}`}，{numberPercent}</span>
              </div>
              <div className={styles.type}>
                <span className={styles.typeCir}></span>
                <span className={styles.symbol}>{`${formatMessage({id: 'explore.category'})}`}</span>
                <span className={styles.comment}>{type} {`${formatMessage({id: 'explore.cols'})}`}，{typePercent}</span>
              </div>
              <div className={styles.date}>
                <span className={styles.dateCir}></span>
                <span className={styles.symbol}>{`${formatMessage({id: 'explore.date'})}`}</span>
                <span className={styles.comment}>{date} {`${formatMessage({id: 'explore.cols'})}`}，{datePercent}</span>
              </div>
              <div className={styles.text}>
                <span className={styles.textCir}></span>
                <span className={styles.symbol}>{`${formatMessage({id: 'explore.text'})}`}</span>
                <span className={styles.comment}>{text} {`${formatMessage({id: 'explore.cols'})}`}，{textPercent}</span>
              </div>
            </div>
          </>
        ) : (
          <div className={styles.loading} style={{height: '100px',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center'}}>
            <Spin />
          </div>
        )
      }
      <Search
        placeholder={formatMessage({id: 'explore.placeholder'})}
        style={{ width: 300, marginTop: 20, marginBottom: 20}}
        onChange={ handleSearch }
      />
      <Table
        columns={columns}
        dataSource={featuresData}
        pagination={false}
        expandable={{
          expandRowByClick: false,
          expandedRowRender: record => {
            if (record.type === 'continuous') {
              const barChartConfig = {
                a: (<HBChart hData={record.hData} />),
                b: (<div style={{width: 600}}><Pie data={record.extension.value_count} updateWhenChange={false}/></div>),
              }
              return (
                <React.Fragment>
                  <Radio.Group onChange={handleChange} defaultValue={defaultTab} style={{ marginBottom: '20px' }}>
                    <Radio.Button value="a">{formatMessage({id: 'explore.histogram'})}</Radio.Button>
                    <Radio.Button value="b">{formatMessage({id: 'explore.pie'})}</Radio.Button>
                  </Radio.Group>
                  <p><span style={{ fontWeight: 'bold' }}>{`${formatMessage({id: 'explore.max'})}`}: </span>{record.extension.max}</p>
                  <p><span style={{ fontWeight: 'bold' }}>{`${formatMessage({id: 'explore.min'})}`}: </span>{record.extension.min}</p>
                  <p><span style={{ fontWeight: 'bold' }}>{`${formatMessage({id: 'explore.medium'})}`}: </span>{record.extension.median}</p>
                  <p><span style={{ fontWeight: 'bold' }}>{`${formatMessage({id: 'explore.mean'})}`}: </span>{record.extension.mean}</p>
                  <p><span style={{ fontWeight: 'bold' }}>{`${formatMessage({id: 'explore.std'})}`}: </span>{record.extension.stddev}</p>
                  {
                    barChartConfig[defaultTab]
                  }
                </React.Fragment>
              )
            } else if (record.type === 'categorical') {
              return (
                <React.Fragment>
                  <p><span style={{ fontWeight: 'bold' }}>{`${formatMessage({id: 'explore.usual'})}`}: </span>{record.extension.mode.value}({record.extension.mode.percentage}%)</p>
                  <div style={{ width: 600 }}>
                    <Pie data={record.extension.value_count} updateWhenChange={false} />
                  </div>
                </React.Fragment>
              )
            } else if (record.type === 'datetime') {
              const barChartConfig = {
                year: (<BarChart data={record.barYearData} />),
                month: (<BarChart data={record.barMonthData} />),
                week: (<BarChart data={record.barWeekData} />),
                hour: (<BarChart data={record.barHourData} />),
              }
              return (
                <>
                  <Radio.Group onChange={handleTitleChange} defaultValue={defaultValue} style={{ marginBottom: '20px' }}>
                    <Radio.Button value="year">Year</Radio.Button>
                    <Radio.Button value="month">Month</Radio.Button>
                    <Radio.Button value="week">Week</Radio.Button>
                    <Radio.Button value="hour">Hour</Radio.Button>
                  </Radio.Group>
                  {
                    barChartConfig[defaultValue]
                  }
                </>
              )
            }
          },
          // rowExpandable: record => record.name !== 'Not Expandable',
        }}
      />
    </div>
  )
}
export default withRouter(connect(({ dataset }) => (
  { dataset }
))(Explore));
