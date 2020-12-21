# -*- encoding: utf-8 -*-

import abc
import json
import numpy as np
import six
from sklearn import metrics
from sklearn.utils.class_weight import compute_sample_weight
import sklearn

@six.add_metaclass(abc.ABCMeta)
class BaseMetric(object):

    def __init__(self, y_true, y_pred, y_score):
        self.y_true = y_true
        self.y_pred = y_pred
        self.y_score = y_score

    def sample_weight(self, y_true):
        return compute_sample_weight('balanced', y=y_true)

    @abc.abstractmethod
    def compute(self):
        pass


# class ConfusionMatrixMetric(BaseMetric):
#
#
#
#
# class RocCurveMetric(BaseMetric):
#
#     def build_roc_curve(self, fpr_rf_lm, tpr_rf_lm, roc_auc_score):
#         data = []
#         roc_curves_BINARYCLASSIF = {"data": data}
#         roc_curves_BINARYCLASSIF["roc_auc"] = roc_auc_score
#         roc_curves = {"BINARYCLASSIF": roc_curves_BINARYCLASSIF}
#         if len(fpr_rf_lm) == len(tpr_rf_lm):
#             for i in range(len(fpr_rf_lm)):
#                 onePoint = {}
#                 onePoint['False positive rate'] = fpr_rf_lm[i]
#                 onePoint['True positive rate'] = tpr_rf_lm[i]
#                 data.append(onePoint)
#         return roc_curves
#
#     def compute(self):
#         roc_auc_score = metrics.roc_auc_score(y_true=self.y_true, y_score=self.y_score,
#                                               sample_weight=self.sample_weight(self.y_true))
#         # fpr_rf_lm, tpr_rf_lm, _ = metrics.roc_curve(y_true=y_true, y_score=y_score,
#         #                                            sample_weight=self.sample_weight(y_true))
#         # roc_curve_data = self.build_roc_curve(fpr_rf_lm, tpr_rf_lm, roc_auc_score)
#         # return json.dumps(roc_curve_data)
#
#         return roc_auc_score



# def compute(self):
#     pre_confusion_matrix = metrics.confusion_matrix(y_true=self.y_true,
#                                                     y_pred=self.y_pred,
#                                                     sample_weight=self.sample_weight(self.y_true))
#     confusion_matrix = pre_confusion_matrix.astype('float') / pre_confusion_matrix.sum(axis=1)[:, np.newaxis]
#     n_classes = np.unique(self.y_true)
#     cmData = self.build_confusion_matrix(confusion_matrix, n_classes)
#     return json.dumps(cmData)
#
# def build_confusion_matrix(self, confusion_matrix, classes):
#     shape = confusion_matrix.shape
#     if shape[0] == len(classes) & shape[1] == len(classes):
#         predictedActual = {}
#         confusionMatrix = {"PredictedActual": predictedActual}
#         cm = {"confusion_matrix": confusionMatrix}
#         for rowNum in range(shape[0]):
#             per_predicted = {}
#             classDict = {"per_predicted": per_predicted}
#             for colNum in range(shape[1]):
#                 per_predicted[str(classes[colNum])] = confusion_matrix[rowNum][colNum]
#             predictedActual[str(classes[rowNum])] = classDict
#         return cm
#     else:
#         raise Exception("confusion_matrix data is illegal!")

y_pred = [1, 1, 0, 1]
y_true = [0, 1, 0, 1]
y_prob = [0.6, 0.6, 0.6, 0.6]

confusion_matrix = metrics.confusion_matrix(y_true=y_true,
                                                y_pred=y_pred,
                                                sample_weight=compute_sample_weight('balanced', y=y_true))
# confusion_matrix = pre_confusion_matrix.astype('float') / pre_confusion_matrix.sum(axis=1)[:, np.newaxis]

# tn, fp, fn, tp = confusion_matrix([0, 1, 0, 1], [1, 1, 1, 0]).ravel()
# print(confusion_matrix)


fpr, tpr, thresholds = sklearn.metrics.roc_curve(y_true, y_prob, pos_label=None, sample_weight=None, drop_intermediate=True)
print(fpr)