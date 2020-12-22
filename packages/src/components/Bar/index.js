import React from "react";
import {
  Chart,
  Geom,
  Axis,
  Tooltip,
  Coordinate,
  Label,
  Legend,
  Interval,
} from "bizcharts";
import DataSet from "@antv/data-set";

class BarChart extends React.Component {
  render() {
    const { data } = this.props;
    const ds = new DataSet();
    const dv = ds.createView().source(data);
    dv.source(data).transform({
      type: "sort",
      callback(a, b) {
        // 排序依据，和原生js的排序callback一致
        return a.value - b.value > 0;
      }
    });
    return (
      <Chart height={400} data={dv.rows} autoFit>
        <Coordinate transpose />
        <Interval position="time*value" />
      </Chart>
    );
  }
}
export default BarChart;
