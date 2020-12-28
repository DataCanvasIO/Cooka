import { DownCircleOutlined, UpCircleOutlined } from '@ant-design/icons';
import { notification } from 'antd';
import React from 'react';
import { UUID } from './util';
import styles from './notice.less';


let allview = null;
let view = null;
const inintstyles = {
  color: '#1890ff',
  cursor: 'pointer',
  display: 'inline-block',
  marginLeft: '8px',
};
allview = (key, response) => {
  const msg = (response.stackTrace && response.stackTrace.split('\n')) || (response.detail && response.detail.split('\n'));
  const message = (
    <span>{response.message || 'system error'}
      <span style={inintstyles} onClick={() => { view(key, response); }}>详细信息
        <UpCircleOutlined />
      </span>
    </span>
  );
  notification.error({
    key,
    duration: 0,
    message,
    description: msg.map((item) => {
      return <p className={styles.pstyle}>{item.replace(/^\s+|\s+$/g, '')}</p>;
    }),
    className: styles.notice,
  });
};

view = (key, response) => {
  const message = (response.stackTrace || response.detail)
    ? (
      <span>{response.message || response.result || 'system error'}
        <span style={inintstyles} onClick={() => { allview(key, response); }}>详细信息 <DownCircleOutlined /></span>
      </span>
    )
    : response.message || response.result || 'system error';
  const args = {
    key,
    message,
    duration: 0,
  };
  notification.error(args);
};


export const ZetNotification = (response) => {
  const key = UUID();
  const data = response.data || response;
  const message = data && (data.stackTrace || data.detail)
    ? (
      <span>{data.message || 'system error'}
        <span style={inintstyles} onClick={() => { allview(key, data); }}>详细信息 <DownCircleOutlined /></span>
      </span>
    )
    : (data && (data.message || data.result)) || 'system error';
  const args = {
    key,
    message,
    duration: 10,

  };
  notification.error(args);
};


export const showNotification = (message) => {
  const key = UUID();
  const args = {
    key,
    message,
    duration: 10,
  };
  notification.error(args);
};
