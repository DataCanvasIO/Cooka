import { getDatasetList, deleteDataset } from '@/services/dataset';
import { message } from 'antd';
import { formatMessage } from 'umi-plugin-locale';

export default {
  state: {
    data: [],
    loading: true,
    selectedRowKeys: [],
    selectedRows: [],
    sorter: {
      field: 'create_datetime',
      order: 'descend',
    },
    pagination: {
      current: 1,
      pageSize: 20,
      total: 0,
    },
    filters: {
      keyWords: '',
    },
  },

  effects: {
    // get table data
    *queryTable({ payload = {} }, { call, put, select }) {
      const data = yield select(state => state.datasetlist.data);
      const pagination = yield select(state => state.datasetlist.pagination);
      yield put({
        type: 'setloading',
      });

      const stateParams = yield select(state => {
        return {
          sorter: state.datasetlist.sorter,
          pagination: state.datasetlist.pagination,
          filters: state.datasetlist.filters,
        };
      });

      const mixinParams = {
        sorter: {
          ...stateParams.sorter,
          ...payload.sorter,
        },
        pagination: {
          ...stateParams.pagination,
          ...payload.pagination,
        },
        filters: {
          ...stateParams.filters,
          ...payload.filters,
        },
      };

      // API PARAMS， DEVELOPER EDIT---------------------------
      const params = {
        page_num: mixinParams.pagination.current,
        page_size: mixinParams.pagination.pageSize,
        query: mixinParams.filters.keyWords,
        order: mixinParams.sorter.order.replace('end', ''),
        order_by: mixinParams.sorter.field,
      };

      const response = yield call(getDatasetList, params);
      const responseData = response.data;

      const dropHistoryData = payload.dropHistoryData === undefined ? false:  payload.dropHistoryData

      yield put({
        type: 'save',
        payload: {
          data: dropHistoryData ? responseData?.datasets:data.concat(responseData?.datasets),
          pagination: {
            current: payload.pagination && payload.pagination.current,
            pageSize: payload.pagination && payload.pagination.pageSize,
            total: responseData ? responseData.count : 0,
          },
        },
      });
    },
    *searchTable({ payload = {} }, { call, put, select }) {
      yield put({
        type: 'setloading',
      });

      const stateParams = yield select(state => {
        return {
          sorter: state.datasetlist.sorter,
          pagination: state.datasetlist.pagination,
          filters: state.datasetlist.filters,
        };
      });

      const mixinParams = {
        sorter: {
          ...stateParams.sorter,
          ...payload.sorter,
        },
        pagination: {
          ...stateParams.pagination,
          ...payload.pagination,
        },
        filters: {
          ...stateParams.filters,
          ...payload.filters,
        },
      };

      // API PARAMS， DEVELOPER EDIT---------------------------
      const params = {
        page_num: mixinParams.pagination.current,
        page_size: mixinParams.pagination.pageSize,
        query: mixinParams.filters.keyWords,
        order: mixinParams.sorter.order.replace('end', ''),
        order_by: mixinParams.sorter.field,
      };

      const originRes = yield call(getDatasetList, params);
      const response = originRes.data;
      yield put({
        type: 'save',
        payload: {
          data: response?.datasets,
          pagination: {
            current: payload.pagination && payload.pagination.current,
            pageSize: payload.pagination && payload.pagination.pageSize,
            total: response ? response.count : 0,
          },
        },
      });
    },

    // get table data first page
    *queryTableFirstPage(_, { put }) {
      yield put({
        type: 'queryTable',
        payload: {
          pagination: {
            current: 1,
          },
        },
      });
    },


    *searchTableFirstPage(_, { put }) {
      yield put({
        type: 'searchTable',
        payload: {
          pagination: {
            current: 1,
          },
        },
      });
    },

    *changeTable({ payload }, { put }) {
      yield put({
        type: 'saveTableChange',
        payload,
      });
      yield put({
        type: 'queryTable',
      });
    },
    *changeFilter({ payload }, { put }) {
      yield put({
        type: 'saveFilter',
        payload: {
          [payload.type]: payload.value,
        },
      });
      yield put({
        type: 'searchTableFirstPage',
      });
    },
    *deleteRows({ payload }, { call, put }) {
      const originRes = yield call(deleteDataset, payload);
      const response = originRes.data;
      if(response) {
        message.success(formatMessage({id: 'datasetlist.delSucceed'}));
        yield put({
          type: 'queryTable',
          payload: {
            pagination: {
              current: 1,
            },
            dropHistoryData: true,
          },
        });
      }
    }
  },

  reducers: {
    setloading(state) {
      return {
        ...state,
        loading: true,
      };
    },
    save(state, { payload }) {
      const Pagination = {
        total: payload.pagination.total,
      };
      payload.pagination && payload.pagination.current
        && (Pagination.current = payload.pagination.current);
      payload.pagination && payload.pagination.pageSize
        && (Pagination.pageSize = payload.pagination.pageSize);

      return {
        ...state,
        data: payload.data,
        pagination: {
          ...state.pagination,
          ...Pagination,
        },
        loading: false,
      };
    },
    saveTableChange(state, { payload }) {
      return {
        ...state,
        sorter: {
          ...state.sorter,
          ...payload.sorter,
        },
        pagination: {
          ...state.pagination,
          ...payload.pagination,
        },
        filters: {
          ...state.filters,
          ...payload.filters,
        },
      };
    },
    changeSelectedRowKeys(state, { payload }) {
      return {
        ...state,
        selectedRowKeys: payload.selectedRowKeys,
        selectedRows: payload.selectedRows,
      };
    },
    saveFilter(state, { payload }) {
      return {
        ...state,
        filters: {
          ...state.filters,
          ...payload,
        },
      };
    },
  },
};
