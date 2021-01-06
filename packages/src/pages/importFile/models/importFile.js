import { createTempDataset, getRetrieveData, getTempDataPreview, getTempDateRetrieve, testImportFile } from '@/services/dataset';

const initializeState = {
  flag: false,
};
export default {
  namespace: 'importFile',
  state: {
    ...initializeState,
    // step2Status: 'succeed',
    showTitle: false,
    read2analyze: false,
    step1Status: '',
    copyTook: '',
    datasetName: '',
    testImportFileResponse: {
      valid: false
    }
  },

  effects: {
    *testImportFile({ payload }, { call, put}) {
      const originRes = yield call(testImportFile, payload);
      if (originRes) {
        yield put({
          type: 'save',
          payload: {
            testImportFileResponse: {
              valid: originRes.code === 0,
              reason: originRes.data.message
            }
          }
        })
      }
    },
    // 创建临时数据集
    *createTempDataset({ payload }, { call, put}) {
      const originRes = yield call(createTempDataset, payload);
      const res = originRes.data;
      if (res) {
        const params = {
          temporary_dataset_name: res.temporary_dataset_name,
          analyze_job_name: res.analyze_job_name,
        };
        yield put({
          type: 'save',
          payload: {
            params
          }
        })
        yield put({
          type: 'getRetrieveData',
          payload: params
        });
      }
    },
    //  文件上传成功后数据预览
    *getTempDataPreview({ payload }, { call, put }) {
      const originRes = yield call(getTempDataPreview, payload);
      const res = originRes.data;
      const columns = [];
      const dataSource = [];
      res.headers.forEach((header) => {
        columns.push({
          title: header,
          dataIndex: header
        })
      })
      res.rows.forEach((row, idx) => {
        dataSource[idx] = dataSource[idx] || {} ;
        row.forEach((item, index) => {
          dataSource[idx][res.headers[index]] = item
        })
      });
      columns[0].fixed = 'left';
      columns[0].width = 150;
      columns[columns.length - 1].fixed = 'right';
      columns[columns.length - 1].width = 150;
      yield put({
        type: 'save',
        payload: {
          columns,
          dataSource
        }
      })
    },
    //  文件上传成功后数据探查
    *getTempDateRetrieve({ payload }, { call, put }) {
      const originRes = yield call(getTempDateRetrieve, payload);
      const res = originRes.data;
      if(res) {
        const number = res.feature_summary.continuous;
        const type = res.feature_summary.categorical;
        const date = res.feature_summary.datetime;
        const text = res.feature_summary.text;
        const data = res.features;
        const n_rows = res.n_rows;
        const file_path = res.file_path;

        if (data.length) {
          data.forEach((item, index) => {
            item.key = index;
            if (item.type === 'continuous') {
              item.hData = [];
              item.extension.bins.map((bin) => {
                item.hData.push({
                  value: [bin.begin, bin.end],
                  count: bin.value
                })
              })
            } else if (item.type === 'datetime') {
              const hour = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24'];
              item.barHourData = [];
              const month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
              item.barMonthData = [];
              const week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
              item.barWeekData = [];
              item.barYearData = [];
              item.extension.by_hour.map((hourData, index) => {
                item.barHourData.push({
                  time: hour[index],
                  value: hourData
                })
              });
              item.extension.by_month.map((monthData, index) => {
                item.barMonthData.push({
                  time: month[index],
                  value: monthData
                })
              });
              item.extension.by_week.map((weekData, index) => {
                item.barWeekData.push({
                  time: week[index],
                  value: weekData
                })
              });
              item.extension.by_year.map((yearData, index) => {
                item.barYearData.push({
                  time: String(yearData['year']),
                  value: yearData['value']
                })
              })
            }
          })
        }
        const datasetName = res.name;
        yield put({
          type: 'save',
          payload: {
            number,
            type,
            date,
            text,
            data,
            n_rows,
            datasetName,
            file_path
          }
        })
      }
    },
    //  加载和分析数据
    *getRetrieveData({ payload }, { call, put, select }) {
      const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
      while (true) {
        const pollJobResponse = yield call(getRetrieveData, payload);
        const pollJobResponseData = pollJobResponse.data;
        yield call(delay, 1000);

        yield put({
          type: 'save',
          payload: {
            pollJobResponse: pollJobResponse,
          }
        })

        if(pollJobResponseData.steps.length === 3 && pollJobResponseData.steps[2]['status'] === 'succeed') {
          const params = yield select(state => state.importFile.params);
          yield put({
            type: 'getTempDataPreview',
            payload: {
              uriParams:params,
              params: {
                page_num: 1,
                page_size: 10
              }
            }
          });

          yield put({
            type: 'getTempDateRetrieve',
            payload: params
          });
          return
        }
      }
    },
    //
    *updateData({ payload }, { call, put, select }) {
      const val = payload.val;
      let newData = null;
      const data = JSON.parse(JSON.stringify(yield select(state => state.importFile.data)));
      const params = yield select(state => state.importFile.params);
      if (val.length === 0) {
        yield put({
          type: 'getTempDateRetrieve',
          payload: params
        });
      }
      newData = data.filter(item => item.name.indexOf(val) > -1);
      yield put({
        type: 'save',
        payload: {
          data: newData
        }
      })
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
