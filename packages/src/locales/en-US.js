export default {
  // 数据集列表
  'datasetlist.placeholder': 'Input dataset name',
  'datasetlist.new': 'New Dataset',
  'datasetlist.upload': 'Upload',
  'datasetlist.import': 'Import',
  'datasetlist.name': 'Name',
  'datasetlist.rows': 'Rows',
  'datasetlist.cols': 'Columns',
  'datasetlist.size': 'Size',
  'datasetlist.time': 'Experiments',
  'datasetlist.date': 'Datetime',
  'datasetlist.option': 'Action',
  'datasetlist.del': 'Delete',
  'datasetlist.delSucceed': 'Deleted',
  'datasetlist.uploadFile': 'Upload',
  'datasetlist.systemImport': 'Import',
  'datasetlist.address': 'Path',
  'datasetlist.source': 'Source',
  'datasetlist.confirm': 'Confirm to delete？',
  'datasetlist.ok': 'Delete',
  'datasetlist.cancel': 'Cancel',
  'datasetlist.nomore': 'No more data',

  'createDataset.sampleTip': 'Sampling can get analysis results more quickly especially when the data is too large',

  // 文件上传
  'upload.uploadFile': 'Upload file',
  'upload.upload': 'Upload',
  'upload.anaysis': 'Sampling analysis',
  'upload.col': 'By rows',
  'upload.percent': 'By percentage',
  'upload.nCol': 'Number of rows',
  'upload.nPercent': 'Percentage',
  'upload.tips': 'Less than 1000 rows, all data will be used',
  'upload.uploadTips': 'Support CSV files, at least 2 columns are required and lines with missing label will be ignored',
  'upload.details': 'learn more',
  'upload.uploadBox': 'Click or drag file here to upload',
  'upload.name': 'Dataset Name',
  'upload.create': 'Create',
  'upload.uploadStep': 'Upload',
  'upload.loadData': 'Load data',
  'upload.analysisData': 'Analysis data',
  'upload.prepare': 'Not started',
  'upload.uploading': 'Uploading...',
  'upload.loading': 'Loading...',
  'upload.analysising': 'Analysis in progress...',
  'upload.fail': 'Load data failed',

  'upload.hintUploadFile': 'Elapsed {elapsed}s, file size {fileSize}',
  'upload.hintLoadData': 'Elapsed {elapsed}s, data shape is ({nRows}, {nColumns})，load {nRowsUsed} rows',
  'upload.hintAnalysis': 'Elapsed {elapsed}s, there are {nContinuous} continuous, {nCategorical} categorical, {nDatetime} datetime features',
  'upload.hintWholeData': 'The use of whole data analysis will take a long time, suitable for small amount of data',

  'upload.necessary': 'Required',
  'upload.rule': 'Only numbers are allowed',
  'upload.big': 'File is too big ',
  'upload.uploadFail': 'Upload failed',
  'upload.wholeData': 'Whole data',

  // 本地导入
  'import.import': 'Import',
  'import.copy': 'Copy file',
  'import.fail': 'Analysis failed',
  'import.address': 'File path',
  'import.analysis': 'Analysis',

  // 数据预览
  'preview.viewOriginFile': 'You can view original file to check that the dataset was read correctly ',
  'preview.view': 'Check it out',

  // 数据探查
  'explore.name': 'Name',
  'explore.type': 'Type',
  'explore.missing': 'Missings',
  'explore.diff': 'Uniques',
  'explore.correlation': 'Correlation with Target',
  'explore.num': 'Continuous',
  'explore.category': 'Categorical',
  'explore.date': 'Datetime',
  'explore.text': 'Text',
  'explore.placeholder': 'Search',
  'explore.max': 'Maximum',
  'explore.min': 'Minimum',
  'explore.medium': 'Median',
  'explore.mean': 'Mean',
  'explore.std': 'Standard deviation',
  'explore.usual': 'Mode',
  'explore.cols': 'columns',
  'explore.dataType': 'Data type',
  'explore.goTrain': 'Train as Target',
  'explore.labelCol': 'Target',
  'explore.histogram': 'Histogram',
  'explore.pie': 'Pie chart',
  'explore.tooMuchMissing': 'More than 70% of all values are missing',
  'explore.stableFeature': 'More than 90% of all values being the same',
  'explore.idNess': 'ID-ness column, different values almost as many as rows',
  'explore.correlationTooHigh': 'Absolute correlation > 0.5 ',
  'explore.correlationTooLow': 'Absolute correlation < 0.01',
  'explore.hintType': 'str type is inferred as categorical feature, int and float type are inferred as continuous feature, yyyy-MM-dd HH:mm:ss format string is inferred as datetime feature',
  'explore.hintDataType': 'Data types in pandas',
  'explore.hintSampling': 'sampling {samplingInfo}',
  'explore.hintNoSampling': 'use whole data',
  'explore.hintMissing': 'Percentage of missing values in this column, {samplingInfo}',
  'explore.row': 'rows',
  'explore.hintUniques': 'The number of different values in this column, {samplingInfo}',  // sampleInfo 可以是 10% 或者 2000行
  'explore.hintCorrelation': 'Calculate by pearson， value ranges is [- 1,1], the greater the absolute value, the stronger the correlation. Positive and negative correlation means positive correlation or negative correlation, and unusually high correlation is indicative of target leakage',

  // 模型训练
  'train.basicOpt': '基础选项',
  'train.tagCol': 'Target',
  'train.normalSampleModal': 'Positive label',
  'train.trainMode': 'Train mode',
  'train.experimentEngine': 'Experiment engine',
  'train.quick': 'Quick mode',
  'train.performance': 'Performance mode',
  'train.minimal': 'Minimum mode*',
  'train.advancedOpt': '高级选项',
  'train.dataAllot': 'Data partition',
  'train.crossVerified': 'Cross Validation',
  'train.partition.manual': 'Manual',
  'train.divisionNum': 'K-Folds',
  'train.testUnionPercentage': 'Test dataset percentage',
  'train.cvdata': 'CV Data',
  'train.testUnion': 'Test Dataset',
  'train.datetimeCol': 'Datetime series feature',
  'train.select': 'Please select',
  'train.datetimeColSelectorNoItem': 'No datetime features',
  'train.partition.noPartitionCols': 'No partition features',
  'train.partition.hint': 'Train-Validation-Holdout divided dataset into training set, evaluation set and test set; Manual mode allows select a feature to partition，this column values should be "TRAIN","EVAL","TEST"',
  'train.train': 'Train',
  'train.labelNotEmpty': 'Label columns is required',
  'train.posNotEmpty': 'Positive label is required',
  'train.taskType': 'Task type',
  'train.taskBinaryClassification': 'Binary Classification',
  'train.taskMultiClassification': 'Multi Classification',
  'train.taskRegression': 'Regression',
  'train.hintInferTaskType': 'A {taskType} task will be created',
  'train.hintTaskType': 'Only two different values in target should be inferred as Binary Classification, target data type is float can be inferred as Regression and other types are inferred as Multi Classification, more than 1000 categories not supported ',
  'train.hintTrainMode': 'Performance mode will use larger parameter space and more iterations than fast mode, in general, the model should also work better, but it will take more time',
  'train.hintDatetimeSeriesFeature': 'Used to split the data in chronological order. If your data is in chronological order and the model is to predict future values, this option can help improve the prediction ability of the model',
  'train.hintTarget': 'Select target column to train',
  'train.hintPositiveLabel': 'Positive label help to evaluate the model correctly',
  'train.hintExperimentEngine': 'Experiment Engine',

  // 模型中心
  'center.trainingPanelTitle': 'Experiment No. {noExperiment}',
  'center.modal': 'Experiment No ',
  'center.target': 'Score',
  'center.process': 'Progress ',
  'center.remain': 'Remaining time',
  'center.spend': 'Elapsed',
  'center.size': 'Size',
  'center.log': 'Log',
  'center.source': 'Source code',
  'center.finished': 'Finished',
  'center.evaluate': 'Evaluate result',
  'center.predict': 'Batch predict',
  'center.evaluate.predict': 'Predict',
  'center.param': 'Hyper parameters',
  'center.mix': 'Confusion matrix',
  'center.actual': 'actual',
  'center.modalEvaluate': 'Metrics',
  'center.roc': 'ROC curve',
  'center.uploadBox': 'Click or drag file here to upload',
  'center.uploadtips': 'Support CSV files, up to 128MB',
  'center.uploadData': 'Upload data',
  'center.loadData': 'Load data',
  'center.read': 'Load model',
  'center.predictData': 'Evaluate data',
  'center.result': 'Write result',
  'center.upload': 'Upload file',

  'center.batchPredict.processTip.upload': 'File size is {fileSize}, took {took}s',
  'center.batchPredict.processTip.loadData': 'Data shape is ({nRows}, {nCols}), took {took}s',
  'center.batchPredict.processTip.loadModel': 'Model size is {modelSize}, took {took}s',
  'center.batchPredict.processTip.evaluate': 'Took {took}s',
  'center.batchPredict.processTip.writeResult': 'Download result',


  'center.readed': 'Read',
  'center.rows': 'row',
  'center.cols': 'columns',
  'center.modalSize': 'model directory size',
  'center.download': 'Download result',
  'center.training': 'The model is in training, please check it later',
  'center.fail': 'model train failed，',
  'center.bug': 'view log',
  'center.success': 'File uploaded successfully',
  'center.big': 'File to big',
  'center.failUpload': 'File uploaded failed',
  'center.hintConfusionMatrix': 'The confusion matrix is a table where each row is a predicted class and each column is the observed class. The cells of the matrix indicate how often each classification prediction coincides with each observed label. This matrix is useful for determining which misclassifications occur most often, i.e. which classes often get "confused" with each other',
  'center.hintOptimizeMetric': 'The model score of last trial',
  'center.hintProgress': 'Parameter search progress, searched times / expected times. By default, the early stopping method is used. When the prediction ability of the model cannot be improved, the training will be stopped in advance',
  'center.hintRemainingTime': 'Estimated remaining time , calculate by the time consumed by the completed trials, The remaining time can only be evaluated by at least one successful trial',
  'center.hintElapsed': 'time consumed',

  'center.hintModelSize': 'The total size of the model file is displayed after the model training is successful',
  'center.hintSourceCode': 'Source code for training model',
  'center.hintLog': 'Training log',
  'center.hintNotebook': 'Training source code export to notebook, need to configure c.CookaApp.notebook_portal options',
  'center.titleNotebook': 'Notebook',
  'center.titleResource': 'Resource',
  'center.hintResource': 'You can view the source code and log of the experiment and notebook export from source code. Notebook needs options c.CookaApp.notebook_portal in the configuration file to be configured correctly',

  'center.hintEarlyStopping': 'Because the performance of the model could not be improved, the training was stopped in advance',
  'center.titleEngine': 'Engine',
  'center.hintTargetCol': 'Target is {targetCol}',

  // extra stuff
  'extra.dataset': 'Dataset',
  'extra.new': 'New Dataset',
  'extra.name': 'Dataset Name',
  'extra.create': 'Create',
  'extra.explore': 'Explore',
  'extra.preview': 'Preview',
  'extra.dataExplore': 'Insight',
  'extra.train': 'Design',
  'extra.center': 'Experiment',
  'extra.doc': ' ', // DataCanvas AutoML Toolkit
  // 'extra.doc': 'Documentation',
  'extra.testAndTrain': 'Train-Validation-Holdout',
  'extra.verifyUnion': 'Validation',
  'extra.trainUnion': 'Training',
  'extra.testUnion': 'Test',
  'extra.inputName': 'Please input dataset name',
  'extra.rule': '名称只允许包含数字、字母和下划线',

}
