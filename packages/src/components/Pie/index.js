import React from 'react';
import { PieChart } from 'bizcharts';

class Pie extends React.Component {

  render() {
    const { data } = this.props;
    return (
      <React.Fragment>
        <PieChart
          data={data}
          // title={{
          //   visible: true,
          //   text: '饼图-外部图形标签(outer label)',
          // }}
          // description={{
          //   visible: true,
          //   text: '当把饼图label的类型设置为outer时，标签在切片外部拉线显示。设置offset控制标签的偏移值。',
          // }}
          radius={0.8}
          angleField='value'
          colorField='type'
          label={{
            visible: true,
            type: 'outer',
            offset: 20,
          }}
          key={Math.random(1,1000)}
        />
      </React.Fragment>
    )
  }
}

export default Pie;
