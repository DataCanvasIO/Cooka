# -*- encoding: utf-8 -*-
# import os
#
# from cooka.common import util
# from cooka.common.serializer import ListBeanField, Bean
# from cooka import settings
# import pandas as pd
# from cooka.common.log import log_core as logger
# from cooka.common.model import Feature, FeatureTypeStats, DatasetStats, ContinuousFeatureBin, ContinuousFeatureExtension, CategoricalFeatureValueCount, \
#     CategoricalFeatureExtension, DatetimeFeatureExtension, YearValueCount, FeatureType, FeatureMode
# from sklearn.compose import make_column_selector
#

# class DaskAnalyzer(Analyzer):
#
#     def __init__(self, path, label_col):
#
#         if not os.path.exists(path):
#             raise FileExistsError("File not found: %s" % path)
#
#         self.file_path = path
#         self.df = dd.read_csv(path, blocksize=consts.DASK_BLOCK_SIZE * 1024 * 1024)[:1000]  # break text into 64MB chunks todo 1000 for dev
#         self.file_size = os.path.getsize(path)
#         self.label_col = label_col
#
#     def analyze_col(self, col_name, missing):
#         # attrs = ('name', 'type', 'missing', 'unique', 'relevance')
#         # self.df[col_name]
#         unique = int(self.df[col_name].value_counts().count().compute())
#         type_name = self.df.dtypes[col_name].name
#
#         # del missing label
#         # label encoder label
#         # calc relevance
#         # not for text
#         relevance = 0.1 # todo self.df[col_name].corr(other=self.df[self.label_col], method="pearson").compute()
#
#         return Feature(name=col_name,
#                 type=self.infer_feature_type(type_name),
#                 missing=missing,
#                 unique=unique,
#                 relevance=relevance)
#
#     def do_analyze_csv(self):
#         df = self.df
#         shape_row = df.shape[0]
#         if isinstance(shape_row, int):
#             n_rows = shape_row
#         else:
#             n_rows = shape_row.compute()
#
#
#         n_cols = len(df.columns)
#         logger.info(f"Dataset shape is {n_rows}, {n_cols}")
#         missing_dict = df.isnull().sum().compute()
#
#         features = [self.analyze_col(col_name, int(missing_dict[col_name]), ) for col_name in df.columns]
#
#         feature_type_dict = pd.Series(data=[f.type for f in features], name='feature_type').value_counts().to_dict()
#         fts = FeatureTypeStats(**feature_type_dict)
#
#         return DatasetStats(n_rows=n_rows, n_cols=n_cols, size=util.human_data_size(self.file_size), features=features, feature_summary=fts)
#
#         # df['SepalLengthCm'].value_counts().compute()
#
#         # X1.corr(Y1, method="pearson")
#
#     def infer_feature_type(self, type_name):
#         if 'float' in type_name or 'int' in type_name:
#             return FeatureType.Continuous
#         elif 'datetime' in type_name :
#             return FeatureType.Datetime
#         else:
#             # todo CategoricalInt
#             # todo infer text
#             return FeatureType.Categorical
#
# r = DaskAnalyzer('/Users/wuhf/Documents/datasets/iris_Missing.csv', 'Species').do_analyze_csv()
# dr = DatasetStatsSerializer(r)
# print(json_util.dumps(dr.data))