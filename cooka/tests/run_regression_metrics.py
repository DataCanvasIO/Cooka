# -*- encoding: utf-8 -*-
from sklearn import metrics
import numpy as np
import math

y_true = np.array([1,3,4,5])
y_pred = np.array([2,3.5,4,5])

explained_variance = round(metrics.explained_variance_score(y_true=y_true, y_pred=y_pred), 4)
neg_mean_absolute_error = round(metrics.mean_absolute_error(y_true=y_true, y_pred=y_pred), 4)
neg_mean_squared_error = round(metrics.mean_squared_error(y_true=y_true, y_pred=y_pred), 4)
rmse = round(math.sqrt(neg_mean_squared_error), 4)
neg_median_absolute_error = round(metrics.median_absolute_error(y_true=y_true, y_pred=y_pred), 4)
r2 = round(metrics.r2_score(y_true=y_true, y_pred=y_pred), 4)

if (y_true >= 0).all() and (y_pred >= 0).all():
    neg_mean_squared_log_error = round(metrics.mean_squared_log_error(y_true=y_true, y_pred=y_pred), 4)
else:
    neg_mean_squared_log_error = None

metrics_dict = {"explained_variance": explained_variance,
                "neg_mean_absolute_error": neg_mean_absolute_error,
                "neg_mean_squared_error": neg_mean_squared_error,
                "rmse": rmse,
                "neg_mean_squared_log_error": neg_mean_squared_log_error,
                "r2": r2,
                "neg_median_absolute_error": neg_median_absolute_error
                }

print(metrics_dict)
