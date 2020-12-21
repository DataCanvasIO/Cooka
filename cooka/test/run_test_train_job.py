# -*- encoding: utf-8 -*-
from cooka.core.analyzer import PandasAnalyzer
from cooka.common.model import TrainJobConf, FrameworkType, ExperimentConf, TrainValidationHoldout
from cooka.common.model import TaskType, SampleConf
from hypernets.core.searcher import OptimizeDirection


class TestTrainJob:

    def _make_train_job_conf(self, framework):
        return TrainJobConf(framework=framework, job_name="job", max_trails=1, searcher=TrainJobConf.Searcher.MCTSSearcher, search_space=TrainJobConf.SearchSpace.Minimal)

    def test_binary_dataset(self, framework):
        experiment_conf = \
            ExperimentConf(name="1",
                           label_col='y',
                           pos_label='yes',
                           task_type=TaskType.BinaryClassification,
                           partition_strategy=ExperimentConf.PartitionStrategy.TrainValidationHoldout,
                           train_validation_holdout=TrainValidationHoldout(train_percentage=80, validation_percentage=10,  holdout_percentage=10),
                           datetime_series_col=None,
                           file_path='cooka/test/dataset/Bank_Marketing_Data/train.csv',
                           test_file_path="cooka/test/dataset/Bank_Marketing_Data/test.csv")

        train_job_conf = self._make_train_job_conf(framework)

        data_stats = PandasAnalyzer(experiment_conf.file_path, None).do_analyze_csv()
        trainer = make_trainer(data_stats, train_job_conf, experiment_conf)

        assert trainer.get_optimize_metric().lower() == "auc"
        assert trainer.get_direction() == OptimizeDirection.Maximize

        trainer.train()

    def test_multi_class_dataset(self, framework):
        experiment_conf = \
            ExperimentConf(name="1",
                           label_col='team',
                           task_type=TaskType.MultiClassification,
                           partition_strategy=ExperimentConf.PartitionStrategy.TrainValidationHoldout,
                           train_validation_holdout=TrainValidationHoldout(train_percentage=80, validation_percentage=10,  holdout_percentage=10),
                           datetime_series_col=None,
                           file_path='cooka/test/dataset/Players/train.csv',
                           test_file_path="cooka/test/dataset/Players/test.csv")

        train_job_conf = self._make_train_job_conf(framework)

        data_stats = PandasAnalyzer(experiment_conf.file_path, None).do_analyze_csv()
        trainer = make_trainer(data_stats, train_job_conf, experiment_conf)

        if framework == FrameworkType.DeepTables:
            assert trainer.get_direction() == OptimizeDirection.Maximize
            assert trainer.get_optimize_metric().lower() == "accuracy"
        elif framework == FrameworkType.GBM:
            assert trainer.get_direction() == OptimizeDirection.Minimize
            assert trainer.get_optimize_metric().lower() == "logloss"

        trainer.train()

    def test_regression_dataset(self, framework):
        experiment_conf = \
            ExperimentConf(name="1",
                           label_col='SalePrice',
                           task_type=TaskType.Regression,
                           partition_strategy=ExperimentConf.PartitionStrategy.TrainValidationHoldout,
                           train_validation_holdout=TrainValidationHoldout(train_percentage=80, validation_percentage=10,  holdout_percentage=10),
                           datetime_series_col=None,
                           file_path='cooka/test/dataset/House_Prices/train.csv',
                           test_file_path='cooka/test/dataset/House_Prices/test.csv')

        train_job_conf = self._make_train_job_conf(framework)

        data_stats = PandasAnalyzer(experiment_conf.file_path, None).do_analyze_csv()
        trainer = make_trainer(data_stats, train_job_conf, experiment_conf)

        assert trainer.get_direction() == OptimizeDirection.Minimize

        if framework == FrameworkType.DeepTables:
            assert trainer.get_optimize_metric().lower() == "rootmeansquarederror"
        elif framework == FrameworkType.GBM:
            assert trainer.get_optimize_metric().lower() == "rmse"

        trainer.train()
