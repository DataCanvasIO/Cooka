## Install using source code

Frontend developed by [reactjs](https://reactjs.org)，therefore, we need to install [node>=8.0.0](https://nodejs.org/en/) first，get it at [https://nodejs.org](https://nodejs.org), then install [yarn](https://yarnpkg.com)：
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

If you want to integrat with notebook, please refer to [Integrate with Notebook](docs/pages/install_with_jupyter.md).
