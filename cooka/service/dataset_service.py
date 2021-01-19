import os
import shutil
import time
import pandas as pd
from os import path as P
import sys
import numpy as np
from cooka.dao.dao import DatasetDao, ExperimentDao
from cooka.dao import db
from cooka.dao.entity import DatasetEntity, MessageEntity

from cooka.common import util, consts
from cooka.common.exceptions import EntityNotExistsException, IllegalParamException
from cooka.common.log import log_web as logger
from cooka.common.model import AnalyzeJobConf, AnalyzeStep, JobStep, SampleConf, LocaleInfo, RespPreviewDataset, \
    DatasetStats, FeatureValueCount, FeatureType, FeatureCorrelation


class DatasetService:

    dataset_dao = DatasetDao()
    model_dao = ExperimentDao()

    def add_analyze_process_step(self, dataset_name, analyze_job_name, step: JobStep):
        step_type = step.type
        with db.open_session() as s:
            # 1.1.  check dataset exists
            d = s.query(DatasetEntity).filter(DatasetEntity.name == dataset_name).first()
            if d is None:
                raise EntityNotExistsException(DatasetEntity, dataset_name)
            dataset_file_path = d.file_path
            # 1.2. check event type, one type one record
            messages = s.query(MessageEntity).filter(MessageEntity.author == analyze_job_name).all()
            for m in messages:
                if step_type == util.loads(m.content).get('type'):
                    raise Exception(f"Event type = {step_type} already exists .")

        # 2. handle event
        with db.open_session() as s:
            # 2.1. create a new message
            # add recommend dataset name if analyze succeed
            if step_type == AnalyzeStep.Types.Analyzed and step.status == JobStep.Status.Succeed:
                step.extension['recommend_dataset_name'] = self.choose_dataset_name(P.basename(dataset_file_path), False)

            content = util.dumps(step.to_dict())
            message = MessageEntity(id=util.short_uuid(), author=analyze_job_name, content=content, create_datetime=util.get_now_datetime())
            s.add(message)

            # 2.2. handle analyze event
            if step_type == AnalyzeStep.Types.Analyzed:
                # update temporary dataset
                if step.status == JobStep.Status.Succeed:
                    hints = step.extension.pop("hints")
                    d_stats = DatasetStats.load_dict(step.extension)
                    features_str = [f.to_dict() for f in d_stats.features]
                    update_fields = \
                        {
                            "has_header": d_stats.has_header,
                            "extension": {"sample_conf": step.extension['sample_conf']},  # for sample hint
                            "n_cols": d_stats.n_cols,
                            "n_rows": d_stats.n_rows,
                            "features": features_str,
                            "hints": hints,
                            "feature_summary": d_stats.feature_summary.to_dict(),
                            "status": DatasetEntity.Status.Analyzed
                         }
                else:
                    update_fields = {
                        "status": DatasetEntity.Status.Failed
                    }
                self.dataset_dao.update_by_name(s, dataset_name, update_fields)

            elif step_type == AnalyzeStep.Types.PatchCorrelation:
                # 1. check dataset status, only analyzed can calc relativity
                dataset = self.dataset_dao.require_by_name(s, dataset_name)
                if dataset.status != AnalyzeStep.Types.Analyzed:
                    raise ValueError(f"Dataset {dataset_name} status is not {AnalyzeStep.Types.Analyzed} .")

                request_label_col = step.extension.get("label_col")
                if request_label_col != dataset.label_col:
                    raise ValueError(f"Dataset {dataset_name} label col is {dataset.label_col} but received result is for {request_label_col}")

                # 2. read extension
                corr_dict = step.extension.get('corr')

                # 3. load & update features
                features = dataset.to_dataset_stats().features
                for f in features:
                    correlation = corr_dict.get(f.name)
                    f.correlation = FeatureCorrelation(value=correlation, status=FeatureCorrelation.calc_status(correlation, request_label_col==f.name))

                # 4. sort features by  abs correlation
                def sort_key(f):
                    if f.correlation.value is None:
                        return 0
                    else:
                        return abs(f.correlation.value)

                features = sorted(features, key=sort_key, reverse=True)

                feature_dict_list = []
                for f in features:
                    feature_dict_list.append(f.to_dict())

                # 5. push back database
                self.dataset_dao.update_by_name(s, dataset_name, {"features": feature_dict_list})

    def brevity_dataset_pagination(self, req_dict):
        # 1. read param
        page_num = util.require_in_dict(req_dict, 'page_num', int, default=1)
        page_size = util.require_in_dict(req_dict, 'page_size', int, default=10)
        query = util.get_from_dict(req_dict, 'query', str)
        order_by = util.require_in_dict(req_dict, 'order_by', str, default="create_datetime")
        order = util.require_in_dict(req_dict, 'order', str, default="desc")

        allow_order_by_fields = ["create_datetime", "n_experiments", "size", "n_rows", "n_cols"]
        if order_by not in allow_order_by_fields:
            raise ValueError(f"Order by field should in {','.join(allow_order_by_fields)}, but input is: {order_by}")

        allow_order_strategies = ["desc", "asc"]

        if order not in allow_order_strategies:
            raise ValueError(f"order strategy should in {','.join(allow_order_strategies)}, but input is: {order}")

        if page_num < 1:
            raise ValueError("Param page_num should > 1 .")

        if page_size < 0:
            raise ValueError("Param page_size should > 0 .")

        def _handle(model_dao, session, dataset: DatasetEntity):
            d = util.sqlalchemy_obj_to_dict(dataset)
            d['file_path'] = util.relative_path(dataset.file_path)
            d['create_datetime'] = util.to_timestamp(dataset.create_datetime)
            d['n_experiments'] = model_dao.query_n_experiment(session, dataset.name)

            del d['features']
            del d['feature_summary']
            del d['extension']

            return d

        # 2. query
        with db.open_session() as s:
            datasets, total = self.dataset_dao.pagination(s, page_num, page_size, query, order_by, order)
            datasets = [_handle(self.model_dao, s, d) for d in datasets]
            return datasets, total

    def create_dataset(self, dataset_name, temporary_dataset_name):
        with db.open_session() as s:
            # 1. check temporary dataset
            temporary_dataset = s.query(DatasetEntity).filter(DatasetEntity.name == temporary_dataset_name).first()
            if temporary_dataset is None:
                raise EntityNotExistsException(DatasetEntity, temporary_dataset_name)
            if temporary_dataset.status != DatasetEntity.Status.Analyzed:
                raise IllegalParamException('dataset_name', temporary_dataset_name, f'Dataset is not ready, status is {temporary_dataset.status}')

            # 2. check dataset name
            new_dataset_dir = P.join(consts.PATH_DATASET, dataset_name)
            if P.exists(new_dataset_dir):
                raise IllegalParamException('dataset_name', dataset_name, f'File path {new_dataset_dir} of dataset already exits')

            # 3. Read temporary dataset
            # temporary_dataset_dict = util.loads(temporary_dataset.extension)

            # 4. make dataset dir, can not rollback, but should enough robust below
            new_dataset_dir = P.join(consts.PATH_DATASET, dataset_name)
            os.makedirs(new_dataset_dir, exist_ok=False)

            # 5. move file
            file_path = temporary_dataset.get_abs_file_path()
            new_dataset_file_path = P.join(new_dataset_dir, f'data{util.get_file_suffix(file_path)}')
            shutil.copy(file_path, new_dataset_file_path)

            # 6. create meta.json
            # temporary_dataset_dict['name'] = dataset_name
            # temporary_dataset_dict['create_datetime'] = util.get_now_long()
            # with open(P.join(new_dataset_dir, 'meta.json'), 'w') as f:
            #     f.write(util.dumps(temporary_dataset_dict))
            properties = {"is_temporary": False,
                          "name": dataset_name,
                          "file_path": new_dataset_file_path}

            # 7. change status
            affect_rows = s.query(DatasetEntity).filter(DatasetEntity.name == temporary_dataset_name, DatasetEntity.is_temporary == True).update(properties)
            if affect_rows != 1:
                raise Exception("Update dataset failed.")

    def retrieve(self, dataset_name, n_top_value):
        with db.open_session() as s:
            dataset = self.dataset_dao.require_by_name(s, dataset_name)
            dict_value = util.sqlalchemy_obj_to_dict(dataset)
            dict_value['file_path'] = util.relative_path(dataset.file_path)
            # if dataset.status == DatasetEntity.Status.Analyzed:
            #     for i, f in enumerate(dict_value['features']):
            #         if f['type'] in [FeatureType.Categorical, FeatureType.Continuous]:
            #             if f['unique']['value'] > n_top_value:
            #                 # calc top {n_count_value}
            #                 extension = f['extension']
            #                 sorted(extension['value_count'], key=lambda _: _['value'])
            #
            #                 top_value_count = extension['value_count'][: n_top_value]
            #                 remain_value_count = extension['value_count'][n_top_value:]
            #                 remain_count = 0
            #                 for remain_dict in remain_value_count:
            #                     remain_count = remain_count + remain_dict['value']
            #
            #                 top_value_count.append(
            #                     FeatureValueCount(type="Remained_SUM", value=remain_count).to_dict()
            #                 )
            #                 dict_value['features'][i]['extension']['value_count'] = top_value_count
                            # extension['value_count'] = top_value_count

            # dict_value['detail'] = dict_value['extension']
            extension = dict_value.pop('extension')
            dict_value['extension'] = {"sample_conf": extension['sample_conf']}
            return dict_value

    def delete(self, dataset_name):
        with db.open_session() as s:
            # 1. delete record
            dataset = self.dataset_dao.require_by_name(s, dataset_name)
            is_temporary = dataset.is_temporary
            self.dataset_dao.delete(s, dataset_name)

            # 2. delete file only not temporary
            if is_temporary is False:
                if "/" not in dataset_name and len(dataset_name) > 1:
                    if len(consts.PATH_DATASET) > 1:
                        dataset_dir = P.join(consts.PATH_DATASET, dataset_name)
                        if P.exists(dataset_dir) and P.isdir(dataset_dir):
                            logger.info(f"Remove file at: {dataset_dir}")
                            shutil.rmtree(dataset_dir)
                        else:
                            raise ValueError(f"dataset dir {dataset_dir} is not dir or not exists, may be a bug here.")
                    else:
                        raise ValueError("Data dir too short, can not delete. ")
                else:
                    raise ValueError("dataset name contains '/' or length too short.")

    def create_temporary_dataset(self, req_dict):
        sample_strategy = util.require_in_dict(req_dict, 'sample_strategy', str, 'random_rows')
        if SampleConf.Strategy.Percentage == sample_strategy:
            percentage = util.get_from_dict(req_dict, 'percentage', int, 30)
            n_rows = None
        elif SampleConf.Strategy.RandomRows == sample_strategy:
            n_rows = util.get_from_dict(req_dict, 'n_rows', int, 1000)
            percentage = None
        elif SampleConf.Strategy.WholeData == sample_strategy:
            n_rows = None
            percentage = None
        else:
            raise ValueError(f"Not support sample strategy: {sample_strategy}")

        upload_took = util.require_in_dict(req_dict, 'upload_took', float)

        file_path = util.require_in_dict(req_dict, 'file_path', str)
        source_type = util.require_in_dict(req_dict, 'source_type', str)

        sample_conf = SampleConf(sample_strategy=sample_strategy, percentage=percentage, n_rows=n_rows)

        # 1. validate param
        if source_type not in [DatasetEntity.SourceType.Upload, DatasetEntity.SourceType.Import]:
            raise IllegalParamException('source_type', source_type, f'Should in {",".join([DatasetEntity.SourceType.Upload, DatasetEntity.SourceType.Import])}')

        if source_type == DatasetEntity.SourceType.Upload:
            upload_file_prefix = P.join(consts.FIELD_TMP, consts.FIELD_UPLOAD)
            if not file_path.startswith(upload_file_prefix):
                raise ValueError(f"For upload file should path should start with {upload_file_prefix} but it's {file_path}")
            else:
                # fix relative path
                file_path = P.join(consts.DATA_DIR, file_path)

        if not P.exists(file_path):
            raise ValueError(f"File={file_path} not exists")

        if not P.isfile(file_path):
            raise ValueError(f"File={file_path} is not a file")

        util.validate_sample_conf(sample_conf)

        # 2. create
        if source_type == DatasetEntity.SourceType.Upload:
            return self._create_temporary_dataset(source_type, file_path, upload_took, sample_conf)
        elif source_type == DatasetEntity.SourceType.Import:
            t1 = time.time()
            internal_path = util.temporary_upload_file_path(P.basename(file_path))
            os.makedirs(P.dirname(internal_path), exist_ok=True)
            shutil.copy(file_path, internal_path)
            took = time.time() - t1
            logger.info(f"Copy file to {internal_path}")
            return self._create_temporary_dataset(source_type, internal_path, took, sample_conf)
        else:
            raise IllegalParamException('source_type', source_type, f'should one of {",".join([DatasetEntity.SourceType.Upload, DatasetEntity.SourceType.Import])}')

    def is_dataset_exists(self, dataset_name):
        with db.open_session() as s:
            d = self.dataset_dao.find_by_name(s, dataset_name)
            exists_in_db = d is not None
            exists_file = P.exists(P.join(consts.PATH_DATABASE, dataset_name))
            return exists_in_db or exists_file

    def choose_dataset_name(self, file_name, is_temporary):
        # 1. cut suffix
        file_name = util.cut_suffix(file_name)

        if is_temporary is True:
            prefix = "temporary_"
        else:
            prefix = ''

        # 2. try 1000 times use num name
        for i in range(1000):
            if i == 0:
                candidate_name = file_name
            else:
                candidate_name = f"{prefix}{file_name}_{i}"
            if not self.is_dataset_exists(candidate_name):
                return candidate_name
        # 3. if a file has over 1000 dataset, use timestamp named
        return f'{prefix}{file_name}_{util.human_datetime()}'

    @staticmethod
    def replace_None(s):
        if s is None:
            return ""
        else:
            return s

    def _create_temporary_dataset(self, source_type, file_path, took, sample_conf: SampleConf):
        now = util.get_now_datetime()
        file_name = P.basename(file_path)
        temporary_dataset_name = self.choose_dataset_name(file_name, True)  # use a long name
        analyze_job_name = util.analyze_data_job_name(util.cut_suffix(file_name), now)
        file_size = P.getsize(file_path)

        # 2. create record
        td = DatasetEntity(name=temporary_dataset_name,
                           file_size=file_size,
                           is_temporary=True,
                           status=DatasetEntity.Status.Created,
                           source_type=source_type,
                           file_path=file_path,
                           create_datetime=now, last_update_datetime=now)
        with db.open_session() as s:
            s.add(td)

        # 3. send  file transfer step
        if source_type == DatasetEntity.SourceType.Upload:
            step = JobStep(type=AnalyzeStep.Types.Upload,
                           status=AnalyzeStep.Status.Succeed,
                           extension={"file_size": file_size, "file_path": file_path},
                           took=took, datetime=util.get_now_long())
            self.add_analyze_process_step(temporary_dataset_name, analyze_job_name, step)
        elif source_type == DatasetEntity.SourceType.Import:
            step = JobStep(type=AnalyzeStep.Types.Copy,
                           status=AnalyzeStep.Status.Succeed,
                           extension={"file_size": file_size,
                                      "file_path": file_path},
                           took=took,
                           datetime=util.get_now_long())
            self.add_analyze_process_step(temporary_dataset_name, analyze_job_name, step)

        # 4. create analyze config
        conf = AnalyzeJobConf(job_name=analyze_job_name,
                              dataset_name=temporary_dataset_name,
                              sample_conf=sample_conf,
                              path=file_path,
                              temporary_dataset=True,
                              label_col=None)

        # 5. start new process
        analyze_config_string = util.dumps(conf.to_dict())
        logger.info(f"Analyze job conf: {analyze_config_string}")

        python_executable = sys.executable

        temporary_dataset_dir = util.temporary_dataset_dir(temporary_dataset_name)

        os.makedirs(temporary_dataset_dir, exist_ok=True)

        std_log = P.join(temporary_dataset_dir, f"{analyze_job_name}.log")

        command = f"nohup {python_executable} {util.script_path('analyze_job.py')} --file_path={file_path} --job_name={analyze_job_name} --dataset_name={temporary_dataset_name} --sample_strategy={sample_conf.sample_strategy} --n_rows={self.replace_None(sample_conf.n_rows)} --percentage={self.replace_None(sample_conf.percentage)} --server_portal={consts.SERVER_PORTAL} 1>{std_log} 2>&1 &"

        logger.info(f"Run analyze job command: \n{command}")
        logger.info(f"Log file:\ntail -f {std_log}")

        # JobManager.instance().run_job(job)
        os.system(command)  # ha ha ha

        return temporary_dataset_name, analyze_job_name

    def preview(self, dataset_name: str, page_num: int, page_size: int) -> RespPreviewDataset:
        """
        Args:
            dataset_name:
            page_num: start from 1
            page_size:

        Returns:

        """
        # 1. validation params
        if page_num < 1:
            raise ValueError("Param page_num should >= 1'")

        if page_size < 1:
            raise ValueError("Param page_size should >= 1'")

        # 2. retrieve dataset
        with db.open_session() as s:
            dataset = self.dataset_dao.require_by_name(s, dataset_name)
            file_path = dataset.file_path
            if not P.exists(file_path):
                raise FileNotFoundError(file_path)
            dataset_stats = dataset.to_dataset_stats()

        relative_file_path = util.relative_path(dataset_stats.file_path)

        # 3. read data
        dataset_headers = [f.name for f in dataset_stats.features]
        dataset_headers.insert(0, "No. ")
        # dataset_headers.insert(0, "number")
        if dataset_stats.has_header:
            iterator_df = pd.read_csv(file_path, chunksize=page_size)
        else:
            iterator_df = pd.read_csv(file_path, chunksize=page_size, header=None)

        # 4. seek pages, page num start from 1
        # e.g. if page_num = 1 while loop will do 0 times, below code will invoke next(iterator_df) and get data
        current_page = 1
        while current_page < page_num:
            try:
                next(iterator_df)  # no Reference, will be gc
                current_page = current_page + 1
            except StopIteration:
                # if page_num is too large , no data returned
                return RespPreviewDataset(headers=dataset_headers, rows=None, count=dataset_stats.n_rows, file_path=relative_file_path)

        # 5. hit data
        try:
            page_df: pd.DataFrame = next(iterator_df)
            # 5.1. make index
            start_line_no = (current_page - 1) * page_size + 1  # start from 1
            df_index = page_df.index = pd.RangeIndex(start_line_no, start_line_no + page_df.shape[0])
            page_df.index = df_index

            # 5.2. replace NaN to null
            page_df.replace(np.NaN, 'NULL', inplace=True)
            # fixme orgin data can not has column named index nor cause a error "ValueError: name already used as a name or title"
            values = page_df.to_records(index=True).tolist()

            return RespPreviewDataset(headers=dataset_headers, rows=values, count=dataset_stats.n_rows, file_path=relative_file_path)
        except StopIteration:
            return RespPreviewDataset(headers=dataset_headers, rows=None, count=dataset_stats.n_rows, file_path=relative_file_path)
