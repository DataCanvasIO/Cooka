import React, { memo } from 'react';
import { Pie, HBChart } from 'components';

const LabelChart = memo((props) => {
  const { labelType, labelData } = props;
  var style = props.style;

  if(style === null || style === undefined){
    style = {
      width: 500
    }
  }

  const chartConfig = {
    categorical: (
    <div style={style}>
      <Pie data={labelData} updateWhenChange={false}/>
    </div>
    ),
    continuous: (
    <div style={style}>
      <HBChart hData={labelData} />
    </div>
    )
  }
  return (
    <>
      {chartConfig[labelType]}
    </>
  )
})

export default LabelChart;
