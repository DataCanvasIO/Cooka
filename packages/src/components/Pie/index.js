import React from 'react';
import { PieChart } from 'bizcharts';

class Pie extends React.Component {
  shouldComponentUpdate(props, nextProps) {
    console.log(props, nextProps)
    // if (props.data !== nextProps.data) {
    //   return true;
    // }
  }
  render() {
    const { data } = this.props;
    return (
      <React.Fragment>
        <PieChart
          data={data}
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
