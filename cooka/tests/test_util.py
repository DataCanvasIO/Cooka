# -*- encoding: utf-8 -*-
from cooka.common import util
import tempfile
from os import path as P


class TestFileUtil:

    def setup_class(self):
        self.path = P.join(tempfile.gettempdir(), util.short_uuid())

        with open(self.path, 'w') as f:
            f.write("abc")

    def test_tail(self):
        s = list(util.tail(self.path, n=1))
        assert len(s) == 1
        assert s[0] == 'c'

    def test_tail_exceed(self):
        s = list(util.tail(self.path, n=4))
        assert len(s) == 3

    # def test_debug(self):
    #     p = '/Users/wuhf/.cooka/tmp/log/analyze_data_job_0QHhSXzm.log'
    #     s = list(util.tail(p, n=1))
    #     print(s)


class TestDatasetUtil:

    def setup_class(self):
        self.path = P.join(tempfile.gettempdir(), util.short_uuid())

        with open(self.path, 'w') as f:
            f.write("abc")

    def test_make_dataset_name(self):
        name1 = "iris-1*2(data.csv"
        assert util.make_dataset_name(name1) == "iris-1_2_data_csv"


def test_human_date():
    print(util.human_datetime(util.get_now_datetime()))
