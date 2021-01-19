# -*- encoding: utf-8 -*-
from jinja2 import Template
from os import path as P

# 训练代码生成器

# 1. 生成导入包
# 2. 生成配置
# 3. 生成数据拆分
# 4. 生成空间
# 5. 生成训练代码
# 6. 生成评估代码
from cooka.common.model import TrainJobConf, ExperimentConf

train_job_conf = TrainJobConf()
experiment_conf = ExperimentConf()
server_portal = "http://localhost:8000"
model_name = "my_model_hh"

train_template_file = P.join(P.dirname(P.abspath(__file__)), 'train.Jinja2')


with open(train_template_file, 'r') as f:
    template = Template(f.read())


params_dict = {
    "server_portal": server_portal,
    "train_job_name": train_job_conf.name,
    "model_name": model_name,

    "train_file_path": experiment_conf.file_path,
    "test_file_path": experiment_conf.test_file_path,
    "task_type": experiment_conf.task_type,
    "dataset_name": experiment_conf.dataset_name,
    "label_col": experiment_conf.label_col,
    "pos_label": experiment_conf.pos_label,
    "train_mode": experiment_conf.train_mode,
    "partition_strategy": experiment_conf.partition_strategy,


    "datetime_series_col": experiment_conf.datetime_series_col,

    "framework": train_job_conf.framework,
    "max_trials": train_job_conf.max_trials,
}

if experiment_conf.partition_strategy == ExperimentConf.PartitionStrategy.TrainValidationHoldout:
    params_dict['holdout_percentage'] = experiment_conf.train_validation_holdout.holdout_percentage
    params_dict["train_percentage"] = experiment_conf.train_validation_holdout.train_percentage,
    params_dict["validation_percentage"] = experiment_conf.train_validation_holdout.validation_percentage,
else:
    params_dict['holdout_percentage'] = experiment_conf.cross_validation.holdout_percentage
    params_dict["n_folds"] = experiment_conf.cross_validation.n_folds,


# cross_validation

print(template)

s = template.render(params_dict)
print(s)
