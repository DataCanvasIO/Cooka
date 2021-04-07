## 安装教程

你可以通过docker、pip、和源码来安装Cooka.

### 使用pip

Cooka需要 `Python3.6` 或者以上版本, 用pip安装命令 :

```shell
pip install --upgrade pip setuptools # (optional)
pip install cooka
```

启动Cooka的Web服务:

```shell
cooka server
```

打开浏览器访问 `http://<your-ip>:8000` 来使用Cooka. 整合jupyter notebook参考[教程](configuration/integrate_with_jupyter.md). 


### 使用 Docker

使用Docker拉起一个Cooka 服务：
```
docker run -ti -p 8000:8000 -p 9001:9001 datacanvas/cooka:latest
# port 9001 is supervisor(which used to manage process) web ui, and the account/password is: user/123 
# port 8000 is cooka web ui
```
打开浏览器访问 `http://<your-ip>:8000` 来使用Cooka。

如果需要与jupyter notebook 整合，请指定运行在容器中的jupyter的url： 
```
docker run -ti -p 8000:8000 -p 9001:9001 -p 8888:8888 -e COOKA_NOTEBOOK_PORTAL=http://<your_ip>:8888 datacanvas/cooka:latest
# port 8888 is jupyter notebook
```

您可也可以把数据存储在主机中:
```shell script
docker run -v /path/to/cooka-config-dir:/root/.config/cooka -v /path/to/cooka-data:/root/cooka -ti -p 8000:8000 -p 9001:9001 datacanvas/cooka:latest
# Config file is at: /root/.config/cooka/cooka.py
# User data is at: /root/cooka
```

### 从源码安装

Cooka的Web页面使用[reactjs](https://reactjs.org)开发，因此需要先安装[node>=8.0.0](https://nodejs.org/en/) 再安装[yarn](https://yarnpkg.com)来构建Cooka:

```shell
npm install yarn -g
```

安装构建环境完成后来构建Cooka并安装：：
```shell
pip install --upgrade pip setuptools
git clone git@github.com:DataCanvasIO/Cooka.git

cd Cooka
python setup.py buildjs  # build frontend
python setup.py install
```
