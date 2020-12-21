# -*- encoding: utf-8 -*-
from cooka.common import util
from cooka.test.test_dataset import TestDataset
from os import path as P
import time
import os
from cooka.common import consts


class TestModel(TestDataset):

    def train_model_and_evaluate(self, dataset_name, req_dict):
        os.environ["ASYNC_TEST_TIMEOUT"] = "10"
        portal = self.get_url("")
        consts.SERVER_PORTAL = portal

        # 1. create a train job
        self.assert_response_and_get(self.fetch(f'/api/dataset/{dataset_name}/feature-series/default/train-job', method="POST", body=util.dumps(req_dict), headers=self.DEFAULT_HEADER))

        # 2.  poll train status
        max_times = 30
        for i in range(max_times):
            time.sleep(1)
            resp_poll = self.assert_response_and_get(self.fetch(f'/api/dataset/{dataset_name}/feature-series/default/train-job', method="GET", headers=self.DEFAULT_HEADER))
            print("resp_poll")
            print(util.dumps(resp_poll))
            trainings = resp_poll['trainings']
            assert len(trainings) == 1
            experiment_dict = trainings[0]
            assert experiment_dict['no_experiment'] == 1

            models_dict_list = experiment_dict['models']
            assert len(models_dict_list) > 0
            model_dict = models_dict_list[0]

            assert 'name' in model_dict
            assert 'status' in model_dict
            assert 'escaped' in model_dict
            assert 'model_file_size' in model_dict
            assert 'log_file_path' in model_dict

            status = model_dict.get('status')
            model_name = model_dict.get('name')

            final_status = ["failed", "succeed"]
            if status in final_status:
                assert status == "succeed"
                return model_name

            if i == max_times - 1:
                raise Exception("Train timeout.")

    def test_multi_classification_model(self):
        # 1. create a dataset
        dataset_name = self.create_dataset_from_file('cooka/test/dataset/iris.csv')

        # 2. create a train job
        req_dict = \
            {
                "label_col": "Species",
                "pos_label": True,
                "train_mode": "minimal",
                "partition_strategy": "cross_validation",
                "holdout_percentage": 20,
                "cross_validation": {
                    "n_folds": 2
                },
                "datetime_series_col": None
            }
        model_name = self.train_model_and_evaluate(dataset_name, req_dict)
        print(model_name)

    def test_binary_classification_model(self):
        # 1. create a dataset
        dataset_name = self.create_dataset()

        # 2. create a train job
        req_dict = \
            {
                "label_col": "readmitted",
                "pos_label": True,
                "train_mode": "minimal",
                "partition_strategy": "cross_validation",
                "holdout_percentage": 20,
                "cross_validation": {
                    "n_folds": 2
                },
                "datetime_series_col": None
            }
        model_name = self.train_model_and_evaluate(dataset_name, req_dict)

        # 1. check model exists
        model_path = util.model_dir(dataset_name, model_name)
        assert P.exists(model_path)

        # 2. predict file
        req_dict = \
            {
                "upload_took": 10,  # 10 just for test
                "file_path": P.abspath('cooka/test/dataset/diabetes_10k_datetime.csv'),
                "reserved_cols": ['race'],
            }

        resp_batch_predict_job = self.assert_response_and_get(self.fetch(f'/api/dataset/{dataset_name}/feature-series/default/model/{model_name}/batch-predict-job', method="POST", body=util.dumps(req_dict), headers=self.DEFAULT_HEADER))
        assert 'batch_predict_job_name' in resp_batch_predict_job
        batch_predict_job_name = resp_batch_predict_job.get('batch_predict_job_name')

        # 3. poll batch job status
        max_poll_times = 31  # try 30 times
        for i in range(max_poll_times):
            time.sleep(1)
            resp_poll_batch_predict_job = self.assert_response_and_get(self.fetch(f'/api/dataset/{dataset_name}/feature-series/default/model/{model_name}/batch-predict-job/{batch_predict_job_name}', method="GET",headers=self.DEFAULT_HEADER))

            # stop
            if i == max_poll_times - 1:
                raise Exception(util.dumps(resp_poll_batch_predict_job))

            assert "batch_predict_job_name" in resp_poll_batch_predict_job
            assert "steps" in resp_poll_batch_predict_job

            print(resp_poll_batch_predict_job)

            batch_predict_steps = resp_poll_batch_predict_job.get('steps')
            if self.check_batch_predict_steps_finished(batch_predict_steps):
                break

        # 4. check model path correct
        resp_model = self.assert_response_and_get(self.fetch(f'/api/dataset/{dataset_name}/feature-series/default/model/{model_name}', method="GET", headers=self.DEFAULT_HEADER))

        # 5. check response
        assert "name" in resp_model
        assert "status" in resp_model
        assert "escaped" in resp_model
        assert "model_file_size" in resp_model
        assert "task_type" in resp_model
        assert "framework" in resp_model
        assert "create_datetime" in resp_model
        assert "last_update_datetime" in resp_model
        assert "log_file_path" in resp_model
        assert "performance" in resp_model
        # todo assert "trails" in resp_model

        performance = resp_model.get('performance')

        assert "metrics" in performance
        assert "confusion_matrix" in performance
        # todo assert "roc_curve" in performance

        metrics = performance.get('metrics')
        assert 'roc_auc' in metrics
        # todo assert 'f1' in metrics

        confusion_matrix = performance.get('confusion_matrix')
        assert "fn" in confusion_matrix
        assert "fp" in confusion_matrix
        assert "tn" in confusion_matrix
        assert "tp" in confusion_matrix

        assert "label" in confusion_matrix
        label_dict = confusion_matrix.get('label')

        # todo assert True in label_dict
        # todo assert False in label_dict

        # todo trails
        # trails = resp_model.get('trails')

        # assert len(trails) > 0
        # trail_dict = trails[0]

        # assert 'params' in trail_dict
        # trail_params_dict = trail_dict.get('params')
        # assert list(trail_params_dict.keys) > 0

        # assert 'metrics' in trail_dict
        # trail_metrics = trail_dict.get('metrics')
        # assert list(trail_metrics.keys) > 0



    def check_batch_predict_steps_finished(self, batch_predict_steps):
        for step in batch_predict_steps:
            if 'write_result' == step['type'] and 'succeed' == step['status']:
                assert 'extension' in step
                assert 'output_path' in step['extension']

                output_path = step['extension']['output_path']
                abs_output_path = P.join(consts.DATA_DIR, output_path)
                assert P.exists(abs_output_path)
                return True
        return False
