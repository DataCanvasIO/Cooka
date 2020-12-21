import time
from cooka.common import util
from cooka.common.log import log_core as logger
from cooka.common.model import AnalyzeStep, JobStep, SampleConf
from cooka.common import client
from cooka.core.analyzer import PandasAnalyzer

# [1]. parse arguments
import argparse
parser = argparse.ArgumentParser(description='Analyze dataset.', add_help=True)
parser.add_argument("--file_path", help="file_path", default=None, required=True)
parser.add_argument("--job_name", help="job_name", default=None, required=True)
parser.add_argument("--dataset_name", help="dataset_name", default=None, required=True)
parser.add_argument("--sample_strategy", help="sample_strategy", default=None, required=True)
parser.add_argument("--percentage", help="percentage", default=20, required=False)
parser.add_argument("--n_rows", help="n_rows", default=1000, required=False)
parser.add_argument("--server_portal", help="server_portal", default="http://localhost:8000", required=False)

# python /cooka/cooka/core/analyze_job.py --file_path=/Users/wuhf/Documents/datasets/bankdata.csv --job_name=job_analyze_bankdata_20201010175013832097 --dataset_name=bankdata_2 --sample_strategy=random_rows --n_rows=1000

args_namespace = parser.parse_args()

file_path = args_namespace.file_path
job_name = args_namespace.job_name
dataset_name = args_namespace.dataset_name

sample_strategy = args_namespace.sample_strategy

# parse params
if SampleConf.Strategy.Percentage == sample_strategy:
    percentage = int(args_namespace.percentage)
    n_rows = None
elif SampleConf.Strategy.RandomRows == sample_strategy:
    n_rows = int(args_namespace.n_rows)
    percentage = None
else:
    percentage = None
    n_rows = None

server_portal = args_namespace.server_portal

print("=======Analyze Config======")
print(f"file_path: {file_path}")
print(f"job_name: {job_name}")
print(f"dataset_name: {dataset_name}")
print(f"sample_strategy: {file_path}")
print(f"percentage: {percentage}")
print(f"n_rows: {n_rows}")
print(f"server_portal: {server_portal}")
print("=========================")

# label_col = self.analyze_job_conf.label_col  # data label
# if label_col is None or len(label_col) < 1:
#     logger.warning("Param 'label_col' not set, does not calculate relevance. ")
sample_conf = SampleConf(sample_strategy=sample_strategy, percentage=percentage, n_rows=n_rows)
util.validate_sample_conf(sample_conf)

# [2]. load data
t = time.time()
load_extension = None
load_status = JobStep.Status.Succeed
try:
    analyzer = PandasAnalyzer(file_path=file_path, label_col=None,  sample_conf=sample_conf)
    load_extension = {
        "n_rows_used": analyzer.n_rows_used,
        "n_cols_used": analyzer.n_cols,
        "n_rows": analyzer.n_rows,
        "n_cols": analyzer.n_cols,
    }
except Exception as e:
    load_status = JobStep.Status.Failed
    raise e
finally:
    client.analyze_callback(portal=server_portal,
                            dataset_name=dataset_name,
                            analyze_job_name=job_name,
                            type=AnalyzeStep.Types.Load,
                            status=load_status,
                            took=util.time_diff(time.time(), t),
                            extension=load_extension)
    logger.info("Load dataset finished. ")


# [3]. do analyze
t = time.time()
analyze_extension = None
analyze_status = JobStep.Status.Succeed
try:
    dataset_stats = analyzer.do_analyze_csv()
    hints = []
    if dataset_stats.n_cols > 1000:
        hints.append({
            "type": "Warning",
            "message": "More than 1,000 columns dataset requires a long time to train."
        })

    if dataset_stats.n_rows > 1000000:
        hints.append({
            "type": "Warning",
            "message": "More than 1,000,000 rows dataset requires a long time to train."
        })
    analyze_extension = dataset_stats.to_dict()
    # del extension['name']
    # del extension['create_datetime']
    analyze_extension['hints'] = hints
    # 增加抽样信息
    analyze_extension['sample_conf'] = sample_conf.to_dict()

except Exception as e:
    analyze_status = JobStep.Status.Failed
    raise e
finally:
    client.analyze_callback(portal=server_portal,
                            dataset_name=dataset_name,
                            analyze_job_name=job_name,
                            type=AnalyzeStep.Types.Analyzed,
                            status=analyze_status,
                            took=util.time_diff(time.time(), t),
                            extension=analyze_extension)
    logger.info("Analyze dataset finished. ")
