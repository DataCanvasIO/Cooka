## 与Jupyter Notebook整合

**1. 安装依赖**

与Jupyter Notebook整合需要以下python模块:

- shap: 用来解释模型
- jupyterlab: notebook 服务
- matplotlib: 在notebook中绘图

您可以参照这个[文档]()来安装shap。

用pip来安装jupyterlab:
```shell script
pip install jupyterlab
```

`matplotlib`依赖系统包`graphviz` 以在centos 7上安装它为例：

```shell script
sudo yum install graphviz
```

接着用pip安装matplotlib：
```shell script
pip install matplotlib
```

**2. 启动Jupyter Notebook**

需要在Cooka的工作目录启动jupyterab，默认在`~/cooka`: 
```shell script
cd ~/cooka
jupyter-lab --ip=0.0.0.0 --no-browser --allow-root --NotebookApp.token= 
```

**3. 配置Cooka**

需要在Cooka的配置`~/.config/cooka/cooka.py`中来配置jupyter notebook的访问地址：:
```shell script
c.CookaApp.notebook_portal = "http://<change_to_you_jupyter_ip>:8888"
```

启动Cooka的Web服务：
```shell script
cooka server
```

然后试试在实验列表中选择实验导出成Notebook吧。
