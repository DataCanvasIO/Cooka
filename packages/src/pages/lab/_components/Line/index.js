import React, { PureComponent } from 'react';
import { Empty } from 'antd';
import EchartsCore from '../EchartsCore';
import { toPercent, toFix } from '@/utils/util';
// import IconSpace from '../IconSpace';

const colors = ['#ff002f', '#1976d2', '#13c2c2'];

class Line extends PureComponent {
  getOption = (min, max) => {
    return {
      parallelAxis: [],
      series: [{
        type: 'parallel',
        lineStyle: {
          width: 2
        },
        data: [],
      }],
      visualMap: {
        min: min,
        max: max,
        left: 0,
        precision: 4,
        calculable: true,
        orient: 'vertical',
        bottom: '15%',
        hoverLink:true,
      },
    };
  };

  render() {
    const { style, className, data, xAxisProp, seriesData, loading, ...restProp } = this.props;
    if (!data || !data.hasOwnProperty('data')) {
      return (<Empty />);
    }
    const  rewards = [];
    for (var item of data.data){
      rewards.push(item.reward);
    }
    const options = this.getOption(Math.min(...rewards), Math.max(...rewards));
    data.param_names.forEach((name, index) => {
      options.parallelAxis.push({
        dim: index,
        name
      });
    });
    data.data.forEach((item, index) => {
      options['series']['data'] = new Array(data.param_names.length);
      options['series'][0]['data'][index] = item.params;
    });

    return (
      <EchartsCore
        // loadingOption={{ color: '#1976d2' }}
        option={ {...options} }
        // showLoading={loading}
        // style={style}
        // className={className}
      />
    );
  }
}
export default Line;
