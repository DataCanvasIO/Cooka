# -*- encoding: utf-8 -*-
from cooka.core.analyzer import PandasAnalyzer
from cooka.common.model import AnalyzeJobConf, SampleConf
import unittest


class TestAnalyzer(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
       cls.data_path = "cooka/test/dataset/diabetes_10k_datetime.csv"

    def test_sample_random_rows_analyzer(self):
        sample_conf = SampleConf(sample_strategy=SampleConf.Strategy.RandomRows, percentage=None, n_rows=200)
        analyzer = PandasAnalyzer(self.data_path, None, sample_conf)
        s = analyzer.do_analyze_csv()
        print(s)

    def test_sample_percentage_analyzer(self):
        sample_conf = SampleConf(sample_strategy=SampleConf.Strategy.Percentage, percentage=50)
        analyzer = PandasAnalyzer(self.data_path, None, sample_conf)
        s = analyzer.do_analyze_csv()
        print(s)

    def test_analyze_job(self):
        d = \
            {
                "job_name": "job_analyze_iris_20200807_142711_372762",
                "dataset_name": "temporary_dataset_iris_20200807_142711_372761",
                "sample_conf": {
                    "sample_strategy": None,
                    "percentage": None,
                    "n_rows": None
                },
                "path": "/Users/wuhf/.cooka/tmp/upload/dRJ9lzjB.csv",
                "temporary_dataset": None,
                "server_portal": "http://localhost:8000",
                "label_col": None
            }
        conf = \
            AnalyzeJobConf.load_dict(d)
        # from multiprocessing import Queue
        # q = Queue()
        # import multiprocessing
        # p = multiprocessing.Process(target=run, args=(conf, q, ))
        # p.start()
        #
        # import time
        # time.sleep(10)
        #
        # print(p.is_alive())
        # for i in range(3):
        #     print(q.get().to_dict())
