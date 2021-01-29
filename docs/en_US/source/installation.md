## Installation

You can use not only docker or pip to install Cooka but also build from source code.

### Using pip

It requires `Python3.6` or above, and uses pip to install Cooka:

```shell script
pip install --upgrade pip setuptools # (optional)
pip install cooka
```

and then start cooka web server:

```shell script
cooka server
```

Open browser visit site `http://<your-ip>:8000` to use cooka. If you want to integrate with jupyter notebook please refer to this [guide](configuration/intergrate_with_jupyter.md). 


### Using Docker

You can also use Cooka through docker image with command:
```shell script
docker run -ti -e NOTEBOOK_TOKEN="your-token" -e COOKA_NOTEBOOK_PORTAL=http://<your_ip>:8888 -p 8888:8888 -p 8000:8000 datacanvas/hypergbm:0.1.0
```

Open browser visit site `http://<your-ip>:8000`，the notebook token is what you have set "you-token"，it can also be empty if do not specified.


## Using source code

Frontend developed by [reactjs](https://reactjs.org), therefore, we need to install [node>=8.0.0](https://nodejs.org/en/) get it at [https://nodejs.org](https://nodejs.org) and install [yarn](https://yarnpkg.com):

```shell script
npm install yarn -g
```

Finally build frontend and install them all：
```shell script
pip install --upgrade pip setuptools
git clone git@github.com:DataCanvasIO/Cooka.git

cd Cooka
python setup.py buildjs  # build frontend
python setup.py install
```
