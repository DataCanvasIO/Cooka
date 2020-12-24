import React from 'react';
import {
  Chart,
  Axis,
  Tooltip,
  Interval,
} from "bizcharts";

class HBChart extends React.Component {

  render() {
    const { hData } = this.props;
    return (
      <React.Fragment>
        <Chart
          height={300}
          width={600}
          data={hData}
          autoFit
        >
          <Axis name="value" />
          <Axis name="count" />
          <Tooltip
            inPlot
            crosshairs={false}
            position='right'
          />
          <Interval position="value*count" />
        </Chart>
      </React.Fragment>
    );
  }
}

export default HBChart;
