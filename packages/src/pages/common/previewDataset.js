import React, { useState, useEffect } from 'react';
import { List, Table } from 'antd/lib/index';
import { useSelector, useDispatch, connect } from 'dva';
import { withRouter } from 'umi';
import { formatMessage } from 'umi-plugin-locale';
import styles from '@/pages/lab/_components/index.less';
import { useWindowSize } from '@/utils/util';
import InfiniteScroll from 'react-infinite-scroller';


const Preview = ({dataset: { data = [], headers, file_path, pagination }, dispatch, datasetName}) => {
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  useEffect(() => {
    dispatch({
      type: 'dataset/queryTableFirstPage',
      payload: {
        datasetName,
      }
    })
  }, []);


  const viewOriginFile = () => {
    window.open(`/api/resource/${file_path}?opt=head&n=100`)
  }

  const renderTableContent = (item=[]) => {
    return (
      <List.Item style={{display: 'flex',justifyContent: 'space-between' }}>
        {
          item && item.map((i)=>{
            return <div style={{ flex:1, maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis' }}>{i}</div>
          })
        }
      </List.Item>
    )
  }

  const handleInfiniteOnLoad = () => {
    // setLoading(true);
    // if (data.length === pagination.total) {
    //   // message.warning('Infinite List loaded all');
    //   setHasMore(false);
    //   setLoading(false);
    //   return;
    // }
    dispatch({
      type: 'dataset/queryTable',
      payload: {
        pagination: {
          current: pagination.current + 1,
          pageSize: 10
        },
        payload: {datasetName}
      }
    })
  }

  const width = headers ? (headers.length * 150) : 0;
  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <span style={{ color: '#c4c4c4' }}>{formatMessage({ id: 'preview.viewOriginFile'})}</span>
        <span style={{ color: '#1890ff', cursor: 'pointer', marginLeft: 10 }} onClick={viewOriginFile}>{formatMessage({ id: 'preview.view'})}</span>
      </div>
      <div style={{ width: '100%', overflow: 'auto'}}>
        <div style={{display: 'flex',justifyContent: 'space-between', height: '46px', lineHeight: '46px', backgroundColor: 'rgb(249, 249, 249)', color: 'rgba(0,0,0,0.85)', fontWeight: 500, width }}>
          {
            headers?.map((item)=>{
              return <div style={{ flex:1, maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis' }}>{item}</div>
            })
          }
        </div>
        <div className={styles.infiniteContainer} style={{ height: useWindowSize().innerHeight - 400, width }}>
          <InfiniteScroll
            initialLoad={false}
            pageStart={0}
            loadMore={handleInfiniteOnLoad}
            hasMore={!loading && hasMore}
            useWindow={false}
          >
            <List
              dataSource={data}
              renderItem={renderTableContent}
            />
          </InfiniteScroll>
      </div>
      </div>
    </div>
  )
}
export default withRouter(connect(({ dataset }) => (
  { dataset }
))(Preview));
