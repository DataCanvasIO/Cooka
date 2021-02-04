#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import join as pjoin
import shutil
from setuptools import setup, find_packages
import distutils.cmd
import distutils.log
import subprocess
from os import path as P


try:
    execfile
except NameError:
    def execfile(fname, globs, locs=None):
        locs = locs or globs
        exec(compile(open(fname).read(), fname, "exec"), globs, locs)

HERE = P.dirname((P.abspath(__file__)))

version_ns = {}
execfile(P.join(HERE, 'cooka', '_version.py'), version_ns)
version = version_ns['__version__']

print("__version__=" + version)

with open(P.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class BuildJSCommand(distutils.cmd.Command):

    description = 'Build frontend that written by javascript'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # 1. check files
        frontend_home = pjoin(HERE, 'packages')
        backend_assets = pjoin(HERE, 'cooka', 'assets')
        if P.exists(backend_assets):
            raise RuntimeError(f"Assets path {backend_assets} already exists")

        # 2. install deps by yarn
        yarn_executable = 'yarn'
        self.announce("yarn install ", distutils.log.INFO)
        subprocess.call([yarn_executable, 'install'], cwd=frontend_home)

        # 3. build assets
        self.announce("yarn build ", distutils.log.INFO)
        subprocess.call([yarn_executable, 'build'],  cwd=frontend_home)

        # 4. copy to python package
        frontend_dist = pjoin(frontend_home, 'dist')
        shutil.copytree(frontend_dist, backend_assets)


if __name__ == '__main__':

    setup(
        name="cooka",
        version=version,
        description="A lightweight AutoML system.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        packages=find_packages(exclude=["test.*", "test"]),
        author="DataCanvas Community",
        author_email="yangjian@zetyun.com",
        cmdclass={'buildjs': BuildJSCommand},
        python_requires='>=3.6.*',
        license='Apache License 2.0',
        install_requires=[
            'numpy',
            'pandas',
            'scikit-learn>=0.22.1',
            'requests',
            'SQLAlchemy>=1.3.18',
            'tornado==6.0.4',
            'jinja2',
            'deeptables==0.1.13',
            'hypergbm==0.2.1',
            'traitlets',
        ],
        # extras_require={
        #     'notebook': [
        #         'shap',
        #         'jupyterlab',
        #         'matplotlib'
        #     ]
        # },
        zip_safe=False,
        platforms="Linux, Mac OS X",
        classifiers=[
            'Operating System :: OS Independent',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'License :: OSI Approved :: Apache Software License',
        ],
        entry_points={
            'console_scripts': [
                'cooka = cooka.cli:main',
            ]
        },
        include_package_data=True,
        package_data={
            'cooka': ['core/train_template/*.jinja2', '*.template', 'assets/*', 'assets/static/*'],  # can not inlcude a directory recursion
        }
    )
