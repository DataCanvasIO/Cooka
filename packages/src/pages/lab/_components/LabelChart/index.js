import React, { memo } from 'react';
import { Pie, HBChart } from 'components';

const LabelChart = memo((props) => {
  const { labelType, labelData } = props;
  const chartConfig = {
    categorical: (
    <div style={{ width: 500 }}>
      <Pie data={labelData} />
    </div>
    ),
    continuous: (
    <div style={{ width: 500 }}>
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
