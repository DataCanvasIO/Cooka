import styles from '@/pages/uploadFile/index.less';
import { QuestionCircleOutlined } from '@ant-design/icons';
import { Card, Col,  Icon, Input, InputNumber, Radio, Row, Slider, Tooltip } from 'antd/lib/index';
import { Form } from 'antd';
import React from 'react';
import { formatMessage } from 'umi-plugin-locale';
import router from 'umi/router';
import { Button } from 'antd';


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
  const byPercentage =
    <>
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

  return byPercentage

}


function makeSamplingTab(sampleStrategy, form, onChange, value){
  if(sampleStrategy === 'random_rows'){
    return makeRandomRows(form);
  }else if(sampleStrategy === 'by_percentage'){
    return makeByPercentage(onChange, value)
  }else {
    return makeWholeData()
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
        <Radio value='whole_data'> {formatMessage({id: 'upload.wholeData'})}</Radio>
        <Radio value='random_rows' style={{ marginLeft: 50 }}>{formatMessage({id: 'upload.col'})}</Radio>
        <Radio value='percentage' style={{ marginLeft: 50 }}>{formatMessage({id: 'upload.percent'})}</Radio>
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


// ------------------创建数据集----------------------

/**
 * 带有tip提示的输入框
 */
class DatasetNameInput extends React.Component {
  /**
   *
   * @param props
   * @param props.value 给组件设置值用的，可以是对象
   * @param props.onChange Form.Item 的onChange逻辑，用来进行验证的，自定义组件要调用
   * @param props.analyzeSucceed 是否分析成功，用来设置按钮状态
   */
  constructor(props){
    super(props);
    this.state = {
      tipContent: null,  // tip提示
    }
  }


  /**
   * 处理输入框变更事件
   * @param inputValue
   */
  inputOnChange(inputValueEvent){
    const inputValue = inputValueEvent.target.value;
    // 1. 调用Form.Item的onChange方法
    this.props.onChange(inputValue);
    // this.props.value = inputValue; // 更新输入框

    // 2. 检查输入的数据是否合法, 如果合法变更按钮状态，如果不合法，使用Tip 提示原因
    if(inputValue === null || inputValue.length < 1){
      // 2.1. 输入的数据为空，提示必选，并置灰 创建按钮
      this.setState({
        tipContent: formatMessage({ id: 'extra.inputName'}),
      });
      this.props.form.setFieldsValue({
        btn: true
      })
    }else{
      const rule = /^[A-Za-z0-9_-]+$/;
      if(rule.test(inputValue)){
        // 2.2. 验证通过，创建按钮的状态由分析结果决定
        this.setState({
          tipContent: null,  // 验证通过清除 tip提示
        });
        this.props.form.setFieldsValue({
          btn: false
        })
      }else{
        // 2.3. 校验不通过，创建按钮不可选
        this.setState({
          tipContent: formatMessage({id: 'extra.rule'})
        });
        this.props.form.setFieldsValue({
          btn: true
        })
      }
    }
  }


  render() {
    return (
      <>
        <Tooltip
          trigger={['focus']}
          title={this.state.tipContent}
          color={'#FFF2F0'}
          placement="bottomLeft"
          style={{ width: '50%'} }
        >
          <Input
            style={{ width: '100%'} }
            value={this.props.value}
            onChange={this.inputOnChange.bind(this)}
            placeholder="Dataset name "
            maxLength={256}
            minLength={0}
          />
        </Tooltip>

      </>
    );
  }
}

class EditButton extends React.Component{



  render() {
    return <Button
      style={{float: 'right', marginTop: 20 }}
      type="primary"
      disabled={this.props.value}
      onClick={this.props.onClick}>
      {formatMessage({id: 'extra.create'})}
    </Button>


  }
}

export class CreateDatasetForm extends React.Component{

  /***
   * @param props.form: 表单对象，用于在组件外操作表单
   * @param props.temporaryDatasetName: 数据集名称，分析成功后填充表单
   * @param props.analyzeSucceed: 是否分析数据成功，只有成功时才能创建数据集
   */
  constructor(props){
    // form, temporaryDatasetName, analyzeSucceed
    super(props);
    this.state = {
      ready2create: false,
    }
  }


  /**
   * 创建数据集按钮事件
   */
  handleCreate(){
    if (this.props.temporaryDatasetName === null || this.props.temporaryDatasetName.length < 1){
      console.error("Property temporaryDatasetName is empty, please check is analyze succeed.");
      return;
    }
    this.props.dispatch({
      type: 'dataset/createDataset',
      payload: {
        dataset_name: this.props.form.getFieldValue()['datasetName'],
        temporary_dataset_name: this.props.temporaryDatasetName,
        callback: () => {
          router.push(`/lab?datasetName=${this.props.form.getFieldValue()['datasetName']}`);
        }
      }
    })
  };

  render() {

    return <Form form={this.props.form} initialValues={ {datasetName: this.props.datasetName, btn: true} } >
      <Form.Item
        style={{ float: 'left', marginRight: 10, marginTop: 20, width: 300 }}
        label={formatMessage({ id: 'extra.name'})}
        name='datasetName'>
        <DatasetNameInput form={this.props.form} onClick={this.handleCreate.bind(this)} />
      </Form.Item>

      <Form.Item name='btn'>
        <EditButton onClick={this.handleCreate.bind(this)}/>
      </Form.Item>
    </Form>

  }

}

