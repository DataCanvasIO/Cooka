# DataFrames
import os

import pandas as pd
import numpy as np
from cooka.common import consts
from cooka.common.model import Feature, FeatureTypeStats, DatasetStats, ContinuousFeatureBin, \
    ContinuousFeatureExtension, FeatureValueCount, \
    CategoricalFeatureExtension, DatetimeFeatureExtension, YearValueCount, FeatureType, FeatureMode, SampleConf, \
    FeatureUnique, FeatureMissing


class Analyzer(object):
    pass


class PandasAnalyzer(Analyzer):

    @staticmethod
    def get_analyze_df(file_path, sample_chunksize, header):
        # infer
        if sample_chunksize > -1:
            df_iterator = pd.read_csv(file_path, chunksize=sample_chunksize, header=header, infer_datetime_format=True)
            return df_iterator.get_chunk()  # use first chunk
        else:
            # use whole data
            return pd.read_csv(file_path, header=header, infer_datetime_format=True)

    def __init__(self, file_path: str, label_col: str, sample_conf: SampleConf):
        import time
        # 1. check params
        if not os.path.exists(file_path):
            raise FileExistsError("File not found: %s" % file_path)
        self.file_path = file_path
        self.sample_conf = sample_conf
        self.label_col = label_col

        # 2. check headers
        is_has_header = self.is_csv_file_has_header(file_path)
        self.is_has_header = is_has_header

        # 3. calc sample chunk size
        self.n_rows = self._count_lines(file_path, is_has_header)
        if sample_conf.sample_strategy == SampleConf.Strategy.RandomRows:
            sample_chunksize = sample_conf.n_rows

        elif sample_conf.sample_strategy == SampleConf.Strategy.Percentage:
            sample_chunksize = round(self.n_rows * sample_conf.percentage / 100)

        elif sample_conf.sample_strategy == SampleConf.Strategy.WholeData:
            sample_chunksize = -1

        else:
            raise ValueError(f"Unsupported sample strategy = {sample_conf.sample_strategy}")

        # 4. read data
        if not is_has_header:
            # 4.1. update columns
            self.df = self.get_analyze_df(file_path, sample_chunksize, None)
            self.df.columns = ["c%s" % c for c in self.df.columns]  # generate name for df
        else:
            self.df = self.get_analyze_df(file_path, sample_chunksize, 'infer')

        self.n_cols = self.df.shape[1]  # read file columns

        if self.sample_conf.sample_strategy == SampleConf.Strategy.WholeData:
            self.n_rows_used = self.n_rows
        else:
            self.n_rows_used = sample_chunksize

        # 3. to fix date types
        categorical_cols = self.get_categorical_cols(self.df)
        for c in categorical_cols:
            self.df[c] = self.parse_date(self.df[c])

    @staticmethod
    def get_categorical_cols(df: pd.DataFrame):
        c_list = []
        for k, v in df.dtypes.items():
            if 'object' in v.name:
                c_list.append(k)
        return c_list



    @staticmethod
    def is_csv_file_has_header(path):
        df_no_header: pd.DataFrame = next(pd.read_csv(path, chunksize=100, header=None))
        for col in df_no_header.dtypes.to_dict():
            type_name = df_no_header.dtypes[col].name
            # only this case
            if 'float' in type_name or 'int' in type_name or 'datetime' in type_name or 'timestamp' in type_name:
                return False
        return True

    @staticmethod
    def parse_date(series: pd.Series):
        format = "%Y-%m-%d %H:%M:%S"  # Now only support one format
        # 1. take top 100 non-empty values
        INFER_TOP_N = 100
        series_non_empty = series.dropna()[: INFER_TOP_N]

        # 2. if these value all datetime value infer it as datetime nor object
        for item in series_non_empty:
            try:
                if isinstance(item, str):
                    pd.datetime.strptime(item, format)
                else:
                    return series
            except Exception as e:
                return series

        # 3. infer as datetime
        return pd.to_datetime(series, format=format)

    def _count_lines(self, path, is_has_header):
        count = 0
        with open(path, 'r') as f:
            for _ in f.readlines():
                count = count + 1
        if count > 0:
            if is_has_header is True:
                return count - 1  # remove header
            else:
                return count
        else:
            return 0

    @staticmethod
    def analyze_continuous(series, missing):

        n_rows = series.shape[0]
        # 1. all data is missing
        if n_rows == missing:
            return \
                ContinuousFeatureExtension(bins=[ContinuousFeatureBin(begin=0, end=0, value=10)],
                                           min=None,
                                           max=None,
                                           mean=None,
                                           stddev=None,
                                           median=None,
                                           value_count=[FeatureValueCount(type='NaN', value=n_rows)])

        # 2. split to 10 bins
        # duplicates='drop': may not up to 10 bins
        bins = [ContinuousFeatureBin(begin=k.left, end=k.right, value=v) for k, v in
                pd.value_counts(pd.cut(series, 10, duplicates='drop')).items()]

        # 3. describe
        series_d = series.describe()
        feature_value_count = pd.value_counts(series)

        # feature_value_count, 按个数进行统计
        feature_value_count_sorted = feature_value_count.sort_values(ascending=False)

        if feature_value_count_sorted.shape[0] > consts.MAX_DISTINCT_VALUES:
            feature_value_count_limited = feature_value_count_sorted.iloc[:consts.MAX_DISTINCT_VALUES]
            others_feature_values_sum = feature_value_count_sorted.iloc[consts.MAX_DISTINCT_VALUES:].sum()
            value_count = [FeatureValueCount(type=k, value=int(v)) for k, v in
                           feature_value_count_limited.items()]

            remained_feature_count = FeatureValueCount(type=consts.KEY_REMAINED_FEATURE_VALUES_SUM,
                                                       value=int(others_feature_values_sum))
            value_count.append(remained_feature_count)
        else:
            value_count = [FeatureValueCount(type=k, value=int(v)) for k, v in feature_value_count_sorted.items()]

        extension = \
            ContinuousFeatureExtension(bins=bins,
                                       min=series_d['min'],
                                       max=series_d['max'],
                                       mean=series_d['mean'],
                                       stddev=series_d['std'],
                                       median=series_d['50%'],
                                       value_count=value_count)

        return extension

    @staticmethod
    def analyze_categorical(series, missing):

        n_rows = series.shape[0]
        # 1. all data is missing
        if n_rows == missing:
            return CategoricalFeatureExtension(value_count=[FeatureValueCount(type='NaN', value=n_rows)],
                                               mode=FeatureMode(value='NaN', count=n_rows, percentage=100))

        # 2. describe
        series_d = series.describe()

        feature_value_count = pd.value_counts(series)
        mode_value = series_d['top']
        mode_count = int(feature_value_count[mode_value])
        mode = FeatureMode(value=str(mode_value), count=mode_count,
                           percentage=round(mode_count / n_rows * 100, 2))  # todo add unit test

        # limit value count
        feature_value_count_limited = feature_value_count.sort_values(ascending=False).iloc[:consts.MAX_DISTINCT_VALUES]

        value_count = [FeatureValueCount(type=str(k), value=int(v)) for k, v in feature_value_count_limited.items()]
        extension = \
            CategoricalFeatureExtension(value_count=value_count, mode=mode)
        return extension

    @staticmethod
    def analyze_datetime(series, missing):
        n_rows = series.shape[0]
        if n_rows == missing:
            return DatetimeFeatureExtension(by_year=list(range(12)),
                                            by_month=list(range(12)),
                                            by_day=list(range(31)),
                                            by_week=list(range(7)),
                                            by_hour=list(range(24)))
        def to_int(v):
            try:
                return int(v)
            except Exception:
                return v

        by_year_dict = series.map(lambda _: to_int(_.year)).value_counts()
        by_month_dict = series.map(lambda _: to_int(_.month)).value_counts()
        by_day_dict = series.map(lambda _: to_int(_.day)).value_counts()
        by_week_dict = series.map(lambda _: to_int(_.dayofweek)).value_counts()  # +1
        by_hour_dict = series.map(lambda _: to_int(_.hour)).value_counts()

        by_year = [YearValueCount(year=int(year), value=count) for year, count in by_year_dict.items()]
        by_month = [int(by_month_dict.get(float(i), 0)) for i in range(12)]
        by_day = [int(by_day_dict.get(float(i), 0)) for i in range(31)]
        by_week = [int(by_week_dict.get(float(i), 0)) for i in range(7)]
        by_hour = [int(by_hour_dict.get(float(i), 0)) for i in range(24)]

        extension = \
            DatetimeFeatureExtension(by_year=by_year, by_month=by_month,
                                     by_day=by_day, by_week=by_week, by_hour=by_hour)
        return extension

    def analyze_col(self, col_name, missing_count):
        """
        Supported case:
            1. categorical/continuous all value is missing
            2. categorical not reach to 10
        """
        series = self.df[col_name]

        unique_value = int(self.df[col_name].value_counts().count())
        type_name = self.df.dtypes[col_name].name

        feature_type = self.infer_feature_type(type_name)
        extension = None
        if feature_type == FeatureType.Continuous:
            extension = self.analyze_continuous(series, missing_count)
        elif feature_type == FeatureType.Categorical:
            extension = self.analyze_categorical(series, missing_count)
        elif feature_type == FeatureType.Datetime:
            extension = self.analyze_datetime(series, missing_count)
        else:
            extension = None

        if extension is not None:
            extension = extension.to_dict()
        n_rows = series.shape[0]

        unique_percentage = unique_value / n_rows * 100
        feature_unique = FeatureUnique(value=unique_value,
                                       percentage=unique_percentage,
                                       status=FeatureUnique.calc_status(unique_value, unique_percentage))
        missing_percentage = missing_count / n_rows * 100
        feature_missing = FeatureMissing(value=missing_count,
                                         percentage=missing_percentage,
                                         status=FeatureMissing.calc_status(missing_percentage))

        # feature_correlation = FeatureCorrelation(value=unique_value, percentage=unique_value/, status=) 相关性在分析那里

        return Feature(name=col_name,
                       type=feature_type,
                       data_type=series.dtype.name,
                       missing=feature_missing,
                       unique=feature_unique,
                       extension=extension)

    def do_analyze_csv(self) -> DatasetStats:
        df: pd.DataFrame = self.df

        # 1. replace Infinity to NaN, the error is:
        # ValueError: cannot specify integer `bins` when input data contains infinity
        df.replace([np.Infinity, -np.Infinity], np.nan, inplace=True)

        # 2. calc missing
        missing_dict = df.isnull().sum()

        # 3. analyze cols
        features = [self.analyze_col(col_name, int(missing_dict[col_name])) for col_name in df.columns]
        feature_type_dict = pd.Series(data=[f.type for f in features], name='feature_type').value_counts().to_dict()
        fts = FeatureTypeStats(**feature_type_dict)

        return DatasetStats(has_header=self.is_has_header,
                            n_rows=self.n_rows, n_cols=len(df.columns),
                            features=features, feature_summary=fts)

        # df['SepalLengthCm'].value_counts().compute()

        # X1.corr(Y1, method="pearson")

    def infer_feature_type(self, type_name):
        if 'float' in type_name or 'int' in type_name:
            return FeatureType.Continuous
        elif 'datetime' in type_name:
            return FeatureType.Datetime
        else:
            # todo CategoricalInt
            # todo infer text
            return FeatureType.Categorical
