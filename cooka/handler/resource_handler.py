# -*- encoding: utf-8 -*-
from cooka.common import util
from cooka.common.authentication import authenticated
from cooka.common.exceptions import MissingParamException
from cooka.common.log import log_web as logger

from cooka.handler.base_handler import BaseHandler
from tornado import gen
from os import path as P
from cooka.common import consts
import tornado.web
import os
import time
from tornado.web import StaticFileHandler
from tornado import httputil


class AbstractTextResourceHandler(BaseHandler):

    @authenticated
    @gen.coroutine
    def get(self, path, *args, **kwargs):
        # 1. validate param
        args = self.get_query_args()
        n = util.require_in_dict(args, 'n', int, 100)
        opt = util.require_in_dict(args, 'opt', str, 'download')

        if opt not in ["head", "download"]:
            raise ValueError(f"Not support operation: {opt}")

        abs_path = P.join(consts.DATA_DIR, path)
        if not P.exists(abs_path):
            raise FileExistsError(abs_path)

        if not P.isfile(abs_path):
            raise ValueError(f"Not a file: {abs_path}")

        if opt == "download":
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=%s' % P.basename(abs_path))
            with open( abs_path, 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    self.write(data)
        elif opt == "head":
            # 2. read and write
            self.write("<pre>")
            for l in self.read_lines(abs_path, n):
                self.write(l)
            self.finish("</pre>")

    def read_lines(self, path, n):
        raise NotImplemented


class TextResourceHeadHandler(AbstractTextResourceHandler):

    def read_lines(self, path, n):
        with open(path, 'r') as f:
            point = 0
            while n == -1 or point < n:
                try:
                    l = next(f)
                    yield l
                    point = point + 1
                except StopIteration:
                    break


def handle_tornado_upload_file(http_handler, tornado_http_files, upload_start_time):
    # 1. check and read param
    tornado_http_file = tornado_http_files.get("file")[0]

    if tornado_http_file is None:
        raise MissingParamException("file")

    file_name = tornado_http_file['filename']
    file_body = tornado_http_file['body']
    file_size = util.human_data_size(len(file_body))
    file_suffix = util.get_file_suffix(file_name)

    assert file_suffix in ['.csv', '.tsv'], 'Please check is your file suffix in [.csv, .tsv], current is: %s' % file_suffix

    origin_file_name = util.make_dataset_name(util.cut_suffix(file_name)) + file_suffix  # for it in url, disk path readable

    # 2. open temporary file and  write to local file
    temporary_file_path = util.temporary_upload_file_path(origin_file_name)

    if not P.exists(P.dirname(temporary_file_path)):
        os.makedirs(P.dirname(temporary_file_path))

    logger.info(f"Open path {temporary_file_path} to store upload file.")

    with open(temporary_file_path, 'wb') as f:
        f.write(file_body)
    logger.info(f"Uploaded file finished at {temporary_file_path}, file size {file_size} .")

    upload_took = util.time_diff(time.time(), upload_start_time)

    # 3. response
    # relative_path = temporary_file_path[len(consts.PATH_DATA_ROOT)+1:]  # relative path not start with /
    response = \
        {
            "path": util.relative_path(P.abspath(temporary_file_path)),
            "size": file_size,
            "took": upload_took
        }
    http_handler.response_json(response)


class ResourceHandler(BaseHandler):
    def prepare(self):
        self.t1 = time.time()

    @gen.coroutine
    def post(self, *args, **kwargs):
        handle_tornado_upload_file(self, self.request.files, time.time())  # may inaccurate time use  StreamResourceHandler instead


@tornado.web.stream_request_body
class StreamResourceHandler(BaseHandler):

    def prepare(self):
        # open temporary file
        self.temporary_file_path = util.temporary_upload_file_path('upload_chunk')
        if not P.exists(P.dirname(self.temporary_file_path)):
            os.makedirs(P.dirname(self.temporary_file_path))

        self.temporary_file = open(self.temporary_file_path, 'wb')  # todo limit max length of file
        logger.info(f"Open path {self.temporary_file_path} to store upload file.")
        self.start_time = time.time()
        self.writed_size = 0

    def data_received(self, chunk):
        self.temporary_file.write(chunk)
        self.writed_size = self.writed_size + len(chunk)
        del chunk  # free mem

    @gen.coroutine
    @authenticated
    def post(self, *args, **kwargs):
        # 1. close file
        file_size = util.human_data_size(self.writed_size)
        logger.info(f"Uploaded file finished at {self.temporary_file_path}, file size {file_size} .")
        if self.temporary_file is not None:
            self.temporary_file.flush()
            self.temporary_file.close()

        content_type = self.request.headers['Content-Type']
        with open(self.temporary_file_path, 'rb') as f:
            fields = content_type.split(";")
            for field in fields:
                k, sep, v = field.strip().partition("=")
                if k == "boundary" and v:
                    from tornado.escape import utf8
                    files = {}
                    httputil.parse_multipart_form_data(utf8(v), f.read(), {}, files)
                    handle_tornado_upload_file(self, files, self.start_time)
                    return
        raise Exception("Handle upload failed.")


class TextResourceTailHandler(AbstractTextResourceHandler):

    def read_lines(self, path, n):
        return util.tail(path, n)


class AssetsHandler(StaticFileHandler):

    MissingResource = ['favicon.ico']

    async def get(self, path, **kwargs):

        if path in self.MissingResource:
            raise tornado.web.HTTPError(404, f"File {path} is missing")

        if path in ['', '/']:
            resource_path = "index.html"
        else:
            absolute_path = self.get_absolute_path(self.root, self.parse_url_path(path))
            if not P.exists(absolute_path):
                logger.info(f"URI {path} not found, use index.html instead ")
                resource_path = "index.html"  # handle 404
            else:
                resource_path = path
        await super(AssetsHandler, self).get(resource_path)
