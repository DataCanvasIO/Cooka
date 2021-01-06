import styles from '@/pages/uploadFile/index.less';
import { QuestionCircleOutlined } from '@ant-design/icons';
import { Card, Col, Input, InputNumber, Radio, Row, Slider, Tooltip } from 'antd/lib/index';
import { Button, Form } from 'antd';
import React, { useEffect, useState } from 'react';
import { formatMessage } from 'umi-plugin-locale';
import router from 'umi/router';
import { SampleStrategy, UploadStepType } from '@/pages/common/appConst';
import { makeStepsDict } from '@/utils/util';
import { checkDatasetName } from '@/services/dataset';
import { showNotification } from '@/utils/notice';
import { withRouter } from 'umi';
import { connect } from 'dva';

function makeRandomRows(form) {

  const randomRows = <Form form={form} initialValues={{ n_rows: 1000, }}>
    <dl>
      <dt>{formatMessage({id: 'upload.nCol'})}</dt>
      <dd className={styles.tips}>{formatMessage({id: 'upload.tips'})}</dd>
    </dl>
    <Form.Item
      name='n_rows'
      rules={[
        {
          required: true,
          message: formatMessage({id: 'upload.necessary'})
        },
        {
          pattern: new RegExp(/^[0-9]{1,}$/, "g"),
          message: formatMessage({id: 'upload.rule'})
        }
      ]}
    >
      <Input style={{ width: 300 }} />
    </Form.Item>
  </Form>

  return randomRows
}

function makeWholeData() {
    return <dl>
      <dd className={styles.tips}>{formatMessage({id: 'upload.hintWholeData'})}</dd>
    </dl>
}


function makeByPercentage(onChange, value) {
  return <>
      <dl>
        <dt>{formatMessage({id: 'upload.nPercent'})}</dt>
      </dl>
      <Row>
        <Col span={12}>
          <Slider
            min={0}
            max={100}
            onChange={onChange}
            value={typeof value === 'number' ? value : 0}
            step={1}
            tooltipVisible={false}
          />
        </Col>
        <Col span={4}>
          <InputNumber
            min={0}
            max={100}
            style={{ margin: '0 16px' }}
            step={1}
            value={value}
            formatter={value => `${value}%`}
            onChange={onChange}
          />
        </Col>
      </Row>
  </>
}


function makeSamplingTab(sampleStrategy, form, onChange, value){

  if(sampleStrategy === SampleStrategy.RandomRows){
    return makeRandomRows(form);
  }else if(sampleStrategy === SampleStrategy.ByPercentage){
    return makeByPercentage(onChange, value)
  } else if(sampleStrategy === SampleStrategy.WholeData){
    return makeWholeData()
  }else{
    console.error("Unseen sample strategy " + sampleStrategy);
  }
}

/**
 * 生成抽样DIV
 */
export function makeSampleDiv(setSampleStrategy, sampleStrategy, form, onChange, value) {

  const handleChange = (e) => {
    setSampleStrategy(e.target.value);
  }

  const analysisTitle = (
    <>
      <Radio.Group onChange={handleChange} defaultValue={sampleStrategy} style={{ marginTop: 12 }}>
        <Radio value={SampleStrategy.WholeData}> {formatMessage({id: 'upload.wholeData'})}</Radio>
        <Radio value={SampleStrategy.RandomRows} style={{ marginLeft: 50 }}>{formatMessage({id: 'upload.col'})}</Radio>
        <Radio value={SampleStrategy.ByPercentage} style={{ marginLeft: 50 }}>{formatMessage({id: 'upload.percent'})}</Radio>
      </Radio.Group>
    </>
  );

  return <div className={styles.analysis}>
    <dl>
      <dt>
        <span>{formatMessage({ id: 'upload.anaysis' })}</span>
        <span>
          <Tooltip placement={'right'} color={'white'} title={formatMessage({id: 'createDataset.sampleTip'})}>
            <QuestionCircleOutlined style={{ marginLeft: 10 }} />
          </Tooltip>
          </span>
      </dt>
    </dl>


    <Card title={analysisTitle} style={{ width: '85%' }}>
      <div>
        {
          makeSamplingTab(sampleStrategy, form, onChange, value)
        }
      </div>
    </Card>
  </div>
}

export function makeCsvFileTip() {

  return <dd>
    <span className={styles.tips}>{formatMessage({id: 'upload.uploadTips'})}</span>
    {/*<a href="">{formatMessage({id: 'upload.details'})}</a>*/}
  </dd>

}

export function checkoutStepFromStepsDict(stepsDict, stepType, handler){
  const destStep = stepsDict[stepType];
  if(destStep !== undefined && destStep !== null){
    handler(destStep)
  }
}

export function checkoutStepFromResponse(jobResponse, stepType, handler){

  if(jobResponse !== null && jobResponse !== undefined) {
    const responseData = jobResponse.data
    const stepsDict = makeStepsDict(responseData.steps);
    checkoutStepFromStepsDict(stepsDict, stepType, handler);
  }

}



// ------------------创建数据集----------------------
export const CreateDatasetFormPage = ({ dispatch,  pollJobResponse }) => {

  const [tipContent, setTipContent] = useState();
  const [tooltipVisible, setTooltipVisible] = useState(false);
  const [disableButton, setDisableButton] = useState(true);
  const [disableInput, setDisableInput] = useState(true);
  const [inputDatasetName, setInputDatasetName] = useState(null);
  const [temporaryDatasetName, setTemporaryDatasetName] = useState(null);


  const showTooltip = (title) => {
    setTooltipVisible(true);
    setTipContent(title);
  }

  const clearTooltip = () => {
    setTipContent(null);
    if(tooltipVisible !== false){
      setTooltipVisible(false);
    }
  }

  // const [tipContent, setTipContent] = useState(null);

  useEffect(() => {
    // enabled input if analyze succeed
    if(pollJobResponse !== null && pollJobResponse !== undefined) {
      const responseData = pollJobResponse.data
      const stepsObject = makeStepsDict(responseData.steps);
      const analyzeStep = stepsObject[UploadStepType.analyze];
      if(analyzeStep !== undefined && analyzeStep !== null){
        if (analyzeStep.status === 'succeed') {
          setDisableInput(false);
          setDisableButton(false);
          setInputDatasetName(analyzeStep.extension.recommend_dataset_name);
          setTemporaryDatasetName(responseData.temporary_dataset_name);
        }
      }
    }
  }, [pollJobResponse])


  const inputOnChange = (inputValueEvent) => {

    const inputValue = inputValueEvent.target.value;
    setInputDatasetName(inputValue);

    if(inputValue === null || inputValue.length < 1) {
      showTooltip(formatMessage({ id: 'extra.inputName' }))
      setDisableButton(true);
      return
    }

    const rule = /^[A-Za-z0-9_-]+$/;
    if(rule.test(inputValue)){
      // check backend
      checkDatasetName(inputValue).then(checkResponse => {
        // 内容改变后只有这一种情况可以提交
        if (checkResponse.code === 0){
          clearTooltip()
          setDisableButton(false);
        }else{
          showTooltip(checkResponse.data.message);
          setDisableButton(true);
        }
      })
    }else{
      showTooltip(formatMessage({id: 'extra.rule'}))
      setDisableButton(true);
    }
  }

  const inputBlur = (inputValueEvent) => {
    inputOnChange(inputValueEvent);
    setTooltipVisible(false);
    console.info("hhhh");
    console.info(tipContent);
  }

  const inputFocus = (inputValueEvent) => {
    inputOnChange(inputValueEvent);
    if(tipContent !== null && tipContent !== undefined && tipContent.length > 0){
      if(tooltipVisible !== true){
        setTooltipVisible(true);
      }
    }
  }


  const handleCreate = () => {
    const datasetName = inputDatasetName

    if (datasetName === null || datasetName.length < 1){
      showNotification("数据集名称为空");
      return;
    }

    if (temporaryDatasetName === null || temporaryDatasetName.length < 1){
      showNotification("未检测到数据集分析成功");
      return;
    }


    dispatch({
      type: 'dataset/createDataset',
      payload: {
        dataset_name: datasetName,
        temporary_dataset_name: temporaryDatasetName,
        callback: () => {
          router.push(`/lab?datasetName=${datasetName}`);
        }
      }
    })
  };

  return (
    <>
      <span> {formatMessage({ id: 'extra.name'})} </span>
      <span>
        <Tooltip
          title={tipContent}
          color={'#FFF2F0'}
          placement="bottomLeft"
          visible={tooltipVisible}
          style={{ width: '50%'} }
        >
          <Input
            style={{ width: '50%'} }
            value={inputDatasetName}
            onFocus={inputFocus.bind(this)}
            onChange={inputOnChange.bind(this)}
            onBlur={inputBlur.bind(this)}
            disabled={disableInput}
            placeholder="Dataset name "
            maxLength={256}
            minLength={0}
          />
        </Tooltip>
          </span>
      <span>
          <Button
            style={{float: 'right' }}
            type="primary"
            disabled={disableButton}
            onClick={handleCreate}>
          {formatMessage({id: 'extra.create'})}
        </Button>
        </span>
    </>
  )
}

