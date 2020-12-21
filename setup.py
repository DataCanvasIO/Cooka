#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="cooka",
    # cmdclass=cmdclass,
    version="1.0.0",
    description="An lightweight automatic machine learning product based on neural network architecture search(Hypernet).",
    packages=find_packages(exclude=["test.*", "test"]),
    author="DataCanvas",
    author_email="wuhf@zetyun.com",
    install_requires=[
        'numpy',
        'pandas',
        'scikit-learn>=0.22.1',
        'requests==2.24.0',
        'SQLAlchemy==1.3.18',
        'tornado==6.0.4',
        'jinja2',
        'deeptables',
        'hypergbm',
        'jupyterlab',
        'tabular-toolbox',  # todo remove if hypergbm installed
        'shap'  # todo remove shap if deeptable add
    ],
    extras_require={
    },
    zip_safe=False,
    platforms="Linux, Mac OS X, Windows",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ],
    entry_points={
        'console_scripts': [
            'cooka-server = cooka.server:start_server',
        ]
    },
    package_data={
        'cooka': ['core/train_template/*.jinja2', 'assets/*'],
    }
)
