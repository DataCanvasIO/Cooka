FROM  ubuntu:18.04

USER root

ENV LANG C.UTF-8

RUN sed -i "s/archive.ubuntu.com/mirrors.aliyun.com/g" /etc/apt/sources.list\
     && sed -i "s/security.ubuntu.com/mirrors.aliyun.com/g" /etc/apt/sources.list

RUN mkdir -p /root/.pip \
    && echo "[global]\n\
index-url = https://mirrors.aliyun.com/pypi/simple" > /root/.pip/pip.conf

# for install shap
RUN echo "[easy_install]\n\
index_url = https://mirrors.aliyun.com/pypi/simple" > /root/.pydistutils.cfg

RUN apt-get update \
     && apt-get install -y language-pack-zh-hans  python3 python3-pip\
     && apt-get clean \
     && pip3 install --upgrade pip setuptools

# only need if install notebook
RUN apt-get install -y gcc g++ make clang-10 python3-clang-10

RUN pip3 install -i http://172.20.10.193:8081/repository/zetyun-pypi-group/simple --trusted-host 172.20.10.193 cooka[notebook]

COPY entrypoint.sh /

RUN chmod +x /entrypoint.sh

ENTRYPOINT /entrypoint.sh
