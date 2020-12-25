import { getTrainingList, getModelDetail, predictModel, getBatchPredictJobname } from '@/services/dataset';
import { ConvertByteUnits } from '@/utils/util';

const initializeState = {

};
export default {
  namespace: 'center',
  state: {
    ...initializeState,
    trainings: [],
    current: -1,
    loading: false,
    nodata: false
  },

  effects: {
    *getBatchPredictJobname({ payload }, { call, put }) {
      const callback = payload.callback;
      const originRes = yield call(getBatchPredictJobname, payload);
      const res = originRes.data;
      if (res) {
        callback && callback(res.batch_predict_job_name);
      }
    },
    *predictModel({ payload }, { call, put }) {
      const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
      while (true) {
        const originRes = yield call(predictModel, payload);
        const res = originRes.data;
        yield call(delay, 1000);
        const { steps = [] } = res;
        // 加载成功
        if (steps.length === 2 || steps.length === 3 || steps.length === 4 || steps.length === 5 && steps[1].status === 'succeed') {
          const { extension: { n_cols = '', n_rows = '' }, took = '', status = '' } = steps[1];
          yield put({
            type: 'save',
            payload: {
              loadingStatus: status,
              current: 1,
              n_cols,
              n_rows,
              loadTook: took.toFixed(2)
            }
          })
        } else if (steps.length === 2 && steps[1].status === 'failed') {  // failed
          const { message = '', status = '' } = steps[1];
          yield put({
            type: 'save',
            payload: {
              loadingStatus: status,
              current: 1,
              loadErrorMsg: message
            }
          });
          return
        }
        // 读取模型成功
        if (steps.length === 3 || steps.length === 4 || steps.length === 5 && steps[2].status === 'succeed') {
          const { extension: { model_size = '' }, took = '', status = '' } = steps[2];
          yield put({
            type: 'save',
            payload: {
              readingStatus: status,
              current: 2,
              readTook: took.toFixed(2),
              loadModelSize: ConvertByteUnits(model_size)
            }
          })
        } else if (steps.length === 3 && steps[2].status === 'failed') {  // failed
          const { message = '', status = '' } = steps[2];
          yield put({
            type: 'save',
            payload: {
              readingStatus: status,
              current: 2,
              readErrorMsg: message
            }
          });
          return
        }
        // 预测数据成功
        if (steps.length === 4 || steps.length === 5 && steps[3].status === 'succeed') {
          const { took = '', status = '' } = steps[3];
          yield put({
            type: 'save',
            payload: {
              predictStatus: status,
              current: 3,
              predictTook: took.toFixed(2),
            }
          })
        } else if (steps.length === 4 && steps[3].status === 'failed') {  // failed
          const { message = '', status = '' } = steps[3];
          yield put({
            type: 'save',
            payload: {
              predictStatus: status,
              current: 3,
              predictErrorMsg: message
            }
          });
          return
        }
        // 写出结果成功
        if (steps.length === 5 && steps[4].status === 'succeed') {
          const { extension: { output_path = '' }, took = '', status = '' } = steps[4];
          yield put({
            type: 'save',
            payload: {
              resultStatus: status,
              current: 5,
              resultTook: took.toFixed(2),
              outputPath: output_path
            }
          })
          return;
        } else if (steps.length === 5 && steps[4].status === 'failed') {  // failed
          const { message = '', status = '' } = steps[4];
          yield put({
            type: 'save',
            payload: {
              resultStatus: status,
              current: 5,
              resultErrorMsg: message
            }
          });
          return
        }
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
    reset(state, { payload }) {
      return {
        ...state
      }
    }
  },
};
