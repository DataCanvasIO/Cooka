# -*- encoding: utf-8 -*-
import time
import os
from cooka.common import util, dataset_util
from cooka.common.consts import BATCH_PREDICTION_COL
from cooka.common.log import log_core as logger
from cooka.common import client
from cooka.common import consts

from cooka.common.model import AnalyzeStep, JobStep, PredictStepType, Model, Feature, ModelFeature, FrameworkType
import pandas as pd
from deeptables.models import DeepTable
from os import path as P
import argparse
parser = argparse.ArgumentParser(description='Analyze dataset.', add_help=True)
parser.add_argument("--input_file_path", help="input_file_path", default=None, required=True)
parser.add_argument("--reserved_cols", help="reserved_cols", default=None, required=False)
parser.add_argument("--model_name", help="model_name", default=None, required=True)
parser.add_argument("--dataset_name", help="dataset_name", default=None, required=True)
parser.add_argument("--job_name", help="job_name", default=None, required=True)
parser.add_argument("--has_header", help="has_header", default=None, required=True)
parser.add_argument("--default_headers", help="default_headers", default=None, required=False)
parser.add_argument("--server_portal", help="server_portal", default=None, required=True)

# [1]. read config
args_namespace = parser.parse_args()

input_file_path = args_namespace.input_file_path
reserved_cols = args_namespace.reserved_cols
model_name = args_namespace.model_name
dataset_name = args_namespace.dataset_name
job_name = args_namespace.job_name
has_header = eval(args_namespace.has_header)
default_headers = args_namespace.default_headers
server_portal = args_namespace.server_portal

print("========Batch Predict Config========")
print(f"input_file_path: {input_file_path}")
print(f"reserved_cols: {reserved_cols}")
print(f"model_name: {model_name}")
print(f"dataset_name: {dataset_name}")
print(f"job_name: {job_name}")
print(f"has_header: {has_header}")
print(f"default_headers: {default_headers}")
print(f"server_portal: {server_portal}")
print("====================================")

# [2]. load data
t_load_start = time.time()
load_extension = None
load_status = JobStep.Status.Succeed
try:
    # May has no header
    if default_headers is not None:
        default_headers = default_headers.split(",")
    df = util.read_csv(input_file_path, has_header, default_headers)
    df_origin = df.copy()

    load_extension = {
        "n_rows": df.shape[0],
        "n_cols": df.shape[1]
    }

except Exception as e:
    load_status = JobStep.Status.Failed
    raise e
finally:
    client. batch_predict_callback(portal=server_portal,
                                   dataset_name=dataset_name,
                                   model_name=model_name,
                                   batch_predict_job_name=job_name,
                                   type=PredictStepType.Load,
                                   status=load_status,
                                   took=time.time()-t_load_start,
                                   extension=load_extension)
    logger.info("Load dataset finished. ")


# [3]. load model
t_load_model_start = time.time()
load_model_status = JobStep.Status.Succeed
load_model_extension = None
try:
    model_dict = client.retrieve_model(portal=server_portal, dataset_name=dataset_name, model_name=model_name)
    features = model_dict['inputs']

    logger.info("Before cast type: ")
    logger.info(df.dtypes)
    X = dataset_util.cast_df(df, features, remove_unnecessary_cols=True)
    logger.info("After cast type: ")
    logger.info(X.dtypes)

    abs_model_path = P.join(consts.DATA_DIR, model_dict['model_path'])

    framework = model_dict['framework']

    if framework == FrameworkType.DeepTables:
        model = DeepTable.load(P.join(abs_model_path, 'model'))
    elif framework == FrameworkType.GBM:
        model = util.load_pkl(P.join(abs_model_path, 'model.pkl'))
    else:
        raise ValueError(f"Unseen model framework: {framework}")
    load_model_extension = {
        "model_size": model_dict['model_file_size']
    }
except Exception as e:
    evaluate_status = JobStep.Status.Failed
    raise e
finally:
    client.batch_predict_callback(portal=server_portal,
                                   dataset_name=dataset_name,
                                   model_name=model_name,
                                   batch_predict_job_name=job_name,
                                   type=PredictStepType.LoadModel,
                                   status=load_model_status,
                                   took=time.time()-t_load_model_start,
                                   extension=load_model_extension)
    logger.info("Load model finished. ")

# [4]. evaluate dataset
t_evaluate_start = time.time()
evaluate_status = JobStep.Status.Succeed
try:
    y_pred = model.predict(X)
    # dt regression model return (n, 1)
    import numpy as np
    if not isinstance(y_pred, np.ndarray):
        y_pred = np.ndarray(y_pred)
    if len(y_pred.shape) == 2:
        y_pred = y_pred.reshape((-1, ))  # reshape to (1, n) to  (n, )
    # proba = dt_model.predict_proba(X)
except Exception as e:
    evaluate_status = JobStep.Status.Failed
    raise e
finally:
    client.batch_predict_callback(portal=server_portal,
                                   dataset_name=dataset_name,
                                   model_name=model_name,
                                   batch_predict_job_name=job_name,
                                   type=PredictStepType.Evaluate,
                                   status=evaluate_status,
                                   took=time.time()-t_evaluate_start,
                                   extension=None)
    logger.info("Evaluate input file finished. ")


# [4]. write result
write_result_extension = {}
t_write_result_start = time.time()
write_result_status = AnalyzeStep.Status.Succeed
try:
    df = X  # remained cols
    if reserved_cols is not None and len(reserved_cols) > 0:
        result_df = df_origin[reserved_cols]
        result_df[BATCH_PREDICTION_COL] = y_pred
    else:
        result_df = pd.DataFrame(data={BATCH_PREDICTION_COL: y_pred})

    output_path = P.join(consts.PATH_TMP_PREDICT, f"{model_name}_{util.human_datetime()}.csv")
    if not P.exists(consts.PATH_TMP_PREDICT):
        os.makedirs(consts.PATH_TMP_PREDICT)

    result_df.to_csv(output_path, index=False)
    logger.info(f"Write result finished at: {output_path}")
    write_result_extension = {
        "output_path": util.relative_path(output_path)
    }
except Exception as e:
    write_result_status = AnalyzeStep.Status.Failed
    raise e
finally:
    client.batch_predict_callback(portal=server_portal,
                                   dataset_name=dataset_name,
                                   model_name=model_name,
                                   batch_predict_job_name=job_name,
                                   type=PredictStepType.WriteResult,
                                   status=write_result_status,
                                   took=time.time()-t_write_result_start,
                                   extension=write_result_extension)

