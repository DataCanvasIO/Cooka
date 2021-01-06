import fetch from 'dva/fetch';
// import { router } from 'umi';
import { notification } from 'antd';
import { join as pathJoin } from 'path';
import { stringify as qsStringify } from 'qs';
// import router from 'umi/router';
import { ZetNotification } from './notice';
import { showNotification } from './notice';
import { ServiceException } from '@/exception';
// import './promise';
const apiPrefix = '';

const codeMessage = {
  200: '服务器成功返回请求的数据。',
  201: '新建或修改数据成功。',
  202: '一个请求已经进入后台排队（异步任务）。',
  204: '删除数据成功。',
  400: '发出的请求有错误，服务器没有进行新建或修改数据的操作。',
  401: '用户没有权限（令牌、用户名、密码错误）。',
  403: '用户得到授权，但是访问是被禁止的。',
  404: '发出的请求针对的是不存在的记录，服务器没有进行操作。',
  406: '请求的格式不可得。',
  410: '请求的资源被永久删除，且不会再得到的。',
  422: '当创建一个对象时，发生一个验证错误。',
  500: '服务器发生错误，请检查服务器。',
  502: '网关错误。',
  503: '服务不可用，服务器暂时过载或维护。',
  504: '网关超时。',
};
function checkStatus(response) {
  // console.log(response.headers.get('Date'));
  if (response && response.status >= 200 && response.status < 300) {
    return response;
  }
  const errortext = codeMessage[response.status] || response.statusText;
  notification.error({
    message: `请求错误 ${response.status}: ${response.url}`,
    description: errortext,
  });
  const error = new Error(errortext);
  error.name = response.status;
  error.response = response;
  throw error;
}

// function changeLoadingStatus(response, loadingId) {
//   if (loadingId) {
//     window.g_app._store.dispatch({
//       type: 'loadingstatus/remove',
//       payload: {
//         loadingId,
//       },
//     });
//   }
//   return response;
// }

/**
 * Requests a URL, returning a promise.
 *
 * @param  {string} url       The URL we want to request
 * @param  {object} [options] The options we want to pass to "fetch"
 * @param  checkResponseCode 是否检查返回状态码，如果要求，则会检查相应的状态码，如果不对右侧通知，如果设置为false则不检查状态
 * @return {object}           An object containing either "data" or "err"
 */
export function request(url, options, checkResponseCode) {
  const defaultOptions = {
    credentials: 'include',
  };
  // const loadingId = options && options.body && options.body.loadingId;
  const newOptions = { ...defaultOptions, ...options };
  if (newOptions.method === 'POST' || newOptions.method === 'PUT' || newOptions.method === 'DELETE') {
    if (!(newOptions.body instanceof FormData)) {
      // if (typeof newOptions.body === 'object' && !Array.isArray(newOptions.body)) {
      //   const { ...body } = newOptions.body;
      //   delete body.loadingId;
      //   newOptions.body = body;
      // }
      newOptions.headers = {
        Accept: 'application/json, text/plain, */*',
        'Content-Type': 'application/json; charset=utf-8',
        ...newOptions.headers,
      };
      newOptions.body = JSON.stringify(newOptions.body);
    } else {
      // newOptions.body is FormData
      newOptions.headers = {
        Accept: 'application/json',
        ...newOptions.headers,
      };
    }
  }

  //
  newOptions.headers = {
    ...newOptions.headers,
    sessionId: localStorage.getItem('sessionId'),
    language: localStorage.getItem('intlLang'),
  };
  return fetch(url, newOptions).then(checkStatus).then(r => {
    try {
      return r.json();
    }catch (e){
      // 如果请求不是一个json 将会报错
      return {
        code: -2,
        data: {}
      }
    }
  } ).then((jsonResponse) => {
      if(checkResponseCode === true) {
        if(jsonResponse.code !== 0){
          showNotification(JSON.stringify(jsonResponse));
        }
      }
      return jsonResponse;
    })
}

/**
 *  the proxy of request
 * @param url
 * @param options
 * @returns {*}
 */
function proxyRequest(url, options, checkResponseCode) {
  options = options || {};
  const prefix = options.prefix || apiPrefix;
  url = url.startsWith(prefix) ? url : pathJoin(prefix, url);
  return request(url, options, checkResponseCode);
}

/**
 * @param url
 * @param data   such as : {name = xxx ,age = xx } equel : url ? name=xxx&age=xx
 * @param options
 * @returns {*}
 */
proxyRequest.get = (url, data, options, checkResponseCode=true) => {
  options = options || {};
  url = data ? `${url}?${qsStringify(data)}` : url;
  return proxyRequest(url, options, checkResponseCode);
};
/**
 *
 * @param url
 * @param data
 * @param options
 * @returns {*}
 */
proxyRequest.post = (url, data, options, checkResponseCode=true) => {
  options = options || {};
  options.body = data;
  options.method = 'POST';
  return proxyRequest(url, options, checkResponseCode);
};

/**
 *
 * @param url
 * @param data
 * @param options
 * @returns {*}
 */
proxyRequest.put = (url, data, options, checkResponseCode=true) => {
  options = options || {};
  options.body = data || {};
  options.method = 'PUT';
  return proxyRequest(url, options, checkResponseCode);
};

/**
 *
 * @param url
 * @param data
 * @param options
 * @returns {*}
 */
proxyRequest.delete = (url, data, options, checkResponseCode=true) => {
  options = options || {};
  options.body = data || {};
  options.method = 'DELETE';
  return proxyRequest(url, options, checkResponseCode);
};

/**
 * @param url
 * @param options
 * @returns {*}
 */
export default proxyRequest;
