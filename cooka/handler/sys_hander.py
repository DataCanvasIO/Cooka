# -*- encoding: utf-8 -*-

from tornado import gen

from cooka.handler.base_handler import BaseHandler
from cooka.common import consts


class ConfigHandler(BaseHandler):

    @gen.coroutine
    def get(self, *args, **kwargs):
        response = {
            "LANG": consts.LANG,
        }
        self.response_json(response)
