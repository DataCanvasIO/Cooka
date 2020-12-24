import React from "react";
import {
  Chart,
  Geom,
  Axis,
  Tooltip,
  Coordinate,
  Interval
} from "bizcharts";
import DataSet from "@antv/data-set";
import { toPercent } from '@/utils/util';

export default class Hhistogram extends React.Component {
  render() {
    const { data } = this.props;
    const ds = new DataSet();
    const dv = ds.createView().source(data);
    // rename && dv.transform({
    //   type:'rename',
    //   map:rename
    // })
    if(data.length === 0){
      return <div></div>
    }
    return (
      <div>
        <Chart height={200} data={dv} scale={{x:{min:0,max:1}}} forceFit >
        <Coordinate transpose />
        <Tooltip visible={false} />
        <Interval
          position="y*x"
          label={[
            "x",
            (xValue) => {
            return {
                content: toPercent(xValue, 0),
              };
            }
          ]}
        />
        <Axis
          name="x"
          label={{
            formatter:(text)=>{
              return `${(Number(text)*100).toFixed(0)}%`
            }
          }}
        />
        <Axis
          name="y"
          label={{
            offset: 12,
            formatter:(text)=>{
              return text
            }
          }}
        />
        <Geom
          type="interval"
          position="y*x"
          color={
            ['y',(y)=>{
              return {
                AUC:'#786de7',
                precision:'#1890ff',
                Recall:'#13c2c2',
                F1:'#ffc53d',
                Accuracy:'#ff7a45'
              }[y]
            }]
          }
          >
          </Geom>
        </Chart>
      </div>
    );
  }
}
