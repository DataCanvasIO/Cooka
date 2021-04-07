# -*- encoding: utf-8 -*-
import json
import tornado

from tornado.web import Finish, HTTPError
import codecs

from cooka.common.model import RestResponse, ResponseCode, ErrorResponse, LocaleInfo
from cooka.common.log import log_web as logger
from typing import Any


from cooka.common import consts
from cooka.common.exceptions import ServiceException


class BaseHandler(tornado.web.RequestHandler):

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        """ Follow https://www.tornadoweb.org/en/stable/guide/structure.html make a BaseHandler to handle Exception.

        Args:
            status_code:
            **kwargs:

        Returns:

        Known Issues:
            1. Can not handle error requests that in `initialize` stage .

        """
        exc_info = kwargs.get('exc_info')
        http_code = 200
        if exc_info is not None:
            exception_class, exception, trace = exc_info
            logger.exception(exception)

            if isinstance(exception, AssertionError):
                service_exception = ServiceException(consts.CODE_ASSERTION_ERROR, exc_info[1].args[0], exc_info)

            elif isinstance(exception, ServiceException):
                service_exception = exception
            elif isinstance(exception, HTTPError):
                service_exception = ServiceException(consts.CODE_HTTP_ERROR, f"status={exception.status_code}", exception)
                http_code = exception.status_code
            else:
                service_exception = ServiceException(consts.CODE_OTHER, exception.args[0], exception)

            response = ErrorResponse(service_exception.code, service_exception.hint)
        else:
            logger.exception(Exception("Unknown exception"))
            response = ErrorResponse(ResponseCode.Exception, str("Unknown exception."))

        self.set_header('Content-Type', 'application/json')
        # handled
        self.set_status(http_code)
        if http_code == 401:
            self.set_header('WWW-Authenticate', 'Basic realm="%s"' % "admin")

        self.finish(response.to_json())

    @staticmethod
    def detect_encoding(b):
        bstartswith = b.startswith
        if bstartswith((codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE)):
            return 'utf-32'
        if bstartswith((codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE)):
            return 'utf-16'
        if bstartswith(codecs.BOM_UTF8):
            return 'utf-8-sig'

        if len(b) >= 4:
            if not b[0]:
                # 00 00 -- -- - utf-32-be
                # 00 XX -- -- - utf-16-be
                return 'utf-16-be' if b[1] else 'utf-32-be'
            if not b[1]:
                # XX 00 00 00 - utf-32-le
                # XX 00 00 XX - utf-16-le
                # XX 00 XX -- - utf-16-le
                return 'utf-16-le' if b[2] or b[3] else 'utf-32-le'
        elif len(b) == 2:
            if not b[0]:
                # 00 XX - utf-16-be
                return 'utf-16-be'
            if not b[1]:
                # XX 00 - utf-16-le
                return 'utf-16-le'
        # default
        return 'utf-8'

    def response_json(self, data: dict):
        rest_result = RestResponse(ResponseCode.Success, data)
        self.set_header("Content-Type", "application/json")
        self.write(rest_result.to_json())

    def decode_bytes(self, b):
        return b.decode(self.detect_encoding(b), 'surrogatepass')

    def get_request_as_dict_if_json(self):
        # todo check body is not json format
        body = self.request.body
        # compatible for py35/36
        try:
            body = body.decode(self.detect_encoding(body), 'surrogatepass')
        except Exception:
            body = body.decode('GBK', 'surrogatepass')
        logger.info("Request body:\n%s" % body)

        return json.loads(body)


    def get_query_args(self):
        args = {}
        for k in self.request.arguments:  # fix values
            args[k] = self.get_argument(k)
        return args

    def get_locale_info(self):
        return LocaleInfo(lang=self.request.headers.get('LANG', LocaleInfo.Types.English))
