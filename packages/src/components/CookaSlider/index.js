import React, { useEffect, useRef, useState, useImperativeHandle } from 'react';
import Draggable from 'react-draggable';
import styles from './index.less';
import { formatMessage } from 'umi-plugin-locale';

let baseWidth = 0;

const CookaSlider = ({ dataRef, sliderData }) => {
  const containerRef = useRef({});
  const [isShow, setIsShow] = useState(false);
  const [data, setData] = useState(sliderData || []);
  // const [bounds, setBounds] = useState({})
  useEffect(() => {
    setIsShow(true);
  }, []);

  useImperativeHandle(dataRef, () => ({
    getData: () => {
      return data;
    },
  }));

  const blockWidth = (percent, width) => {
    if (!width) {
      return 0;
    }
    return width * percent / 100;
  }

  const handleDrag = (e, ui, index) => {
    const currData = [...data];
    const { deltaX, deltaY } = ui;
    // console.log('ui=>', deltaX, ui, index)
    const count = Math.round(Math.abs(deltaX) / 8);
    if (deltaX < 0) {
      currData[index].count = data[index].count - count;
      currData[index+1].count = data[index+1].count + count;
    }
    if (deltaX > 0) {
      currData[index].count = data[index].count + count;
      currData[index+1].count = data[index+1].count - count;
    }
    //
    if (index === 0) {
      if (currData[index].count < 1) {
        currData[index].count = 1;
        currData[index+1].count = 99 - currData[index+2].count;
        console.log(currData[index].count)

        return false;
      }
      if (currData[index+1].count < 1) {
        currData[index+1].count = 1;
        currData[index].count = 99 - currData[index+2].count;
        return false;
      }
      // setBounds({
      //   left: 4,
      //   right: 707+1
      // })
    }
    if (index === 1) {
      if (currData[index].count < 1) {
        currData[index].count = 1;
        currData[index+1].count = 99 - currData[index-1].count;
        return false;
      }
      if (currData[index+1].count < 1) {
        currData[index+1].count = 1;
        currData[index].count = 99 - currData[index-1].count;
        return false;
      }
    }
    setTimeout(() => {
      setData(currData);
    }, 100)
    // console.log('currData =>>>', currData)
  };

  const handleStart = (e, ui, index) => {
    // console.log(e, ui, index)
  }

  const width = containerRef.current.clientWidth || 0;
  const gridWidth = width / 100;
  return (
    <>
      <div ref={containerRef} className={styles.container}>
        {
          isShow && data && data.map((item, index) => {
            if (index === 0) {
              baseWidth = 0;
            }
            const dragClass = `cooka-drag-bar-${index}`;
            const elementWidth = blockWidth(item.count, width);
            const dragBarWidth = baseWidth + elementWidth - 4;
            baseWidth += elementWidth;
            const displayContent = `${item.name} ${item.count}%`;

            return (
              <React.Fragment key={index}>
                <div className={styles.block} style={{background: item.color, width: elementWidth}}>
                  {
                    elementWidth > 100 ? displayContent : ''
                  }
                </div>
                  {
                    index !== data.length - 1 &&
                      <Draggable
                        axis="x"
                        position={{x: dragBarWidth, y: 0}}
                        grid={[gridWidth, gridWidth]}
                        // bounds={bounds}
                        scale={1}
                        onDrag={(e, ui) => handleDrag(e, ui, index)}
                        onStart={(e, ui) => handleStart(e, ui)}
                      >
                        <div className={`${styles.dragBar} ${dragClass}`}></div>
                      </Draggable>
                  }
              </React.Fragment>
            )
          })
        }
      </div>
      <div className={styles.legend}>
        <div className={styles.train}>
          <span className={styles.trainCir}></span>
          <span className={styles.symbol}>{formatMessage({id: 'extra.trainUnion'})}</span>
          {/* <span>{`${data[0].count}%`}</span> */}
        </div>
        <div className={styles.verification}>
          <span className={styles.verificationCir}></span>
          <span className={styles.symbol}>{formatMessage({id: 'extra.verifyUnion'})}</span>
          {/* <span>{`${data[1].count}%`}</span> */}
        </div>
        <div className={styles.test}>
          <span className={styles.testCir}></span>
          <span className={styles.symbol}>{formatMessage({id: 'extra.testUnion'})}</span>
          {/* <span>{`${data[2].count}%`}</span> */}
        </div>
      </div>
    </>
  );
}


export default CookaSlider;
