import requests

from cooka.common import util
from cooka.common.log import log_web as logger

HEADERS = {"Content-Type": "application/json;charset=utf-8"}
TIMEOUT = 30


def _checkout_response_json(response):
    # print("Response: ")
    # print(response.text)
    response_dict = util.loads(response.text)
    code = response_dict["code"]
    if code != 0:
        raise Exception(f"Update failed, {response.text}")
    return response_dict['data']


def callback(url, type, status, took, extension, **kwargs):
    req_body_dict = \
        {
            "type": type,
            "status": status,
            "took": took,
            "datetime": util.get_now_long(),
            "extension": extension
        }

    req_body = util.dumps(req_body_dict)
    logger.info(f"Send process event: \n{url}\n{req_body}")
    # Note: http body should be a bytes or will be encode by "requests" and using iso-8859-1
    response = requests.post(url, data=req_body.encode('utf-8'), timeout=TIMEOUT, headers=HEADERS)
    _checkout_response_json(response)


def analyze_callback(portal, analyze_job_name, dataset_name, type, status, took, extension, **kwargs):
    url = f"{portal}/api/dataset/{dataset_name}/analyze-job/{analyze_job_name}"
    callback(url, type, status, took, extension)


def train_callback(portal, train_job_name, dataset_name, type, status, took, extension, **kwargs):
    url = f"{portal}/api/dataset/{dataset_name}/feature-series/default/train-job/{train_job_name}"
    callback(url, type, status, took, extension)


def batch_predict_callback(portal, dataset_name, model_name, batch_predict_job_name, type, status, took, extension, **kwargs):
    url = f"{portal}/api/dataset/{dataset_name}/feature-series/default/model/{model_name}/batch-predict-job/{batch_predict_job_name}"
    callback(url, type, status, took, extension)


def retrieve_model(portal, dataset_name, model_name):
    url = f"{portal}/api/dataset/{dataset_name}/feature-series/default/model/{model_name}"
    response = requests.get(url, timeout=TIMEOUT, headers=HEADERS)
    return _checkout_response_json(response)


def retrieve_dataset(portal, dataset_name):
    url = f"{portal}/api/dataset/{dataset_name}"
    response = requests.get(url, timeout=TIMEOUT, headers=HEADERS)
    return _checkout_response_json(response)
