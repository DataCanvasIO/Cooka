# -*- encoding: utf-8 -*-
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import roc_auc_score, mean_squared_log_error, accuracy_score, \
    mean_squared_error, mean_absolute_error, r2_score, precision_score, recall_score, f1_score, fbeta_score, log_loss

from sklearn.datasets import load_iris
X, y = iris_data = load_iris(return_X_y=True)

from sklearn.linear_model import LogisticRegression

lr = LogisticRegression()
lr.fit(X, y)
y_test = y
y_score = lr.predict_proba(X)
y_pred = lr.predict(X)


accuracy_value = accuracy_score(y_test, y_pred)
print(accuracy_value)

f1_value = f1_score(y_test, y_pred, average='micro',)
print(f1_value)

fbeta_value = fbeta_score(y_test, y_pred, beta=10, average='micro')  # beta == 10 from aps
print(fbeta_value)

precision_value = precision_score(y_test, y_pred, average='micro')
print(precision_value)

recall_value = recall_score(y_test, y_pred, average='micro')
print(recall_value)


log_loss_value = log_loss(y_test, y_score)
print(log_loss_value)


metrics_dict = {"accuracy": accuracy_value,
                "f1": f1_value,
                "fbeta": fbeta_value,
                "precision": precision_value,
                "recall": recall_value,
                "log_loss": log_loss_value
                }

print(metrics_dict)



