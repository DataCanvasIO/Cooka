# -*- encoding: utf-8 -*-

from tornado import gen

from cooka.common.authentication import authenticated
from cooka.handler.base_handler import BaseHandler
from cooka.common import consts
import requests, json


class ConfigHandler(BaseHandler):

    @gen.coroutine
    @authenticated
    def get(self, *args, **kwargs):
        response = {
            "LANG": consts.LANG,
        }
        self.response_json(response)
