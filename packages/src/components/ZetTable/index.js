import React, { PureComponent, Fragment } from 'react';
import { connect } from 'dva';
import withRouter from 'umi/withRouter';
import PropTypes from 'prop-types';
import { Table,  } from 'antd/lib/table';
import { Alert,  } from 'antd/lib/alert';
import {  Button } from 'antd/lib/button';

import styles from './index.less';

const paginationConfig = {
  showTotal: (total) => {
    return `共 ${total} 个`;
  },
  showQuickJumper: true,
  showSizeChanger: true,
  size: 'small',
};

@withRouter
@connect()
class ZetTable extends PureComponent {
  static defaultProps = {
    rowKey: record => record.id,
    columns: [],
    buttonlist: [],
  }

  componentDidMount() {
    // const storePageSize = localStorage.getItem('table-page-size');
    const { dispatch, tableModelName, tabledata: {
      pagination,
      filters,
      sorter,
    } } = this.props;
    if (pagination) {
      dispatch({
        type: `${tableModelName}/saveTableChange`,
        payload: {
          pagination,
          filters,
          sorter,
        },
      });
    }
  }

  changeSelectedRow = (selectedRowKeys, selectedRows) => {
    const { dispatch, tableModelName } = this.props;
    dispatch({
      type: `${tableModelName}/changeSelectedRowKeys`,
      payload: {
        selectedRowKeys,
        selectedRows,
      },
    });
  }

  // getPageSize = (currPageSize) => {
  //   let tablePageSize = storage.get('table-page-size');
  //   if (!tablePageSize || (parseInt(tablePageSize, 10) !== currPageSize)) {
  //     storage.add('table-page-size', currPageSize);
  //     tablePageSize = currPageSize;
  //   }
  //   return tablePageSize;
  // }

  handleTableChange = (pagination, filters, sorter) => {
    // const pageSize = this.getPageSize(pagination.pageSize);
    const { dispatch, tableModelName,
      tabledata: {
        sorter: {
          field,
          order,
        },
      },
    } = this.props;
    if (sorter && Object.keys(sorter).length === 0
    && field && field.length > 0 && order && order.length > 0) {
      dispatch({
        type: `${tableModelName}/changeTable`,
        payload: {
          pagination,
          sorter: {
            field,
            order: 'descend',
          },
          filters,
        },
      });
    } else {
      dispatch({
        type: `${tableModelName}/changeTable`,
        payload: {
          pagination,
          sorter,
          filters,
        },
      });
    }
  }

  render() {
    const {
      columns,
      rowkey,
      tabledata: {
        data,
        loading,
        pagination,
        selectedRowKeys,
        selectedRows,
      },
      buttonlist,
      tableModelName,
      selectbar,
      selectRowOptions = {},
      ...otherProps
    } = this.props;
    const Pagination = this.props.pagination
      || { ...paginationConfig, ...pagination };
    const newColumns = [];
    for (const column of columns) {
      if (column.sorter) {
        if (typeof column.sorter === 'boolean' && column.sorter === true) {
          newColumns.push({
            ...column,
            // sortOrder: column.sorter.field === column.dataIndex ? column.sorter : false,
          });
        }
        if (typeof column.sorter === 'function') {
          newColumns.push({
            ...column,
            // sortOrder: column.sorter.field === column.dataIndex ? column.sorter : false,
          });
        }
      } else {
        newColumns.push(column);
      }
    }
    // let x = 0;
    // for (let i = 0; i < newColumns.length; i++) {
    //   if (typeof newColumns[i].width === 'number') {
    //     x += newColumns[i].width;
    //   } else {
    //     x += 180;
    //   }
    // }
    // const scroll = { x };
    const buttonBar = buttonlist.map(b => {
      return (
        <Button
          key={b.name}
          type={b.type}
          disabled={b.disabled}
          onClick={() => { b.callback(selectedRowKeys, selectedRows); }}
          {...b.props}
        >
          {b.name}
        </Button>
      );
    });
    return (
      <div>
        {selectedRowKeys && selectedRowKeys.length > 0 && [
          <div className={styles.buttonBar} key='buttonBar'>{buttonBar}</div>,
          <div key='tableAlert'>
            { (selectbar === undefined || selectbar) && (
              <Alert
                className={styles.tableAlert}
                message={(
                  <Fragment>
                    已选择 <span style={{ fontWeight: 600 }}>{selectedRowKeys.length}</span> 项
                    <span
                      onClick={() => { this.changeSelectedRow([], []); }}
                      style={{ float: 'right', color: '#388DED' }}
                    >
                      清空
                    </span>
                  </Fragment>
                )}
                type="info"
                showIcon
              />
            )
            }
          </div>,
        ]}
        <Table
          columns={newColumns}
          rowKey={rowkey}
          size='middle'
          dataSource={this.props.dataSource || data}
          pagination={Pagination}
          loading={this.props.loading || loading}
          onChange={this.props.onChange || this.handleTableChange}
          rowSelection={this.props.rowSelection || {
            selectedRowKeys,
            onChange: this.changeSelectedRow,
            ...selectRowOptions,
          }}
          // scroll={(newColumns && newColumns.length >= 6) ? scroll : {}}
          {...otherProps}
        />
      </div>
    );
  }
}

ZetTable.propTypes = {
  rowKey: PropTypes.func,
  columns: PropTypes.arrayOf(PropTypes.object),
  buttonlist: PropTypes.arrayOf(PropTypes.object),
};

export default ZetTable;
