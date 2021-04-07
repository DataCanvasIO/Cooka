# -*- encoding: utf-8 -*-
from collections import OrderedDict
from cooka.common import consts
from cooka.common.exceptions import EntityNotExistsException
from cooka.common.model import ExperimentConf, TrainJobConf, FrameworkType, JobStep, TrainStep, CrossValidation, \
    TrainValidationHoldout, Model, ModelStatusType, \
    AnalyzeStep, FeatureType, FeatureValueCount, SampleConf, TrainValidationHoldoutDefault, TrialStatus
from cooka.dao.dao import ExperimentDao, DatasetDao
from cooka.dao.entity import ExperimentEntity, MessageEntity
from cooka.dao import db
from cooka.common import util
import abc
from cooka.common.model import TrainMode
from cooka.common.model import Feature, DatasetStats, ModelFeature
from cooka.common.log import log_web as log
from cooka.common.model import TaskType
from cooka.common.model import TrainJobConf
from cooka.service.dataset_service import DatasetService
from os import path as P
from jinja2 import Template
import sys, os
from jinja2.loaders import FileSystemLoader
from jinja2 import Environment
import math
import subprocess
import pandas as pd


class ExperimentService(object):

    model_dao = ExperimentDao()
    dataset_dao = DatasetDao()
    dataset_service = DatasetService()

    def create_temporary_model(self, session, model_name, no_experiment, input_features, experiment_conf: ExperimentConf, train_job_conf: TrainJobConf):
        # 1. create a temporary model
        now = util.get_now_datetime()
        extension = {
            "experiment_conf": experiment_conf.to_dict(),
            "train_job_conf": train_job_conf.to_dict(),
        }
        gbm_model = ExperimentEntity(name=model_name,
                                     framework=train_job_conf.framework,
                                     dataset_name=experiment_conf.dataset_name,
                                     no_experiment=no_experiment,
                                     inputs=input_features,
                                     task_type=experiment_conf.task_type,
                                     model_path=util.model_dir(experiment_conf.dataset_name, model_name),
                                     status=ModelStatusType.Running,
                                     train_job_name=train_job_conf.name,
                                     extension=extension,
                                     create_datetime=now,
                                     last_update_datetime=now)
        session.add(gbm_model)

    def _infer_task_type(self, f:Feature):
        n_unique = f.unique.value
        if n_unique == 2:
            # log.info(f'2 class detected,  so inferred as a [binary classification] task')
            return TaskType.BinaryClassification
        else:
            if 'float' in f.data_type:
                # log.info(f'Target column type is float, so inferred as a [regression] task.')
                return TaskType.Regression
            else:
                if n_unique > 1000:
                    if 'int' in f.type:
                        # log.info(
                        #   'The number of classes exceeds 1000 and column type is int, so inferred as a [regression] task ')
                        return TaskType.Regression
                    else:
                        raise ValueError(
                            'The number of classes exceeds 1000, please confirm whether your predict target is correct ')
                else:
                    print(f'{n_unique} class detected, inferred as a [multiclass classification] task')
                    return TaskType.MultiClassification

    def _find_feature(self, features, feature_name):
        for f in features:
            if f.name == feature_name:
                return f
        return None

    @staticmethod
    def calc_avg_trial_elapsed(model_name, model_status, succeed_trials):
        total_elapsed = 0
        if succeed_trials is not None and len(succeed_trials) > 0:
            for trial in succeed_trials:
                total_elapsed = total_elapsed + trial.extension['elapsed']
            return total_elapsed / len(succeed_trials)
        else:
            log.warning(f"Model = {model_name}, status={model_status} but has no trials, " +
                        "may be train script execute failed, see trial log for more detail.")
            return 0

    def find_running_model(self):
        with db.open_session() as s:
            return self.model_dao.find_running_model(s)

    @staticmethod
    def calc_remain_time(model: Model):
        if model.status in [ModelStatusType.Failed, ModelStatusType.Succeed]:
            return 0  # finished
        elif model.status == ModelStatusType.Running:
            model_train_process = model.progress
            if model_train_process is None or model_train_process in [TrainStep.Types.Load]:
                estimated_remaining_time = None
            elif model_train_process in [TrainStep.Types.Optimize]:  # in this stage already has a trial finished, before this stage has no evaluate remaining time
                # 1. calc avg elapsed
                avg_elapsed = ExperimentService.calc_avg_trial_elapsed(model.name, model_train_process, model.trials)

                # 2. calc estimated remaining time
                model_extension = model.extension
                train_mode = model_extension['experiment_conf']["train_mode"]  # extension must has experiment_conf and train_mode and not None
                max_trials = consts.TRAIN_MODE_MAX_TRIALS_MAPPING[train_mode]  # must has {train_mode}
                train_trial_no = model.train_trial_no
                estimated_remaining_time = (max_trials - train_trial_no) * avg_elapsed

                # 3. plus final train time and evaluate/persist time
                estimated_remaining_time + avg_elapsed + 30

            elif model_train_process in [TrainStep.Types.Searched]:
                avg_elapsed = ExperimentService.calc_avg_trial_elapsed(model.name, model_train_process, model.trials)
                # plus final train/evaluate/persist time
                estimated_remaining_time = avg_elapsed + 30

            elif model_train_process in [TrainStep.Types.FinalTrain, TrainStep.Types.Evaluate]:
                # plus final train/evaluate/persist time
                estimated_remaining_time = 30

            elif model_train_process in [TrainStep.Types.Persist]:  # finished
                estimated_remaining_time = 0  # remaining 0 seconds means finished.
            else:
                raise ValueError(f"Unseen model status: {model_train_process} ")
            return estimated_remaining_time
        else:
            raise ValueError(f"Unseen model status {model.status}")

    def get_experiments(self, dataset_name, page_num, page_size):
        # 1. validation params
        if page_num < 1:
            raise ValueError("Param page_num should >= 1'")

        if page_size < 1:
            raise ValueError("Param page_size should >= 1'")

        def f(model: Model):
            model_extension = model.extension
            train_mode = model_extension['experiment_conf']["train_mode"]  # extension must has experiment_conf and train_mode and not None
            max_trials = consts.TRAIN_MODE_MAX_TRIALS_MAPPING[train_mode]  # must has {train_mode}
            d = \
                {
                    "name": model.name,
                    "no_experiment": m.no_experiment,
                    "train_mode": m.extension['experiment_conf']['train_mode'],
                    "target_col": m.extension['experiment_conf']['label_col'],
                    "metric_name": consts.TASK_TYPE_OPTIMIZE_METRIC_MAPPING[m.task_type],   # m.extension['experiment_conf']['optimize_metric'],
                    "status": model.status,
                    "score": model.score,
                    "engine": m.extension['train_job_conf']['framework'],
                    "escaped": model.escaped_time_by_seconds(),
                    "log_file_path": model.log_file_path(),
                    "train_source_code_path": model.train_source_code_path(),
                    "train_notebook_uri": model.train_notebook_uri(),
                    "train_trial_no": 0 if model.train_trial_no is None else model.train_trial_no,
                    "max_train_trial_no": max_trials,
                    "estimated_remaining_time": ExperimentService.calc_remain_time(model),
                    "model_file_size": model.model_file_size
                }
            return d

        with db.open_session() as s:
            # check dataset
            dataset = self.dataset_dao.require_by_name(s, dataset_name)

            models, total = self.model_dao.find_by_dataset_name(s, dataset_name, page_num, page_size)
            experiments = []
            for m in models:
                model_as_dict = f(m)
                experiments.append(model_as_dict)

            # return sorted(experiments, key=lambda x: x['no_experiment'], reverse=True)
            return experiments, total

    def get_direction_source_code(self, metric_name):
        metric_name = metric_name.lower()
        if metric_name in ["auc", "accuracy"]:
            return "OptimizeDirection.Maximize"
        elif metric_name in ["rootmeansquarederror", 'rmse']:
            return "OptimizeDirection.Minimize"
        else:
            raise ValueError(f"Unknown metric name: {metric_name}")

    def get_optimize_metric(self, task_type, framework):
        dt_optimize_metrics = {
            TaskType.BinaryClassification: "AUC",
            TaskType.MultiClassification: "accuracy",
            TaskType.Regression: "RootMeanSquaredError"
        }

        gbm_optimize_metrics = {
            TaskType.BinaryClassification: "auc",
            TaskType.MultiClassification: "accuracy",
            TaskType.Regression: "rmse"
        }

        if framework == FrameworkType.DeepTables:
            metric = dt_optimize_metrics.get(task_type)
        elif framework == FrameworkType.GBM:
            metric = gbm_optimize_metrics.get(task_type)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

        if metric is None:
            raise ValueError(f"Unknown task type = {task_type}, framework = {framework}")
        return metric

    def get_default_metric(self, task_type):
        if task_type == TaskType.BinaryClassification:
            return "roc_auc"  # Must be auc for DT
        elif task_type == TaskType.MultiClassification:
            return "accuracy"
        elif task_type == TaskType.Regression:
            return 'rmse'
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    @staticmethod
    def generate_notebook_cell(text_source_code: str, cell_type: str = 'code'):

        code_cell = \
            {
                "cell_type": 'code',
                "execution_count": 1,
                "metadata": {},
                "outputs": [
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": []
                    }
                ],
                "source": text_source_code
            }

        markdown_cell = \
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": text_source_code
            }
        if cell_type == "markdown":
            return markdown_cell
        elif cell_type == "code":
            return code_cell
        else:
            raise ValueError(f"Unknown cell type: {cell_type}")


    @staticmethod
    def generate_notebook(cells):
        notebook_json = \
        {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "codemirror_mode": {
                        "name": "ipython",
                        "version": 3
                    },
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.7.7"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        return notebook_json

    def generate_code(self, model_name, model_input_features, n_rows, train_job_conf: TrainJobConf, experiment_conf: ExperimentConf):
        # 1. set earlystopping
        if experiment_conf.train_mode == TrainMode.Minimal:
            earlystopping_patience = "[1]"
        else:
            if n_rows <= 1000:
                earlystopping_patience = "[10, 50, 100]"
            elif 1000 < n_rows <= 10000 :
                earlystopping_patience = "[5, 10, 15]"
            else:
                earlystopping_patience = "[1, 3, 5]"

        # 2. set default header if has no header
        if not experiment_conf.dataset_has_header:
            if experiment_conf.dataset_default_headers is not None:
                dataset_default_headers_code = util.dumps(experiment_conf.dataset_default_headers, indent=None)
            else:
                raise ValueError("When dataset_has_header is False then param dataset_default_headers can be None.")
        else:
            dataset_default_headers_code = None

        # 3. make reader params
        pos_label = experiment_conf.pos_label
        pos_label_is_str = isinstance(pos_label, str)
        reward_metric = self.get_optimize_metric(experiment_conf.task_type, train_job_conf.framework)
        params_dict = {
            "server_portal": consts.SERVER_PORTAL,
            "train_job_name": train_job_conf.name,
            "data_root": consts.DATA_DIR,
            "model_name": model_name,
            "pos_label": pos_label,
            "earlystopping_patience": earlystopping_patience,
            "pos_label_is_str": pos_label_is_str,
            "train_file_path": experiment_conf.file_path,
            "test_file_path": experiment_conf.test_file_path,
            "task_type": experiment_conf.task_type,
            "gbm_task_type": experiment_conf.task_type,
            "dataset_name": experiment_conf.dataset_name,
            "label_col": experiment_conf.label_col,
            "pos_label_value": experiment_conf.pos_label,
            "train_mode": experiment_conf.train_mode,
            "partition_strategy": experiment_conf.partition_strategy,
            "datetime_series_col": experiment_conf.datetime_series_col,
            "partition_col": experiment_conf.partition_col,
            "reward_metric": reward_metric,
            "optimize_direction": self.get_direction_source_code(reward_metric),
            "framework": train_job_conf.framework,
            "max_trials": train_job_conf.max_trials,
            "dataset_has_header": experiment_conf.dataset_has_header,
            "dataset_default_headers": dataset_default_headers_code,
            "model_feature_list": util.dumps(model_input_features, indent=None)
        }

        if experiment_conf.partition_strategy == ExperimentConf.PartitionStrategy.TrainValidationHoldout:
            params_dict['holdout_percentage'] = experiment_conf.train_validation_holdout.holdout_percentage
            params_dict["train_percentage"] = experiment_conf.train_validation_holdout.train_percentage
            params_dict["validation_percentage"] = experiment_conf.train_validation_holdout.validation_percentage
            params_dict["random_state"] = experiment_conf.train_validation_holdout.random_state
        elif experiment_conf.partition_strategy == ExperimentConf.PartitionStrategy.Manual:
            pass
        elif experiment_conf.partition_strategy == ExperimentConf.PartitionStrategy.CrossValidation:
            params_dict['holdout_percentage'] = experiment_conf.cross_validation.holdout_percentage
            params_dict["n_folds"] = experiment_conf.cross_validation.n_folds
        else:
            raise Exception(f"Unseen partition strategy: {experiment_conf.partition_strategy} ")

        # 4. render raw python
        template_dir = P.join(consts.PATH_INSTALL_HOME, 'cooka', 'core', 'train_template')
        train_template_file = P.join(template_dir, 'target_raw_python.jinja2')
        with open(train_template_file, 'r') as f:
            raw_python_content = Environment(loader=FileSystemLoader(template_dir)).from_string(f.read()).render(params_dict)

        # 5. render notebook
        import copy
        params_dict_notebook = copy.deepcopy(params_dict)
        params_dict_notebook['target_source_type'] = 'notebook'

        def render_file_for_nb(name, comment=None):
            file_content = util.read_text(P.join(template_dir, name))
            c = Environment(loader=FileSystemLoader(template_dir)).from_string(file_content).render(params_dict_notebook)
            cell_code = ExperimentService.generate_notebook_cell(c, 'code')
            if comment is not None:
                cell_comment = ExperimentService.generate_notebook_cell(comment, 'markdown')
            else:
                cell_comment = None
            return cell_code, cell_comment


        task_type_name_dict = {
            TaskType.MultiClassification: "Multi Classification",
            TaskType.BinaryClassification: "Binary Classification",
            TaskType.Regression: "Regression"
        }
        framework_github_dict = {
            FrameworkType.DeepTables: "[DeepTables](https://github.com/DataCanvasIO/DeepTables)",
            FrameworkType.GBM: "[HyperGBM](https://github.com/DataCanvasIO/HyperGBM)" ,
        }

        example_doc = f"""# Training {experiment_conf.label_col} in {experiment_conf.dataset_name}
{task_type_name_dict[experiment_conf.task_type]} model by {framework_github_dict.get(train_job_conf.framework)}, Generated on {util.human_std_datetime()}"""

        cell_example_doc = ExperimentService.generate_notebook_cell(example_doc, 'markdown')
        cell_train_header, cell_train_header_comment = render_file_for_nb('train_header.jinja2')
        cell_train_config, cell_train_config_comment = render_file_for_nb('train_config.jinja2', "## [1]. train config")
        cell_train_data_partition, cell_train_data_partition_comment = render_file_for_nb('train_data_partition.jinja2', "## [2]. data partition")
        cell_train_search, cell_train_search_comment = render_file_for_nb('train_search.jinja2', "## [3]. search best params")
        # cell_train_final_train, cell_train_final_train_comment = render_file_for_nb('train_final_train.jinja2', "## [4]. final train")
        cell_train_evaluate, cell_train_evaluate_comment = render_file_for_nb('train_evaluate.jinja2', "## [4]. evaluate")

        cells = [cell_example_doc, cell_train_header, cell_train_config_comment, cell_train_config, cell_train_data_partition_comment, cell_train_data_partition, cell_train_search_comment, cell_train_search, cell_train_evaluate_comment, cell_train_evaluate]

        if experiment_conf.task_type == TaskType.BinaryClassification:
            cell_evaluate_confusion_matrix, cell_evaluate_confusion_matrix_comment = render_file_for_nb('plot_confusion_matrix.jinja2', "## 5. Plot confusion matrix")
            cell_evaluate_plot_roc_curve, cell_evaluate_plot_roc_curve_comment = render_file_for_nb('plot_roc_curve.jinja2', "## 6. Plot roc curve")
            cells.append(cell_evaluate_confusion_matrix_comment)
            cells.append(cell_evaluate_confusion_matrix)
            cells.append(cell_evaluate_plot_roc_curve_comment)
            cells.append(cell_evaluate_plot_roc_curve)

        if train_job_conf.framework == FrameworkType.GBM:
            cell_plot_feature_importance, plot_feature_importance_comment = render_file_for_nb('plot_feature_importance.jinja2', "## Plot feature importance")
            cells.append(plot_feature_importance_comment)
            cells.append(cell_plot_feature_importance)

        if train_job_conf.framework == FrameworkType.DeepTables:
            content_dt_explainer = \
            """dt_explainer = DeepTablesExplainer(estimator, X_test, num_samples=100)
shap_values = dt_explainer.get_shap_values(X_test[:1], nsamples='auto')"""
            cell_dt_explaine = ExperimentService.generate_notebook_cell(content_dt_explainer)
            cells.append(cell_dt_explaine)

            feature_importances = """shap.summary_plot(shap_values,X_test, plot_type="bar")"""
            cells.append(ExperimentService.generate_notebook_cell(feature_importances))

            prediction_explainer = """shap.decision_plot(dt_explainer.explainer.expected_value, shap_values[0], X_test.iloc[0])"""
            cells.append(ExperimentService.generate_notebook_cell(prediction_explainer))

        notebook_dict = ExperimentService.generate_notebook(cells)
        notebook_content = util.dumps(notebook_dict)

        return raw_python_content, notebook_content

    def run_train_job(self, conf: ExperimentConf, no_experiment: int, model_input_features:list, n_rows: int):
        framework = conf.engine

        # 1. create train conf
        job_name = f"train_job_{conf.dataset_name}_{framework}_{util.human_datetime()}"

        model_name = util.model_name(conf.dataset_name, no_experiment)  #f"{conf.dataset_name}_{no_experiment}"

        model_dir = util.model_dir(conf.dataset_name, model_name)
        os.makedirs(model_dir)
        train_source_code_path = P.join(model_dir, 'train.py')
        train_log = P.join(model_dir, f"train.log")

        train_job_conf = TrainJobConf(framework=framework,
                                      name=job_name,
                                      model_name=model_name,
                                      searcher=TrainJobConf.Searcher.MCTSSearcher,
                                      max_trials=consts.TRAIN_MODE_MAX_TRIALS_MAPPING[conf.train_mode],
                                      search_space=TrainJobConf.SearchSpace.Minimal)
        # 2. insert to db
        with db.open_session() as s:
            self.create_temporary_model(s, model_name, no_experiment, model_input_features, conf,  train_job_conf)

        # 3. generate train source code
        train_source_code, notebook_content = self.generate_code(model_name, model_input_features, n_rows, train_job_conf, conf)

        with open(train_source_code_path, 'w', encoding='utf-8') as f:
            f.write(train_source_code)

        notebook_file_path = P.join(model_dir, 'train.ipynb')
        with open(notebook_file_path, 'w', encoding='utf-8') as f:
            f.write(notebook_content)

        # 4. run train process
        # Note: if plus & at end of command, the process id will be plus 1 cause a bug
        command = f"nohup {sys.executable} {train_source_code_path} 1>{train_log} 2>&1"

        log.info(f"Run train job command: \n{command}")
        log.info(f"Log file:\ntail -f  {train_log}")
        log.info(f"Train source code:\n {train_source_code_path}")

        train_process = subprocess.Popen(["bash", "-c", command], stdout=subprocess.PIPE)

        with db.open_session() as s:
            self.model_dao.update_model_by_name(s, model_name, {"pid": train_process.pid})

        return train_job_conf.to_dict()

    def _handle_label_col(self, dataset_name, task_type, label_col, file_path):
        # calc correlation
        # 1. update label col, Avoiding that http request send first and not label_col not updated
        with db.open_session() as s:
            self.dataset_dao.update_by_name(s, dataset_name, {"label_col": label_col})

        # 2. start a process to analyze correlation
        analyze_pearson_job_name = util.analyze_data_job_name(P.basename(file_path))
        std_log = P.join(util.dataset_dir(dataset_name), f"{analyze_pearson_job_name}.log")
        if task_type == TaskType.Regression: # only for regression task and continuous feature
            command = f"nohup {sys.executable} {util.script_path('analyze_correlation_job.py')} --dataset_name={dataset_name} --label_col={label_col} --job_name={analyze_pearson_job_name} --server_portal={consts.SERVER_PORTAL} 1>{std_log} 2>&1"
            calc_correlation_process = subprocess.Popen(["bash", "-c", command], stdout=subprocess.PIPE)

            log.info(f"Run calculate pearson command: \n{command}")
            log.info(f"Log file:\ntail -f  {std_log}")
            log.info(f"Process id is {calc_correlation_process.pid}")
        else:
            log.info(f"Note a regression task, skip calc correlation.")

    def experiment(self, req_dict: dict):
        # 1. read params
        label_col = util.require_in_dict(req_dict, 'label_col', str)
        pos_label = util.get_from_dict(req_dict, 'pos_label', object)
        train_mode = util.get_from_dict(req_dict, 'train_mode', str)

        partition_strategy = util.require_in_dict(req_dict, 'partition_strategy', str)
        dataset_name = util.require_in_dict(req_dict, 'dataset_name', str)

        partition_col = util.get_from_dict(req_dict, 'partition_col', str)

        # todo check datetime_series_col
        datetime_series_col = util.get_from_dict(req_dict, 'datetime_series_col', str)

        experiment_engine = util.require_in_dict(req_dict, 'experiment_engine', str)
        if experiment_engine not in [FrameworkType.GBM, FrameworkType.DeepTables]:
            raise ValueError(f"Unseen experiment_engine {experiment_engine}")

        # 2. check partition_strategy
        cross_validation = None
        train_validation_holdout = None
        if partition_strategy == ExperimentConf.PartitionStrategy.CrossValidation:
            cross_validation_dict = util.require_in_dict(req_dict, 'cross_validation', dict)
            n_folds = util.require_in_dict(cross_validation_dict, 'n_folds', int)
            holdout_percentage = util.require_in_dict(cross_validation_dict, 'holdout_percentage', int)
            if 1 < n_folds <= 50:
                cross_validation = CrossValidation(n_folds=n_folds, holdout_percentage=holdout_percentage)
            else:
                raise ValueError(f"1 < n_folds <= 50 but current is: {n_folds}")
        elif partition_strategy == ExperimentConf.PartitionStrategy.TrainValidationHoldout:
            train_validation_holdout_dict = util.require_in_dict(req_dict, 'train_validation_holdout', dict)
            train_percentage = util.require_in_dict(train_validation_holdout_dict, 'train_percentage', int)
            validation_percentage = util.require_in_dict(train_validation_holdout_dict, 'validation_percentage', int)
            holdout_percentage = util.require_in_dict(train_validation_holdout_dict, 'holdout_percentage', int)
            random_state = util.require_in_dict(train_validation_holdout_dict, 'random_state', int)
            if train_percentage + validation_percentage + holdout_percentage != 100:
                raise ValueError("train_percentage plus validation_percentage plus holdout_percentage should equal 100.")
            train_validation_holdout = TrainValidationHoldout(train_percentage=train_percentage,
                                                              validation_percentage=validation_percentage,
                                                              holdout_percentage=holdout_percentage,
                                                              random_state=random_state)
        elif partition_strategy == ExperimentConf.PartitionStrategy.Manual:
            if partition_col is None or len(partition_col) <= 0:
                raise ValueError(f"{ExperimentConf.PartitionStrategy.Manual} strategy need a partition col but it's empty .")
        else:
            raise ValueError(f"Unknown partition strategy = {partition_strategy}")

        # 2. Retrieve data
        with db.open_session() as s:
            # 2.1. check dataset
            dataset = self.dataset_dao.require_by_name(s, dataset_name)
            if dataset is None:
                raise ValueError(f"Dataset={dataset_name} not exists.")
            dataset_stats = dataset.to_dataset_stats()

            # 2.2. generate new experiment name
            no_experiment = self.model_dao.get_max_experiment(s, dataset_name) + 1

        # 3. calc task type
        # 3.1. find label
        label_f: Feature = self._find_feature(dataset_stats.features, label_col)
        if label_f is None:
            raise ValueError(f"Label col = {label_col} is not in dataset {dataset_name} .")

        task_type = self._infer_task_type(label_f)

        # 3.2. check pos_label
        if task_type == TaskType.BinaryClassification:
            if pos_label is None:
                raise ValueError("Pos label can not be None when it's binary-classify")
            else:
                if isinstance(pos_label, str):
                    if len(pos_label) < 1:
                        raise ValueError("Pos label can not be empty when it's binary-classify")

        # 4. ensure dataset label is latest
        if dataset_stats.label_col is None:
            log.info(f"Dataset {dataset_name} label_col not set now, update to {label_col}")
            self._handle_label_col(dataset_name, task_type, label_col, dataset_stats.file_path)

        if dataset_stats.label_col != label_col:
            log.info(f"Dataset {dataset_name} label_col current is {dataset_stats.label_col}, but this experiment update to {label_col}")
            self._handle_label_col(dataset_name, task_type, label_col, dataset_stats.file_path)

        # 5. run experiment
        if not dataset_stats.has_header:
            dataset_default_headers = [f.name for f in dataset_stats.features]
        else:
            dataset_default_headers = None

        conf = ExperimentConf(dataset_name=dataset_name,
                              dataset_has_header=dataset_stats.has_header,
                              dataset_default_headers=dataset_default_headers,
                              train_mode=train_mode,
                              engine=experiment_engine,
                              label_col=label_col,
                              pos_label=pos_label,
                              task_type=task_type,
                              partition_strategy=partition_strategy,
                              cross_validation=cross_validation,
                              train_validation_holdout=train_validation_holdout,
                              datetime_series_col=datetime_series_col,
                              partition_col=partition_col,
                              file_path=dataset_stats.file_path)

        model_input_features = list(map(lambda _: ModelFeature(name=_.name, type=_.type, data_type=_.data_type).to_dict(), filter(lambda _: _.name != label_f.name, dataset_stats.features)))

        train_conf = self.run_train_job(conf, no_experiment, model_input_features,  dataset_stats.n_rows)

        return {
            "no_experiment": no_experiment,
            "experiment_conf": conf.to_dict(),
            "train_job_conf": train_conf
        }

    def infer_label_col(self, dataset_stats: DatasetStats):
        label_cols = ['label', 'target', 'y']
        # 1. find a col in { label_cols }
        for f in dataset_stats.features:
            if f.name.lower() in label_cols:
                return f

        # 2. if no col in { label_cols } using the latest col
        return dataset_stats.features[-1]

    def infer_pos_label(self, f: Feature):
        "Only for binary classification"
        # 1. load values count
        value_count: list = FeatureValueCount.load_dict_list(f.extension['value_count'])

        if len(value_count) != 2:
            raise ValueError(f"infer pos label only for binary classification, label name = {f.name}")

        # 2. cast to str and check it in { pos_labels }
        pos_labels = ['y', '1', 'yes', 'true']
        pos_label_dict = {v.type: str(v.type).lower() for v in value_count}
        for k, v in pos_label_dict.items():
            if v in pos_labels:
                return k

        # 3. if not match using the latest one
        return value_count[-1].type

    def get_recommended_conf_from_history(self, history_model: Model):
        model_extension = history_model.extension
        return ExperimentConf.load_dict(model_extension.get('experiment_conf'))

    def get_recommended_conf_as_new(self, dataset_name, dataset_stats: DatasetStats,  target_col: str):

        target_feature = None
        # 1. get target feature
        if target_col is None:
            # train infer label by rules
            target_feature: Feature = self.infer_label_col(dataset_stats)
        else:
            # get train col by target_col
            for f in dataset_stats.features:
                if f.name == target_col:
                    target_feature = f
                    break
            if target_feature is None:
                raise ValueError(f"Target col {target_col} not in dataset {dataset_name}. ")

        # 2. try to infer pos label
        task_type = self._infer_task_type(target_feature)
        if task_type == TaskType.BinaryClassification:
            pos_label = self.infer_pos_label(target_feature)
        else:
            pos_label = None

        return \
            ExperimentConf(label_col=target_feature.name,
                           task_type=task_type,
                           pos_label=pos_label,
                           train_mode=TrainMode.Quick,
                           engine=FrameworkType.GBM,
                           partition_strategy=ExperimentConf.PartitionStrategy.TrainValidationHoldout,
                           train_validation_holdout=TrainValidationHoldoutDefault,
                           datetime_series_col=None)

    def recommended_train_configuration(self, dataset_name, req_dict):
        datetime_series_col = None  # todo support datetime_series
        target_col = req_dict.get('target_col')

        # 1. read last train-job
        with db.open_session() as s:
            # 1.1. check dataset name
            dataset_stats = self.dataset_dao.require_by_name(s, dataset_name).to_dataset_stats()
            # 1.2. query models
            last_model = self.model_dao.checkout_one(self.model_dao.find_by_dataset_name(s, dataset_name, 1, 1)[0])

        # 2. infer conf
        if last_model is None:
            experiment_conf = self.get_recommended_conf_as_new(dataset_name, dataset_stats, target_col)
        else:
            _experiment_conf: ExperimentConf = self.get_recommended_conf_from_history(last_model)
            if target_col is not None and _experiment_conf.label_col != target_col:
                log.info(f"Change label from {_experiment_conf.label_col} to {target_col}, " +
                         f"and recommended params using new target.")
                experiment_conf = self.get_recommended_conf_as_new(dataset_name, dataset_stats, target_col)
            else:
                # use history
                experiment_conf = _experiment_conf

        train_validation_holdout = experiment_conf.train_validation_holdout
        cross_validation = experiment_conf.cross_validation

        conf = \
            {
                "label_col": experiment_conf.label_col,
                "task_type": experiment_conf.task_type,
                "pos_label": experiment_conf.pos_label,
                "train_mode": experiment_conf.train_mode,
                "engine": experiment_conf.engine,
                "partition_strategy": experiment_conf.partition_strategy,
                "train_validation_holdout": train_validation_holdout.to_dict() if train_validation_holdout is not None else None,
                "cross_validation": cross_validation.to_dict() if cross_validation is not None else None,
                "partition_col": experiment_conf.partition_col,
                "datetime_series_col": datetime_series_col
            }
        return conf

    def _update_model(self, session, model_name, progress, values):
        values['last_update_datetime'] = util.get_now_datetime()
        values['progress'] = progress
        affected = session.query(ExperimentEntity) \
            .filter(ExperimentEntity.name == model_name) \
            .update(values)
        if affected != 1:  # rollback them all
            raise Exception(f"Update error, affected rows={affected}")

    def _check_progress_change(self, wanna_progress, current_progress):
        if current_progress is None:  # has no progress at beginning
            return
        # todo copy to analyze job
        state_order = [TrainStep.Types.Load, TrainStep.Types.Searched, TrainStep.Types.FinalTrain, TrainStep.Types.Evaluate, TrainStep.Types.Persist]

        i = state_order.index(current_progress)  # may cause a error due state error, like: ValueError: 'c' is not in list
        if i == len(state_order) - 1:
            # end
            raise ValueError("End state can not change.")  # final state

        next_state = state_order[i+1]
        if wanna_progress != next_state:
            raise ValueError(f"State={current_progress} can goto {next_state} not {wanna_progress}")

    def require_model(self, s, model_name) -> Model:
        model_entity = self.model_dao.find_by_name(s, model_name)

        if model_entity is None:
            raise EntityNotExistsException(ExperimentEntity, model_name)
        return model_entity.to_model_bean()

    def retrieve(self, model_name):

        def _replace_NaN(v):
            if v is None:
                return v
            else:
                if math.isnan(v):
                    return None
                else:
                    return v

        with db.open_session() as s:
            model = self.require_model(s, model_name)

        # handle trials
        if model.trials is not None and len(model.trials)>0:
            failed_trials = {}
            for t in model.trials:
                if t.status == TrialStatus.Failed:
                    failed_trials[t.trial_no] = t.extension['reason']

            # Filter that failed trials
            succeed_trials = list(filter(lambda _: _.status == TrialStatus.Succeed, model.trials))
            if len(succeed_trials) > 0:
                param_names = [k for k in succeed_trials[0].extension['params']]
                trial_data_dict_list = []
                trial_params_values = []
                trial_index = []
                for t in succeed_trials:
                    param_values = [_replace_NaN(t.extension['params'].get(n)) for n in param_names]
                    trial_params_values.append(param_values)
                    trial_index.append(t.trial_no)
                df_train_params = pd.DataFrame(data=trial_params_values, columns=param_names)

                # remove if all is None
                df_train_params.dropna(axis=1, how='all', inplace=True)
                for i, t in enumerate(succeed_trials):
                    trial_extension = t.extension
                    trial_data_dict = {"reward": trial_extension['reward'], "params": [_replace_NaN(_) for _ in df_train_params.iloc[i].tolist()], "elapsed": trial_extension['elapsed']}
                    trial_data_dict_list.append(trial_data_dict)

                if len(df_train_params.columns.values) > 0:  # ensure not all params is None
                    trials_dict = {
                        "param_names": df_train_params.columns.tolist(),
                        "data": trial_data_dict_list
                    }
                else:
                    trials_dict = {}
            else:
                trials_dict = {}
        else:
            trials_dict = {}
            failed_trials = {}

        model_dict = model.to_dict()
        # update trials
        model_dict['trials'] = trials_dict
        model_dict['failed_trials'] = failed_trials
        model_dict['model_path'] = util.relative_path(model_dict['model_path'])
        model_dict['escaped'] = model.escaped_time_by_seconds()
        model_dict['log_file_path'] = model.log_file_path()
        model_dict['train_source_code_path'] = model.train_source_code_path()
        model_dict['train_notebook_uri'] = model.train_notebook_uri()

        return model_dict

    def train_process_terminated(self, model_name):
        with db.open_session() as s:
            # because of check database 1 seconds every time fix read is running but before handle_models finished.
            # 1. check status, only running can change to finished
            model = self.model_dao.find_by_name(s, model_name)
            if model.status == ModelStatusType.Running:
                _now = util.get_now_datetime()
                properties = {
                    "status": ModelStatusType.Failed,
                    "finish_datetime": _now,
                    "last_update_datetime": _now
                }
                self.model_dao.update_model_by_name(s, model_name, properties)
            else:
                log.warning(f"Train process is already finished, model = {model_name}")

    def add_train_process_step(self, train_job_name, req_dict):
        # [1]. read & check params
        step_type = util.require_in_dict(req_dict, 'type', str)
        step_status = util.require_in_dict(req_dict, 'status', str)
        step_extension = util.get_from_dict(req_dict, 'extension', dict)

        if step_status not in [JobStep.Status.Succeed, JobStep.Status.Failed]:
            raise ValueError(f"Unknown status = {step_status}")

        # [2]. save message
        with db.open_session() as s:

            # [2.1].  check temporary model exists
            model = self.model_dao.find_by_train_job_name(s, train_job_name)
            model_name = model.name

            def handle_step_failed():
                self._update_model(s, model_name, step_type,
                                   {"status": ModelStatusType.Failed, "finish_datetime": util.get_now_datetime()})

            # [2.2]. check event type, one type one record
            messages = s.query(MessageEntity).filter(MessageEntity.author == train_job_name).all()
            for m in messages:
                if step_type == util.loads(m.content).get('type'):
                    if step_type not in [TrainStep.Types.Optimize]:
                        raise Exception(f"Event type = {step_type} already exists .")

            # [2.3]. create a new message
            content = util.dumps(req_dict)
            message = MessageEntity(id=util.short_uuid(), author=train_job_name, content=content, create_datetime=util.get_now_datetime())
            s.add(message)

            # [2.4]. handle analyze event
            current_progress = model.progress
            # todo check in code body self._check_progress_change(step_type, current_progress)  # add failed status

            if step_type == TrainStep.Types.Load:
                if step_status == JobStep.Status.Succeed:
                    self._update_model(s, model_name, step_type, {"status": ModelStatusType.Running})
                else:
                    handle_step_failed()

            elif step_type == TrainStep.Types.Optimize:
                # Note: this step is always succeed
                train_trial_no = step_extension.get('trial_no')
                # load current trial and append new
                trials = model.trials
                if model.trials is None:
                    trials = []
                trials.append(step_extension)
                trial_status = step_extension['status']
                trial_extension = step_extension['extension']
                if trial_status == TrialStatus.Succeed:
                    self._update_model(s, model_name, step_type, {"train_trial_no": train_trial_no, "score": trial_extension.get('reward'), "trials": trials})
                elif trial_status in [TrialStatus.Failed, TrialStatus.Skip]:
                    # does not update score
                    self._update_model(s, model_name, step_type, {"train_trial_no": train_trial_no, "trials": trials})
                else:
                    raise ValueError(f"Unseen trial status {trial_status} .")

            elif step_type == TrainStep.Types.Searched:
                if step_status == JobStep.Status.Succeed:
                    self._update_model(s, model_name, step_type, {})
                else:
                    handle_step_failed()

            elif step_type == TrainStep.Types.Evaluate:
                if step_status == JobStep.Status.Succeed:
                    self._update_model(s, model_name, step_type, {"performance": step_extension['performance']})
                else:
                    handle_step_failed()

            elif step_type == TrainStep.Types.Persist:
                if step_status == JobStep.Status.Succeed:
                    model_file_size = step_extension['model_file_size']
                    self._update_model(s, model_name, step_type, {"model_file_size": model_file_size,
                                                                  "status": ModelStatusType.Succeed,
                                                                  "finish_datetime": util.get_now_datetime()})
                else:
                    handle_step_failed()
            else:
                raise ValueError(f"Unseen step type {step_type} of model {model_name}")
