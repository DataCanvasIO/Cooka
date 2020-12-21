# -*- encoding: utf-8 -*-

from jinja2.loaders import FileSystemLoader
from jinja2 import Environment

p = '/Users/wuhf/PycharmProjects/cooka/cooka/test/main.jinja2'

with open(p, 'r') as f:
    rtemplate = Environment(loader=FileSystemLoader("/Users/wuhf/PycharmProjects/cooka/cooka/test")).from_string(f.read())
    data = rtemplate.render({})
    print(data)
