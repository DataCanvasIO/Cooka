Release Note
=====================

Version 0.1.2
-------------

**实验设计**
- 使用设置随机种子来拆分训练集和测试集

**实验列表**
- 超参数图表中，参数的折线颜色与reward关联(修复bug)

** 其他 **
- Update hypergbm to 0.2.2


Version 0.1.1
-------------

这个版本包含以下新特性:

**数据集管理**

- 搜索
- 删除
- 上传、导入csv
    * 分析抽样支持按行数、按比例、和使用全量数据
    * 支持无列头数据集文件
    * 自动推断特征类型（连续、离散、日期）

**数据集预览**

- 查看原始数据集
- 数据表格滚动加载

**数据集探查**

- 特征类型分布
- 特征的数据类型、特征类型、缺失值、不同值、线性相关分析
- Id列、常量列、过多缺失值列识别
- 特征检索
- 日期类型特征支持
    - 按年、月、日、时、星期分布
- 类别特征
    - 值分布
    - 众数
- 连续特征
    - 区间分布
    - 值分布
    - 最大值，最小值，中位数，均值，标准差

**实验设计**

- 自动推荐建模选项
- HyperGBM、HyperDT实验引擎
- 快速、性能训练模式
- Train-Validation-Holdout数据拆分模式
- 按日期顺序拆分数据
- 支持任务类型
    - 二分类
    - 多分类
    - 回归

**实验列表**

- 训练进度、剩余时间评估
- 混淆矩阵、ROC曲线(二分类)
- 评估指标
    - 二分类： Accuracy, F1, Fbeta, Precision, Recall, AUC, Log Loss
    - 多分类： Accuracy, F1, Fbeta, Precision, Recall, Log Loss
    - 回归： EVS, MAE, MSE, RMSE, MSLE, R2, MedianAE
- 查看训练日志、训练源码
- 导出成Notebook文件
- 优化参数可视化
- 批量预测

