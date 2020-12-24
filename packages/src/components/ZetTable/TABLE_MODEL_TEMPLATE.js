import { queryList, deleteTag } from 'services/tag';

export default {
  state: {
    data: [],
    loading: true,
    selectedRowKeys: [],
    selectedRows: [],
    sorter: {
      field: 'name',
      order: 'descend',
    },
    pagination: {
      current: 1,
      pageSize: 10,
      total: 0,
    },
    filters: {
      keyWords: '',
    },
  },

  effects: {
    // get table data
    *queryTable({ payload = {} }, { call, put, select }) {
      yield put({
        type: 'setloading',
      });

      const stateParams = yield select(state => {
        return {
          sorter: state.TABLE_MODEL_NAME.sorter,
          pagination: state.TABLE_MODEL_NAME.pagination,
          filters: state.TABLE_MODEL_NAME.filters,
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
        pageIndex: mixinParams.pagination.current,
        pageNum: mixinParams.pagination.pageSize,
        keyWords: mixinParams.filters.keyWords,
        orderKey: mixinParams.sorter.field,
        orderBy: mixinParams.sorter.order.replace('end', ''),
      };

      const originResponse = yield call(queryList, params);
      const response = originResponse.data;
      yield put({
        type: 'save',
        payload: {
          data: response ? response.rows : [],
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
        type: 'queryTableFirstPage',
      });
    },
    *deleteTag({ payload }, { put, call }) {
      yield call(deleteTag, payload);
      yield put({
        type: 'queryTable',
      });
    },
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
