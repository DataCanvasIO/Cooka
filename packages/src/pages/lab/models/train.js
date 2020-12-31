import { interTaskType, train } from '@/services/dataset';

const initializeState = {

};
export default {
  namespace: 'train',
  state: {
    ...initializeState,
    defaultTab: 'a',
    defaultPanel: null,
  },

  effects: {
    *inferTasktype({ payload }, { call, put }) {
      const callback = payload.callback;
      const originRes = yield call(interTaskType, payload);
      const res = originRes.data;
      if(res) {
        callback && callback(res)
      }
    },
    *train({ payload }, { call, put }) {
      const originRes = yield call(train, payload);
      const res = originRes.data;
      if (res) {
        yield put({
          type: 'save',
          payload: {
            defaultTab: 'd',
            defaultPanel: 0
          }
        })
      }
    }
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
  },
};
