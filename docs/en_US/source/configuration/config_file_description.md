## Configuration file

Cooka provides a command to generate config template:
```shell
❯ cooka generate-config

# Configuration file for cooka

# HTTP Server port
# c.CookaApp.server_port = 8000

# Language, zh_CN or en_US, auto; if is auto will read localization from use browser
# c.CookaApp.language = "auto"

# Data to storage
# c.CookaApp.data_directory = "~/cooka"

# Integrate with jupyter, Jupyter notebook work dir should at `c.CookaApp.data_directory`
# c.CookaApp.notebook_portal = "http://localhost:8888"

# Default optimize metric
# c.CookaApp.optimize_metric = {
#     "multi_classification_optimize": "accuracy",
#     "binary_classification": "auc",
#     "regression": "rmse"
# }

# Default trial nums
# c.CookaApp.max_trials = {
#     "performance": 50,
#     "quick": 10,
#     "minimal": 1
# }

```
Write it to configuration file at `~/.config/cooka/cooka.py`:
```shell
mkdir -p ~/.config/cooka/
cooka generate-config > ~/.config/cooka/cooka.py
```
