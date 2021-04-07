# -*- encoding: utf-8 -*-
from cooka.common.serializer import Bean, ListBeanField, StringField, BeanField, IntegerField, FloatField, DictField, ListObjectField, ObjectField
from cooka.common.serializer import BooleanField, DatetimeField
from os import path as P
from cooka.common import util


STATUS_FEATURE_NORMAL = 'normal'

STATUS_SUCCEED = "succeed"
STATUS_FAILED = "failed"


class FeatureUnique(Bean):
    value = IntegerField()
    percentage = FloatField()
    status = StringField()

    class Status:
        ID_ness = 'ID-ness'
        Stable = 'stable'

    @staticmethod
    def calc_status(n_uniques, percentage):
        if n_uniques == 1:
            return FeatureUnique.Status.Stable
        else:
            if percentage > 90:
                return FeatureUnique.Status.ID_ness
            else:
                return STATUS_FEATURE_NORMAL


class FeatureMissing(Bean):
    value = IntegerField()
    percentage = FloatField()
    status = StringField()

    class Status:
        TooHigh = 'too_high'

    @staticmethod
    def calc_status(percentage):
        if percentage > 70:
            return FeatureMissing.Status.TooHigh
        else:
            return STATUS_FEATURE_NORMAL


class FeatureCorrelation(Bean):
    value = FloatField()
    status = StringField()

    class Status:
        TooHigh = 'too_high'
        TooLow = 'too_low'

    @staticmethod
    def calc_status(correlation, is_target_col):
        if correlation is None:
            return STATUS_FEATURE_NORMAL
        else:
            _c = abs(correlation)
            if _c > 0.5:
                if is_target_col is True:
                    return STATUS_FEATURE_NORMAL
                else:
                    return FeatureCorrelation.Status.TooHigh
            elif _c < 0.01:
                return FeatureCorrelation.Status.TooLow
            else:
                return STATUS_FEATURE_NORMAL


class Feature(Bean):
    name = StringField()
    type = StringField()
    data_type = StringField()
    correlation = BeanField(bean_cls=FeatureCorrelation)
    missing = BeanField(bean_cls=FeatureMissing)
    unique = BeanField(bean_cls=FeatureUnique)
    extension = DictField()


class SampleConf(Bean):
    sample_strategy = StringField()
    percentage = IntegerField()
    n_rows = IntegerField()

    class Strategy:
        RandomRows = "random_rows"
        Percentage = "percentage"
        WholeData = "whole_data"


class AnalyzeJobConf(Bean):

    job_name = StringField()
    dataset_name = StringField()
    sample_conf = BeanField(SampleConf)
    path = StringField()
    temporary_dataset = BooleanField()
    label_col = StringField()


class JobStep(Bean):
    type = StringField()
    status = StringField()
    took = FloatField()
    datetime = IntegerField()
    extension = DictField()

    class Status:
        Succeed = "succeed"
        Failed = "failed"


class AnalyzeStep(JobStep):

    class Types:
        Upload = 'upload'
        Copy = 'copy'
        Load = 'load'
        Analyzed = 'analyzed'
        PatchCorrelation = 'patch_correlation'
        End = 'end'


class PredictStepType(object):
    Upload = 'upload'
    Load = 'load'
    LoadModel = 'load_model'
    CheckDataType = 'check_data_type'
    Evaluate = 'evaluate'
    WriteResult = 'write_result'
    End = 'end'


class FrameworkType:
    Keras = 'Keras'
    GBM = 'HyperGBM'
    DeepTables = "DeepTables"


class TrainJobConf(Bean):
    framework = StringField()
    name = StringField()
    model_name = StringField()
    searcher = StringField()
    max_trials = IntegerField()
    search_space = StringField()

    class SearchSpace:
        Complex = "complex"
        Basic = "basic"
        Minimal = "minimal"

    class Searcher:
        RandomSearcher = 'random_searcher'
        EvolutionSearcher = 'evolution_searcher'
        MCTSSearcher = 'MCTS_searcher'
        EnasSearcher = 'Enas_searcher'


class TrainStep(JobStep):
    class Types:
        """
        Begin -> Load -> Optimize -> Searched -> FinalTrain -> Evaluate -> Persist -> End
        One state can only go to next state or end
        """
        Load = 'load'
        Optimize = 'optimize'
        Searched = 'searched'
        FinalTrain = 'final_train'
        Evaluate = 'evaluate'
        Persist = 'persist'


class ClassifyTaskMetrics(Bean):
    auc = FloatField()
    accuracy = FloatField()
    recall = FloatField()
    precision = FloatField()
    f1 = FloatField()


class RegressionTaskMetrics(Bean):
    mse = FloatField()
    mae = FloatField()
    msle = FloatField()
    rmse = FloatField()
    rootmeansquarederror = FloatField()
    r2 = FloatField()


class BinaryLabel(Bean):
    true = ObjectField()
    false = ObjectField()


class ConfusionMatrix(Bean):
    fn = IntegerField()
    fp = IntegerField()
    tn = IntegerField()
    tp = IntegerField()
    label = BeanField(BinaryLabel)


class ROCCurve(Bean):
    false_positive_rate = ListObjectField()
    true_positive_rate = ListObjectField()
    thresholds = ListObjectField()


class Performance(Bean):
    metrics = DictField()  # RegressionTaskMetrics or ClassifyTaskMetrics
    confusion_matrix = BeanField(ConfusionMatrix)
    roc_curve = BeanField(ROCCurve)


class TaskType:
    MultiClassification = "multi_classification"
    BinaryClassification = "binary_classification"
    Regression = "regression"


class ModelFeature(Bean):
    name = StringField()
    type = StringField()
    data_type = StringField()


class TrainTrial(Bean):
    trial_no = IntegerField()
    status = StringField()
    extension = DictField()

    # if status is succeed, extension is :
    # reward = FloatField()
    # elapsed = FloatField()
    # params = DictField()

    # is status is failed, extension is:
    # reason = StringField()


class Model(Bean):
    name = StringField()
    framework = StringField()
    dataset_name = StringField()
    model_file_size = IntegerField()
    no_experiment = IntegerField()
    inputs = ListBeanField(ModelFeature)
    task_type = StringField()
    performance = BeanField(Performance)
    model_path = StringField()
    status = StringField()
    pid = IntegerField()
    score = FloatField()
    progress = StringField()
    train_job_name = StringField()
    train_trial_no = IntegerField()
    trials = ListBeanField(TrainTrial)
    extension = DictField()
    create_datetime = DatetimeField()
    finish_datetime = DatetimeField()
    last_update_datetime = DatetimeField()

    def escaped_time(self):
        if self.status in [ModelStatusType.Succeed, ModelStatusType.Failed]:
            if self.finish_datetime is None:
                raise Exception("Internal error, train finished but has no finish_datetime. ")
            escaped = util.datetime_diff_human_format_by_minute(self.finish_datetime, self.create_datetime)
        else:
            escaped = util.datetime_diff_human_format_by_minute(util.get_now_datetime(), self.create_datetime)
        return escaped

    def escaped_time_by_seconds(self):
        if self.status in [ModelStatusType.Succeed, ModelStatusType.Failed]:
            if self.finish_datetime is None:
                raise Exception(f"Internal error, model name = {self.name} train finished but has no finish_datetime. ")
            escaped = util.datetime_diff(self.finish_datetime, self.create_datetime)
        else:
            escaped = util.datetime_diff(util.get_now_datetime(), self.create_datetime)
        return escaped

    def default_metric(self):
        m = \
            {
                'multi_classification': "logloss",
                'regression': "mae",
                'binary_classification': "auc"
            }
        return m[self.task_type]

    def log_file_path(self):
        # exits begin from train start
        return util.relative_path(P.join(str(self.model_path), 'train.log'))

    def train_source_code_path(self):
        # exits begin from train start
        return util.relative_path(P.join(str(self.model_path), 'train.py'))

    def train_notebook_uri(self):
        # exits begin from train start
        train_notebook_path = P.join(str(self.model_path), 'train.ipynb')
        return util.relative_path(train_notebook_path)


class ModelStatusType(Bean):
    Succeed = STATUS_SUCCEED
    Failed = STATUS_FAILED
    Running = "running"


class TrialStatus:
    Succeed = STATUS_SUCCEED
    Failed = STATUS_FAILED
    Skip = 'skip'


class CrossValidation(Bean):
    n_folds = IntegerField()
    holdout_percentage = IntegerField()


CrossValidationDefault = CrossValidation(n_folds=5, holdout_percentage=20)


class TrainValidationHoldout(Bean):
    train_percentage = IntegerField()
    validation_percentage = IntegerField()
    holdout_percentage = IntegerField()
    random_state = IntegerField()


TrainValidationHoldoutDefault = TrainValidationHoldout(train_percentage=80,
                                                       validation_percentage=10,
                                                       holdout_percentage=10,
                                                       random_state=9527)


class TrainMode:
    Quick = "quick"
    Performance = "performance"
    Minimal = "minimal"


class ExperimentConf(Bean):
    dataset_name = StringField()
    dataset_has_header = BooleanField()
    dataset_default_headers = ListObjectField()
    train_mode = StringField()
    engine = StringField()
    label_col = StringField()
    pos_label = ObjectField()
    task_type = StringField()  # calc in frontend
    partition_strategy = StringField()
    cross_validation = BeanField(CrossValidation)
    train_validation_holdout = BeanField(TrainValidationHoldout)
    datetime_series_col = StringField()
    partition_col = StringField()
    # feature_series_name = StringField()
    file_path = StringField()
    test_file_path = StringField()

    class PartitionStrategy:
        CrossValidation = 'cross_validation'
        TrainValidationHoldout = 'train_validation_holdout'
        Manual = 'manual'


class PartitionClass:
  Train = 'TRAIN'
  Test = 'TEST'
  Eval = 'EVAL'


class FeatureTypeStats(Bean):
    categorical = IntegerField(default=0)
    continuous = IntegerField(default=0)
    text = IntegerField(default=0)
    datetime = IntegerField(default=0)


class FeatureType:
    Categorical = 'categorical'
    # CategoricalInt = 'categorical_int'

    Continuous = 'continuous'
    # ContinuousInt = 'continuous_int'

    Text = 'text'
    Datetime = 'datetime'


class ContinuousFeatureBin(Bean):
    begin = ObjectField()
    end = ObjectField()
    value = IntegerField()


class FeatureValueCount(Bean):
    type = ObjectField()
    value = IntegerField()


class FeatureMode(Bean):
    value = StringField()
    count = IntegerField()
    percentage = FloatField()


class CategoricalFeatureExtension(Bean):
    value_count = ListBeanField(FeatureValueCount)
    mode = BeanField(FeatureMode)


class ContinuousFeatureExtension(Bean):
    bins = ListBeanField(ContinuousFeatureBin)
    min = FloatField()
    max = FloatField()
    mean = FloatField()
    stddev = FloatField()
    median = FloatField()
    value_count = ListBeanField(FeatureValueCount)


class YearValueCount(Bean):
    year = IntegerField()
    value = IntegerField()


class DatetimeFeatureExtension(Bean):
    by_year = ListBeanField(YearValueCount)
    by_month = ListObjectField()
    by_day = ListObjectField()
    by_week = ListObjectField()
    by_hour = ListObjectField()


class DatasetStats(Bean):
    label_col = StringField()
    file_path = StringField()
    has_header = BooleanField()
    n_rows = IntegerField()
    n_cols = IntegerField()
    features = ListBeanField(Feature)
    feature_summary = BeanField(FeatureTypeStats)
    create_datetime = IntegerField()

    @property
    def features_names(self):
        return [f.name for f in self.features]


class RestResponse(object):

    def __init__(self, code, data):
        """
        :param code:
        :param data: dict
        """
        self.code = code
        self.data = data

    def to_json(self):
        result = {"code": self.code, "data": self.data}
        return util.dumps(result)


class ErrorResponse(object):

    def __init__(self, code, message):
        """
        :param code:
        :param data: dict
        """
        self.code = code
        self.data = {
            "message": message
        }

    def to_json(self):
        result = {"code": self.code, "data": self.data}
        return util.dumps(result)


class ResponseCode(object):
    Success = 0
    Exception = -1


class LocaleInfo(object):
    def __init__(self, lang):
        self.lang = lang

    class Types(object):
        English = "en_US"
        HanYu = "zh_CN"
        UseClient = "use_client"


class RespPreviewDataset(Bean):
    headers = ListObjectField()
    rows = ListObjectField()
    count = IntegerField()
    file_path = StringField()
