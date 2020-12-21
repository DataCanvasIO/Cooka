# -*- encoding: utf-8 -*-

from hypernets.searchers.random_searcher import RandomSearcher
from hypernets.core.callbacks import *
from hypernets.core.searcher import OptimizeDirection

from sklearn.model_selection import train_test_split
import tempfile
from os import path as P

from hypergbm.hyper_gbm import HyperGBM
from hypergbm.pipeline import DataFrameMapper
from hypergbm.sklearn.sklearn_ops import numeric_pipeline_complex, categorical_pipeline_simple
from hypernets.core.callbacks import *
from hypernets.core.ops import ModuleChoice, HyperInput
from hypernets.core.search_space import Choice
from hypernets.core.search_space import HyperSpace
from hypernets.core.searcher import OptimizeDirection
from hypernets.searchers.random_searcher import RandomSearcher
from hypergbm.search_space import search_space_general
import pandas as pd
import unittest


class TestHypernet(unittest.TestCase):

    def test_hypergbm_bankdata(self):
        rs = RandomSearcher(search_space_general, optimize_direction=OptimizeDirection.Maximize)
        hk = HyperGBM(rs, task='classification', reward_metric='accuracy',
                      callbacks=[SummaryCallback(), FileLoggingCallback(rs)])

        df = pd.read_csv('cooka/test/dataset/Bank_Marketing_Data/train.csv')

        df.drop(['id'], axis=1, inplace=True)
        X_train, X_test = train_test_split(df.head(1000), test_size=0.2, random_state=42)
        y_train = X_train.pop('y')
        y_test = X_test.pop('y')

        X_train_origin = X_train.copy()

        hk.search(X_train, y_train, X_test, y_test, max_trails=1)
        assert hk.best_model
        best_trial = hk.get_best_trail()

        estimator = hk.final_train(best_trial.space_sample, X_train, y_train)

        result = estimator.evaluate(X_test, y_test)
        print(result)

        predict_result = estimator.predict(X_train_origin)
        print(predict_result)

    def test_hypergbm_diabetes(self):
        rs = RandomSearcher(search_space_general, optimize_direction=OptimizeDirection.Maximize)
        hk = HyperGBM(rs, task='classification', reward_metric='accuracy',
                      callbacks=[SummaryCallback(), FileLoggingCallback(rs)])

        df = pd.read_csv('cooka/test/dataset/diabetes_10k.csv')

        X_train, X_test = train_test_split(df.head(1000), test_size=0.2, random_state=42)
        y_train = X_train.pop('readmitted')
        y_test = X_test.pop('readmitted')

        X_train_origin = X_train.copy()

        hk.search(X_train, y_train, X_test, y_test, max_trails=2)
        assert hk.best_model
        best_trial = hk.get_best_trail()

        estimator = hk.final_train(best_trial.space_sample, X_train, y_train)

        # result = estimator.evaluate(X_test, y_test)
        # print(result)

        series_gender = X_train_origin.pop('gender')
        X_train_origin['gender'] = series_gender

        predict_result = estimator.predict(X_train_origin)
        print(predict_result)


if __name__ == '__main__':
    unittest.main()