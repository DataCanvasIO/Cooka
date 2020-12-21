# -*- encoding: utf-8 -*-

from os import path as P
from cooka.common import util
from cooka.common import consts
from cooka.common.model import Feature, FeatureType
from cooka.test.base_test_case import BaseTestCase, WithTemporaryDatasetTestCase


class TestDataset(WithTemporaryDatasetTestCase):

    def create_dataset(self):
        # 1. create temporary dataset
        temporary_dataset_name = self.create_temporary_dataset()

        # 2. create dataset and validate
        dataset_name = f"diabetes_{util.short_uuid()}"
        body = \
            {
                "dataset_name": dataset_name,
                "temporary_dataset_name": temporary_dataset_name
            }

        create_response = self.fetch('/api/dataset', method="POST", body=util.dumps(body), headers=self.DEFAULT_HEADER)
        self.assert_response_and_get(create_response)
        return dataset_name

    # support create dataset by file path
    def create_dataset_from_file(self, file_path):
        # 1. create temporary dataset
        temporary_dataset_name = self.create_temporary_dataset_from_file(file_path)

        # 2. create dataset and validate
        body = \
            {
                "dataset_name": temporary_dataset_name,
                "temporary_dataset_name": temporary_dataset_name
            }

        create_response = self.fetch('/api/dataset', method="POST", body=util.dumps(body), headers=self.DEFAULT_HEADER)
        self.assert_response_and_get(create_response)
        return temporary_dataset_name

    def test_create_and_delete_dataset(self):
        portal = self.get_url("")
        consts.SERVER_PORTAL = portal

        dataset_name = self.create_dataset()
        dataset_path = P.join(consts.PATH_DATASET, dataset_name)

        assert P.exists(P.join(dataset_path, 'data.csv'))
        # assert P.exists(P.join(dataset_path, 'meta.json'))

        # 3. retrieve dataset todo use bean not json
        retrieve_response = self.fetch(f'/api/dataset/{dataset_name}', method="GET", headers=self.DEFAULT_HEADER)

        dict_retrieve_response = self.assert_response_and_get(retrieve_response)

        assert dataset_name == dict_retrieve_response.get('name')
        assert dict_retrieve_response.get('file_size')
        assert dict_retrieve_response.get('n_rows') == 10000
        assert dict_retrieve_response.get('n_cols') == 52
        assert len(dict_retrieve_response.get('features')) == 52

        features_list_dict = dict_retrieve_response.get('features')

        for f in features_list_dict:
            feature_extension = f['extension']
            if f['name'] == 'datetime':
                assert f['type'] == FeatureType.Datetime
                assert 'by_year' in feature_extension
                assert len(feature_extension.get('by_month')) == 12
                assert len(feature_extension.get('by_week')) == 7
                assert len(feature_extension.get('by_hour')) == 24

            elif f['name'] == 'gender':
                assert "mode" in feature_extension
                assert "value_count" in feature_extension
                assert f['type'] == FeatureType.Categorical

            elif f['name'] == 'num_medications':
                assert f['type'] == FeatureType.Continuous
                assert "bins" in feature_extension
                assert "min" in feature_extension
                assert "max" in feature_extension
                assert "mean" in feature_extension
                assert "stddev" in feature_extension
                assert "median" in feature_extension

        feature_summary = dict_retrieve_response.get('feature_summary')
        assert feature_summary.get('categorical') == 43
        assert feature_summary.get('continuous') == 8
        assert feature_summary.get('text') == 0
        assert feature_summary.get('datetime') == 1

        # 4. preview data
        self.asset_preview_data(dataset_name)

        # 5. show dataset list
        dataset_list_resp = self.assert_response_and_get(self.fetch(f'/api/dataset', method="GET", headers=self.DEFAULT_HEADER))["datasets"]
        assert len(dataset_list_resp) > 0
        dataset_brevity_dict = dataset_list_resp[0]
        assert "name" in dataset_brevity_dict
        assert "status" in dataset_brevity_dict
        assert "file_size" in dataset_brevity_dict
        assert "n_rows" in dataset_brevity_dict
        assert "n_cols" in dataset_brevity_dict
        assert "hints" in dataset_brevity_dict
        assert "is_temporary" in dataset_brevity_dict
        assert "source_type" in dataset_brevity_dict
        assert "file_path" in dataset_brevity_dict
        assert "file_name" in dataset_brevity_dict
        assert "create_datetime" in dataset_brevity_dict
        assert "last_update_datetime" in dataset_brevity_dict
        assert "n_experiments" in dataset_brevity_dict

        # 6. delete it
        self.assert_response_and_get(self.fetch(f'/api/dataset/{dataset_name}', method="DELETE", headers=self.DEFAULT_HEADER))
        # retrieve detail should not exist

        # response is not 0
        # self.assert_response_and_get(self.fetch(f'/api/dataset/{dataset_name}', method="DELETE", headers=self.DEFAULT_HEADER))

        # data dir should not exists
        assert not P.exists(P.join(consts.PATH_DATASET, dataset_name))

    def asset_preview_data(self, dataset_name):
        preview_uri = f'/api/dataset/{dataset_name}/preview?page_size=20'
        response = self.fetch(preview_uri, method="GET", headers=self.DEFAULT_HEADER)
        response_dict = self.assert_response_and_get(response)
        assert len(response_dict['rows']) == 20
        assert len(response_dict['headers']) == 52
        assert response_dict['count'] > 0

    def test_recommend_train_conf(self):
        dataset_name = self.create_dataset_from_file("cooka/test/dataset/Bank_Marketing_Data/train.csv")

        recommend_conf = self.assert_response_and_get(self.fetch(f'/api/dataset/{dataset_name}/feature-series/default/recommend-train-conf', method="GET", headers=self.DEFAULT_HEADER)).get("conf")

        assert recommend_conf['label_col'] == "y"
        assert recommend_conf['pos_label'] == "yes"
        assert recommend_conf['train_mode'] == "quick"
        assert recommend_conf['partition_strategy'] == "train_validation_holdout"
        train_validation_holdout = recommend_conf.get('train_validation_holdout')

        assert train_validation_holdout['train_percentage'] == 80
        assert train_validation_holdout['validation_percentage'] == 10
        assert train_validation_holdout['holdout_percentage'] == 10
