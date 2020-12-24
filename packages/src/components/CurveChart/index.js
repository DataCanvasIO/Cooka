import React, { PureComponent } from 'react';
import { Chart, Tooltip, Axis, View, Geom, Legend } from 'bizcharts';
import { DataView } from '@antv/data-set';

class CurveChart extends PureComponent {
  getLegendTpl = (data, item, legendName = '') => {
    /* return Object.keys(data)
      .map(item => {
        return `<li><span class='ellipsis' style="margin-right:20px;width:40px">${item}</span><span>${
          data[item].roc_auc
        }</span></li>`;
      })
      .join(''); */
    const legendNameArr = Array.isArray(legendName) ? legendName : legendName.split(',');
    let dataValue;
    let legendValue;
    for (const name of legendNameArr) {
      dataValue = item === 'chartData' ? data[name] : data[item][name];
      if (dataValue) {
        legendValue = Number(dataValue).toFixed(4);
        break;
      }
    }
    return legendValue;
  };

  render() {
    const { data, height, extraDv = {} } = this.props;
    let xName = 'False positive rate';
    let yName = 'True positive rate';
    let zName = 'thresholds';
    const legendName = extraDv.legendName || 'roc_auc';
    const dv = new DataView().source(data);
    const dv2 = new DataView().source([{ x: 0, y: 0 }, { x: 1, y: 1 }]);

    const scale = {
      x: {
        min: 0,
        max: 1,
        alias: xName,
        tickInterval: 0.1,
        formatter: value => {
          return `${(value * 100).toFixed(0).toString()}%`;
        },
      },
      y: {
        min: 0,
        max: 1,
        alias: yName,
        tickInterval: 0.1,
        formatter: value => {
          return `${(value * 100).toFixed(0).toString()}%`;
        },
      },
      z: {
        min: 0,
        max: 1,
        alias: zName,
        tickInterval: 0.1,
        formatter: value => {
          return `${(value * 100).toFixed(0).toString()}%`;
        },
      }
    };
    if (this.chart) {
      this.chart.forceFit();
    }
    return (
      <Chart forceFit height={height} data={dv.rows} scale={scale} padding={[40, 250, 60, 60]}>
        <Tooltip showCrosshairs showMarkers>
        {(title,items) => {
          console.log(title,items);
          // items 是个数组，即被触发tooltip的数据。
          // 获取items的颜色
          const color = items[0].color;
          return (
            <div style={{ padding: 4 }}>
              <div>
                <span>FPR: {title}</span>
              </div>
              <div style={{ marginTop: 4 }}>
                <span>TPR: {items[0].value}</span>
              </div>
              <div style={{ marginTop: 4 }}>
                <span>Thresholds: {`${((items[0].data.z) * 100).toFixed(0).toString()}%`}</span>
              </div>
            </div>
          )
        }}
        </Tooltip>
        {/* <Legend
          position="right-bottom"
          marker="circle"
          name="name"
          itemFormatter={item => {
            const legendTpl = this.getLegendTpl(data, item, legendName);
            return legendTpl ? `${item} :   ${legendTpl}` : item;
          }
          }
        /> */}
        <Legend visible={false} />
        <View data={dv.rows}>
          <Axis name="x" title={{ offset: 52 }} />
          <Axis name="y" title={{ offset: 52 }} />
          <Geom type="line" position="x*y" color="name" />
        </View>
        {extraDv.diagonalAuxiliary !== false && (
          <View data={dv2.rows}>
            <Geom type="line" shape="dash" position="x*y" color="#e56285" tooltip={false} />
          </View>
        )}
      </Chart>
    );
  }
}

export default CurveChart;
