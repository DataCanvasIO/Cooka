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
```shell
docker run -ti -p 888:8888 -p 8000:8000 -p 9001:9001 -e COOKA_NOTEBOOK_PORTAL=http://<your_ip>:8888 datacanvas/cooka:latest
```

打开浏览器访问 `http://<your-ip>:8000` 来使用Cooka
Open browser visit site `http://<your-ip>:8000`，notebook的token您设置的"you-token"，如果不指定则为空。

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
