# -*- encoding: utf-8 -*-

from sklearn.model_selection import train_test_split

from deeptables.models.hyper_dt import DTModuleSpace, DnnModule, DTFit, HyperDT
from hypernets.core.callbacks import SummaryCallback, FileLoggingCallback
import pandas as pd

from hypernets.core.search_space import HyperSpace, MultipleChoice, Bool, Choice
from hypernets.searchers.mcts_searcher import MCTSSearcher
from deeptables.utils import consts as DT_consts

import time


def my_space():
    space = HyperSpace()
    with space.as_default():
        p_nets = MultipleChoice(
            ['dnn_nets', 'linear', 'fm_nets'], num_chosen_most=2)
        dt_module = DTModuleSpace(
            nets=p_nets,
            auto_categorize=Bool(),
            cat_remain_numeric=Bool(),
            auto_discrete=Bool(),
            apply_gbm_features=Bool(),
            gbm_feature_type=Choice([DT_consts.GBM_FEATURE_TYPE_DENSE, DT_consts.GBM_FEATURE_TYPE_EMB]),
            embeddings_output_dim=Choice([4, 10]),
            embedding_dropout=Choice([0, 0.5]),
            stacking_op=Choice([DT_consts.STACKING_OP_ADD, DT_consts.STACKING_OP_CONCAT]),
            output_use_bias=Bool(),
            apply_class_weight=Bool(),
            earlystopping_patience=Choice([3,5,10])
        )

        dnn = DnnModule(dnn_units=Choice([100, 200]),
                        reduce_factor=Choice([1, 0.8]),
                        dnn_dropout=Choice([0, 0.3]),
                        use_bn=Bool(),
                        dnn_layers=2,
                        activation='relu')(dt_module)
        fit = DTFit(batch_size=Choice([128, 256]))(dt_module)

    return space


rs = MCTSSearcher(my_space, max_node_space=5)

hdt = HyperDT(rs,
              callbacks=[SummaryCallback(), FileLoggingCallback(rs)],
              reward_metric='AUC',
              dnn_params={
                  'dnn_units': ((256, 0, False), (256, 0, False)),
                  'dnn_activation': 'relu',
              })

from deeptables.datasets import dsutils

df = dsutils.load_bank()[:1000]
print("data shape: ")
print(df.shape)

df.drop(['id'], axis=1, inplace=True)
y = df.pop("y")
X = df

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=12)


t1 = time.time()
hdt.search(X_train, y_train, X_test, y_test, max_trails=1)

best_trial = hdt.get_best_trail()
estimator = hdt.final_train(best_trial.space_sample, X_train, y_train)

print("escaped: ")
print(time.time()-t1)

r = estimator.evaluate(X_test, y_test, metrics=['accuracy', 'auc'])
print(r)

y_score = estimator.predict_proba(X_test)
# y_pred = estimator.predict(X_test)

from sklearn.metrics import roc_curve
fpr,tpr,thresholds = roc_curve(y_test, y_score, pos_label='yes')
ks = max(tpr-fpr)
print(ks)
