## 配置文件

Cooka 提供了一个命令来生成配置文件模板:
```shell
❯ cooka generate-config

# Configuration file for cooka

# HTTP 服务端口
# c.CookaApp.server_port = 8000

# 语言，可以设置为 zh_CN, en_US, auto; 如果是auto将使用浏览器中到语言信息
# c.CookaApp.language = "auto"

# Cooka的数据目录
# c.CookaApp.data_directory = "~/cooka"

# Jupyter 的访问地址，Jupyter的工作目录应与Cooka的数据目录一致
# c.CookaApp.notebook_portal = "http://localhost:8888"

# 不同任务类型的默认优化指标
# c.CookaApp.optimize_metric = {
#     "multi_classification_optimize": "accuracy",
#     "binary_classification": "auc",
#     "regression": "rmse"
# }

# 不同训练模式的trails个数
# c.CookaApp.max_trials = {
#     "performance": 50,
#     "quick": 10,
#     "minimal": 1
# }

```
把配置模板写入到配置文件`~/.config/cooka/cooka.py`中:
```shell
mkdir -p ~/.config/cooka/
cooka generate-config > ~/.config/cooka/cooka.py
```
