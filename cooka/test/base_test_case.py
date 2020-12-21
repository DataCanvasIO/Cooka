# -*- encoding: utf-8 -*-
import mimetypes

from tornado.testing import AsyncHTTPTestCase

from cooka.common import util
from os import path as P
import time

from cooka.common.model import AnalyzeStep
from cooka.dao import db
from cooka.dao.entity import DatasetEntity
from cooka.server import make_app
from tornado import gen
from functools import partial
import uuid
from os import path as P
from cooka.common.consts import PATH_INSTALL_HOME


class BaseTestCase(AsyncHTTPTestCase):

    DEFAULT_HEADER = {"Content-Type": "application/json"}

    def get_app(self):
        return make_app()

    def assert_response_and_get(self, response):
        self.assertEqual(response.code, 200)
        response_body = util.loads(response.body)
        assert response_body['code'] == 0
        return response_body['data']


class WithTemporaryDatasetTestCase(BaseTestCase):

    @gen.coroutine
    def multipart_producer(self, boundary, filepath, write):
        boundary_bytes = boundary.encode()
        filename = P.basename(filepath)

        filename_bytes = filename.encode()
        mtype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        buf = (
                (b"--%s\r\n" % boundary_bytes)
                + (
                        b'Content-Disposition: form-data; name="file"; filename="%s"\r\n'
                        % (filename_bytes)
                )
                + (b"Content-Type: %s\r\n" % mtype.encode())
                + b"\r\n"
        )
        yield write(buf)
        with open(filepath, "rb") as f:
            while True:
                # 16k at a time.
                chunk = f.read(16 * 1024)
                if not chunk:
                    break
                yield write(chunk)

        yield write(b"\r\n")

        yield write(b"--%s--\r\n" % (boundary_bytes,))

    def create_temporary_dataset(self) -> str:
        data_path = P.join(PATH_INSTALL_HOME, "cooka/test/dataset/diabetes_10k_datetime.csv")
        return self.create_temporary_dataset_from_file(data_path)

    def create_temporary_dataset_from_file(self, data_path):
        """This can not in setup_class(cls) nor setUpClass(cls), setUp, because http server not ready.
        """
        super(WithTemporaryDatasetTestCase, self).setUp()  # must invoke or not create http server
        from cooka.common import consts
        consts.SERVER_PORTAL = self.get_url('')  # use temporary server

        # 1. upload
        boundary = uuid.uuid4().hex
        headers = {"Content-Type": "multipart/form-data; boundary=%s" % boundary}
        producer = partial(self.multipart_producer, boundary, data_path)

        upload_response = self.fetch(path='/api/resource', method="POST", body_producer=producer, headers=headers)

        upload_response_body = self.assert_response_and_get(upload_response)
        upload_file_path = upload_response_body.get('path')
        upload_took = upload_response_body.get('took')

        assert upload_file_path is not None
        assert upload_took is not None

        # 2. send request
        body = {
            "sample_strategy": "random_rows",
            "percentage": 30,
            "n_rows": 1000,
            "file_path": upload_file_path,
            "upload_took": upload_took,
            "source_type": "upload",
        }
        str_body = util.dumps(body)

        # 3. validate code
        create_response_body = self.assert_response_and_get(self.fetch(path='/api/temporary-dataset', method="POST", body=str_body, headers=headers))
        print(f"create response body:\n {create_response_body}")

        # 3. poll dataset message
        temporary_dataset_name = create_response_body["temporary_dataset_name"]
        analyze_job_name = create_response_body["analyze_job_name"]

        excepted_event = [AnalyzeStep.Types.Upload, AnalyzeStep.Types.Load, AnalyzeStep.Types.Analyzed]

        analyze_passed = False
        poll_job_response_body = None
        for i in range(10):  # poll for 30 times every time one second
            poll_job_response = self.fetch(f'/api/dataset/{temporary_dataset_name}/analyze-job/{analyze_job_name}', method="GET")
            poll_job_response_body = self.assert_response_and_get(poll_job_response)
            events = poll_job_response_body['steps']
            events.sort(key=lambda x: x['datetime'])
            events_type = [event["type"] for event in events]
            if excepted_event == events_type:  # has all excepted type order by datetime
                # validate every
                analyze_passed = True
                break

            if AnalyzeStep.Types.End in events_type:
                break

            time.sleep(1)

        assert analyze_passed, f"{poll_job_response_body}"

        # 4. retrieve dataset and check detail
        with db.open_session() as s:
            temporary_dataset = s.query(DatasetEntity).filter(DatasetEntity.name == temporary_dataset_name).first()
            assert temporary_dataset is not None, f'Temporary dataset = {temporary_dataset_name} create failed'

            assert len(temporary_dataset.extension) > 0
            assert temporary_dataset.status == DatasetEntity.Status.Analyzed

        return temporary_dataset_name
