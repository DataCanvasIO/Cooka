# -*- encoding: utf-8 -*-
"""
Only analyzed dataset and use pearson instead Cramer's V ,
"""
import time
import pandas as pd
import argparse

from sklearn.preprocessing import LabelEncoder
from cooka.common import util, dataset_util
from cooka.common.model import FeatureType, DatasetStats, AnalyzeStep, JobStep
from cooka.common.log import log_web as logger
from cooka.common import client

# 1. parse params
parser = argparse.ArgumentParser(description='Analyze dataset.', add_help=True)
parser.add_argument("--dataset_name", help="dataset_name", default=None, required=True)
parser.add_argument("--label_col", help="label_col", default=None, required=True)
parser.add_argument("--job_name", help="job_name", default=None, required=True)
parser.add_argument("--server_portal", help="server_portal", default="http://localhost:8000", required=False)

args_namespace = parser.parse_args()

dataset_name = args_namespace.dataset_name
server_portal = args_namespace.server_portal
label_col = args_namespace.label_col
job_name = args_namespace.job_name

print("===========Calculate Pearson Corr Config==========")
print(f"file_path: {dataset_name}")
print(f"label_col: {label_col}")
print(f"job_name: {job_name}")
print(f"server_portal: {server_portal}")
print("==================================================")

t = time.time()  # begin time

# 2. retrieve dataset info
dataset_detail = client.retrieve_dataset(server_portal, dataset_name)
dataset_stats = DatasetStats.load_dict(dataset_detail)

# 3. read df
df = util.read_csv(util.abs_path(dataset_stats.file_path), dataset_stats.has_header, dataset_stats.features_names)
df = dataset_util.cast_df(df, dataset_detail['features'], True)
y = df[label_col]

# 4. encode y if is categorical # Do not calculate if categorical
# for f in dataset_stats.features:
#     if f.name == label_col:
#         if f.type == FeatureType.Categorical:
#             logger.info(f"Encode label column {label_col} because type is {f.type}. ")
#             y = pd.Series(LabelEncoder().fit_transform(y), name=label_col)

# 5. encode categorical features
pearson_corr_dict = {}
for f in dataset_stats.features:
    if f.type == FeatureType.Categorical:
        logger.info(f"Skip categorical feature {f.name} ")
        # lb = LabelEncoder()
        # encoded_series = pd.Series(lb.fit_transform(df[f.name]), name=f.name)
        # pearson_corr_dict[f.name] = y.corr(encoded_series, method='pearson')
        pearson_corr_dict[f.name] = None

    elif f.type in [FeatureType.Continuous, FeatureType.Datetime]:
        pearson_corr_dict[f.name] = y.corr(df[f.name], method='pearson')
    else:
        logger.info(f"Encode feature {f.name} type is {f.type}, skipped calc corr. ")
        pearson_corr_dict[f.name] = None  # not support text feature

extension = {"corr": pearson_corr_dict, "label_col": label_col}

# 6. send back calc result
client.analyze_callback(portal=server_portal,
                        dataset_name=dataset_name,
                        analyze_job_name=job_name,
                        type=AnalyzeStep.Types.PatchCorrelation,
                        status=JobStep.Status.Succeed,
                        took=util.time_diff(time.time(), t),
                        extension=extension)
