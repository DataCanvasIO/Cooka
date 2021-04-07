## Installation

You can use docker,pip and source code to install Cooka.

### Using pip

It requires `Python3.6` or above, uses pip to install Cooka:

```shell
pip install --upgrade pip setuptools # (optional)
pip install cooka
```

then start cooka web server:

```shell
cooka server
```

Open browser visit site `http://<your-ip>:8000` to use Cooka. If you want to integrate with jupyter notebook please refer to this [guide](configuration/integrate_with_jupyter.md). 


### Using Docker

You can also use Cooka through docker with command:
```
docker run -ti -p 8000:8000 -p 9001:9001 datacanvas/cooka:latest
# port 9001 is supervisor(which used to manage process) web ui, and the account/password is: user/123 
# port 8000 is cooka web ui
```
Open browser and visit site `http://<your-ip>:8000` to use cooka.

If you want to integrate with jupyter notebook, please specify jupyter url running in the container:
```
docker run -ti -p 8000:8000 -p 9001:9001 -p 8888:8888 -e COOKA_NOTEBOOK_PORTAL=http://<your_ip>:8888 datacanvas/cooka:latest
# port 8888 is jupyter notebook
```

You can persist data in the host:
```shell script
docker run -v /path/to/cooka-config-dir:/root/.config/cooka -v /path/to/cooka-data:/root/cooka -ti -p 8000:8000 -p 9001:9001 datacanvas/cooka:latest
# Config file is at: /root/.config/cooka/cooka.py
# User data is at: /root/cooka
```

### Using source code

Frontend developed by [reactjs](https://reactjs.org), therefore, we need to install [node>=8.0.0](https://nodejs.org/en/) get it at [https://nodejs.org](https://nodejs.org) and install [yarn](https://yarnpkg.com):

```shell
npm install yarn -g
```

Finally build frontend and install them all：
```shell
pip install --upgrade pip setuptools
git clone git@github.com:DataCanvasIO/Cooka.git

cd Cooka
python setup.py buildjs  # build frontend
python setup.py install
```
