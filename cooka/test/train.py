# -*- encoding: utf-8 -*-


# -*- encoding: utf-8 -*-
import pandas as pd
import sklearn
import math
import shap
import requests
import pickle
import numpy as np
import matplotlib.pyplot as plt
from os import path as P
from sklearn.model_selection import train_test_split
from sklearn import metrics

from cooka.common import dataset_util
from cooka.common import util
from deeptables.models.hyper_dt import HyperDT, DnnModule, DTModuleSpace, DTFit, DTEstimator
from deeptables.utils import consts as DT_consts
from deeptables.utils.shap import DeepTablesExplainer

from hypernets.core.callbacks import *
from hypernets.core.ops import HyperInput, ModuleChoice
from hypernets.core.search_space import *
from hypernets.core.searcher import OptimizeDirection
from hypernets.searchers.mcts_searcher import MCTSSearcher

from hypergbm.estimators import LightGBMEstimator, XGBoostEstimator, CatBoostEstimator
from hypergbm.hyper_gbm import HyperGBM
from hypergbm.pipeline import DataFrameMapper
from hypergbm.sklearn.sklearn_ops import numeric_pipeline_complex, categorical_pipeline_simple
from hypernets.searchers.random_searcher import RandomSearcher
from hypergbm.search_space import search_space_general
from hypernets.experiment.general import GeneralExperiment
from tabular_toolbox.column_selector import column_object

shap.initjs()
Status_Failed = 'failed'
Status_Succeed = 'succeed'
def train_callback(portal, train_job_name, dataset_name, type, status, took, extension, **kwargs):
    url = f"{portal}/api/dataset/{dataset_name}/feature-series/default/train-job/{train_job_name}"
    # req_body_dict = \
    #     {
    #         "type": type,
    #         "status": status,
    #         "took": took,
    #         "datetime": round(time.time() * 1000),
    #         "extension": extension
    #     }
    # req_body = json.dumps(req_body_dict)
    # print(f"Send train process event: \n{url}\n{req_body}")
    # response = requests.post(url, data=req_body, timeout=20, headers={"Content-Type": "application/json;charset=utf-8"})
    # response_dict = json.loads(response.text)
    # code = response_dict["code"]
    # if code != 0:
    #     raise Exception(f"Update failed, {response.text}")
    # return response_dict['data']


class TrainTrailCallback(Callback):
    def __init__(self, server_portal, train_job_name, dataset_name):
        super(TrainTrailCallback, self).__init__()
        self.server_portal = server_portal
        self.train_job_name = train_job_name
        self.dataset_name = dataset_name

    def on_build_estimator(self, hyper_model, space, estimator, trail_no):
        pass

    def on_trail_begin(self, hyper_model, space, trail_no):
        pass
        #trail_extension = {
        #    "trail_no": trail_no
        #}
        #train_callback(self.server_portal, self.train_job_name, self.dataset_name, 'optimize_start', 'succeed', 0, trail_extension)

    def get_space_params(self, space):
        params_dict = {}
        for hyper_param in space.get_all_params():
            param_name = hyper_param.alias[len(list(hyper_param.references)[0].name) + 1:]
            param_value = hyper_param.value
            # only show number param
            if isinstance(param_value, int) or isinstance(param_value, float):
                if not isinstance(param_value, bool):
                    params_dict[param_name] = param_value
        return params_dict
    def ensure_number(self, value, var_name):
        if value is None:
             raise ValueError(f"Var {var_name} can not be None.")
        else:
            if not isinstance(value, float) and not isinstance(value, int):
                raise ValueError(f"Var {var_name} = {value} not a number.")


    def on_trail_end(self, hyper_model, space, trail_no, reward, improved, elapsed):
        self.ensure_number(reward, 'reward')
        self.ensure_number(trail_no, 'trail_no')
        self.ensure_number(elapsed, 'elapsed')

        trail_extension = {
            "trail_no": trail_no,
            "reward": reward,
            "elapsed": elapsed,
            "params": self.get_space_params(space)
        }
        train_callback(self.server_portal, self.train_job_name, self.dataset_name, 'optimize', Status_Succeed, elapsed, trail_extension)

    def on_skip_trail(self, hyper_model, space, trail_no, reason, reward, improved, elapsed):
        pass
        # trail_extension = {
        #     "trail_no": trail_no,
        #     "elapsed": elapsed,
        #     "params": self.get_space_params(space),
        #     "message": str(reason)
        # }
        # train_callback(self.server_portal, self.train_job_name, self.dataset_name, 'optimize', Status_Succeed, elapsed, trail_extension)

# [1]. train config
train_file_path = "/Users/wuhf/cooka/dataset/iris_8/data.csv"
test_file_path = None
server_portal = "http://localhost:8240"
max_trails = 10
task_type = "multi_classification"
dataset_name = "iris_8"
dataset_has_header = True

dataset_default_headers = None
label_col = "Species"
pos_label = None
train_mode = "quick"
framework = "HyperGBM"
partition_strategy = "train_validation_holdout"
holdout_percentage = 10
n_folds = None
train_percentage = 80
validation_percentage = 10
datetime_series_col = None
train_job_name = "train_job_iris_8_HyperGBM_20201216174345819774"
model_name = "iris_8_gbm_1"
model_feature_list = [{"name": "SepalLengthCm", "type": "continuous", "data_type": "float64"}, {"name": "SepalWidthCm", "type": "continuous", "data_type": "float64"}, {"name": "PetalLengthCm", "type": "continuous", "data_type": "float64"}, {"name": "PetalWidthCm", "type": "continuous", "data_type": "float64"}]
data_root = "/Users/wuhf/cooka"

print("=================Train Config================")
print(f"train_file_path: {train_file_path}")
print(f"test_file_path: {test_file_path}")
print(f"server_portal: {server_portal}")
print(f"max_trails: {max_trails}")
print(f"task_type: {task_type}")
print(f"dataset_name: {dataset_name}")
print(f"dataset_has_header: {dataset_has_header}")
print(f"dataset_default_headers: {dataset_default_headers}")
print(f"label_col: {label_col}")
print(f"pos_label: {pos_label}")
print(f"train_mode: {train_mode}")
print(f"framework: {framework}")
print(f"partition_strategy: {partition_strategy}")
print(f"holdout_percentage: {holdout_percentage}")
print(f"n_folds: {n_folds}")
print(f"train_percentage: {train_percentage}")
print(f"validation_percentage: {validation_percentage}")
print(f"datetime_series_col: {datetime_series_col}")
print(f"train_job_name: {train_job_name}")
print(f"model_name: {model_name}")
print(f"data_root: {data_root}")
print("============================================")


# [2]. data partition
load_start_time = time.time()
load_status = Status_Succeed
try:


    df = pd.read_csv(train_file_path)


    X_train, X_test = train_test_split(df, test_size=0.1,  random_state=42, shuffle=True)

    y_train = X_train.pop(label_col)
    y_test = X_test.pop(label_col)
    X_train = dataset_util.cast_df(X_train, model_feature_list, remove_unnecessary_cols=True)
    X_test = dataset_util.cast_df(X_test, model_feature_list, remove_unnecessary_cols=True)
    classes = list(set(y_train).union(set(y_test)))
except Exception as e:
    load_status = Status_Failed
    raise e
finally:
    train_callback(server_portal, train_job_name, dataset_name, 'load', load_status, time.time() - load_start_time, None)

# [3]. search best params
t_search_begin = time.time()
search_status = Status_Succeed
try:

    reward_metric =  "accuracy"
    optimize_direction = OptimizeDirection.Maximize
    print(f"Optimize direction: {optimize_direction}, reward metric: reward_metric")




    search_space = search_space_general




    rs = MCTSSearcher(search_space, max_node_space=10, optimize_direction=optimize_direction)
    hk = HyperGBM(rs, task="classification", reward_metric=reward_metric,
                  callbacks=[TrainTrailCallback(server_portal, train_job_name, dataset_name), SummaryCallback(), FileLoggingCallback(rs), EarlyStoppingCallback(max_no_improvement_trails=5, mode=optimize_direction.value)])
    experiment = GeneralExperiment(hk, X_train, y_train, X_eval=X_test, y_eval=y_test)
    estimator = experiment.run(use_cache=True, max_trails=max_trails)

except Exception as e:
    search_status = Status_Failed
    raise e
finally:
    train_callback(server_portal, train_job_name, dataset_name, 'searched', search_status, time.time() - t_search_begin, None)


# [4]. evaluate
t_evaluate_begin = time.time()
evaluate_status = Status_Succeed
evaluate_extension = {}
try:

    y_pred = estimator.predict(X_test)

    y_score = estimator.predict_proba(X_test)

    y_scores = y_score
    y_score = y_score[:, 1]





    accuracy_value = round(metrics.accuracy_score(y_test, y_pred), 4)
    f1_value = round(metrics.f1_score(y_test, y_pred, average='micro',), 4)
    fbeta_value = round(metrics.fbeta_score(y_test, y_pred, beta=10, average='micro'), 4)
    precision_value = round(metrics.precision_score(y_test, y_pred, average='micro'), 4)
    recall_value = round(metrics.recall_score(y_test, y_pred, average='micro'), 4)
    log_loss_value = round(metrics.log_loss(y_test, y_scores), 4)
    metrics_dict = {
        "accuracy": accuracy_value,
        "f1": f1_value,
        "fbeta": fbeta_value,
        "precision": precision_value,
        "recall": recall_value,
        "log_loss": log_loss_value
    }
    performance = {"metrics": metrics_dict, "confusion_matrix": None, "roc_curve": None}

    evaluate_extension['performance'] = performance

except Exception as e:
    evaluate_status = Status_Failed
    raise e
finally:
    train_callback(server_portal, train_job_name, dataset_name, 'evaluate', evaluate_status, time.time() - t_evaluate_begin, evaluate_extension)

# [5]. persist model
persist_status = Status_Succeed
t_persist_begin = time.time()
persist_extension = {}
try:

    model_dir_path = util.model_dir(dataset_name, model_name)
    if not P.exists(model_dir_path):
        os.makedirs(model_dir_path)

    model_data_path = P.join(model_dir_path, 'model.pkl')
    with open(model_data_path, 'wb') as f:
        pickle.dump(estimator, f)
    
    model_file_size = P.getsize(model_data_path)

    print(f"Persist model to: {model_data_path}")
    persist_extension = {
        "model_file_size": model_file_size
    }
except Exception as e:
    persist_status = Status_Failed
    raise e
finally:
    train_callback(server_portal, train_job_name, dataset_name, 'persist', persist_status, time.time() - t_persist_begin, persist_extension)