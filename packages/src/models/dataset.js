import { createDataset, getDataPreview } from '@/services/dataset';

const initializeState = {

};
export default {
  namespace: 'dataset',
  state: {
    ...initializeState,
    data: [],
    loading: true,
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
    //  创建数据集成功后数据预览
    *queryTable({ payload = {} }, { call, put, select }) {
      const data = yield select(state => state.dataset.data);
      yield put({
        type: 'setloading',
      });

      const stateParams = yield select(state => {
        return {
          sorter: state.dataset.sorter,
          pagination: state.dataset.pagination,
          filters: state.dataset.filters,
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
        uriParams:payload.payload,
        param: {
          page_num: mixinParams.pagination.current,
          page_size: mixinParams.pagination.pageSize,
          query: mixinParams.filters.keyWords,
          order: mixinParams.sorter.order.replace('end', ''),
          order_by: mixinParams.sorter.field,
        }
      };

      const originResponse = yield call(getDataPreview, params);
      const res = originResponse.data;

      yield put({
        type: 'save',
        payload: {
          headers: res?.headers,
          data: data.concat(res?.rows),
          file_path: res?.file_path,
          // columns,
          pagination: {
            current: payload.pagination && payload.pagination.current,
            pageSize: payload.pagination && payload.pagination.pageSize,
            total: res ? res.count : 0,
          },
        },
      });
    },

    // get table data first page
    *queryTableFirstPage( { payload }, { put }) {
      yield put({
        type: 'queryTable',
        payload: {
          pagination: {
            current: 1,
          },
          payload
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
    // 创建数据集
    *createDataset({ payload }, { call, put}) {
      const originRes = yield call(createDataset, payload);
      const res = originRes.data;
      const callback = payload.callback;
      if (res) {
        yield put({
          type: 'save',
        });
        callback && callback();
      }
    },
  },

  reducers: {
    save(state, { payload }) {
      return {
        ...state,
        ...payload
      };
    },
    mergeState(state, { payload }) {
      return {
        ...state,
        ...payload,
      };
    },
    reset(state, { payload }) {
      return {
        ...state
      }
    }
  },
};
