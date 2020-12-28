import { batchPredict, getPredictJob } from '@/services/dataset';
import { makeStepsDict } from '@/utils/util';
import { PredictStepType, StepStatus } from '@/pages/common/appConst';
import { showNotification } from '@/utils/notice';

const initializeState = {};
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
