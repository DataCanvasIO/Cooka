Release Note
=====================

Version 0.1.0
-------------


**Dataset manage**

- Search
- Delete
- Upload or import CSV
    * Sampling analysis
    * Support no column headers
    * Inferring feature types

**Dataset preview**

- Cat origin file on line
- Scrolling

**Dataset insight**

- Distribution of feature type
- Data type, feature type, missing percentage,  uniques, linear correlation
- Recognize Id-ness, constant, missing percentage too high features
- Feature search
- Datetime features
    - Display by year, month, day, hour, week
- Categorical features
    - Distribution of values
    - Mode
- Continuous features
    - Distribution of interval
    - Distribution of values
    - max, min, median, mean, stand deviation

**Experiment design**

- Recommend experiment options
- HyperGBM,HyperDT as experiment engine
- Quick, performance training mode
- Train-Validation-Holdout data partition
- Split data in datetime order
- Support binary classification, multi-classification, regression

**Experiment list**

- Training process,
- Remaining time estimation
- Confusion matrix and ROC curve for binary-classification
- Evaluation metrics
    - Binary classification： Accuracy, F1, Fbeta, Precision, Recall, AUC, Log Loss
    - Multi-classification： Accuracy, F1, Fbeta, Precision, Recall, Log Loss
    - Regression： EVS, MAE, MSE, RMSE, MSLE, R2, MedianAE
- View train log and source code
- Export to notebook
- Hyper-params
- Batch predict
