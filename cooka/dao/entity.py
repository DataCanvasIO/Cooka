# -*- encoding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, JSON

from cooka.common.model import Model, Performance, TrainTrail, DatasetStats, Feature
from cooka.dao.db import Base
from cooka.common.model import ModelFeature
from deeptables.models.deepmodel import IgnoreCaseDict
from cooka.common import consts
from os import path as P

class Process(Base):
    __tablename__ = 'cd_process'

    id = Column(String, primary_key=True, )
    command = Column(String(4096))
    logfile = Column(String(4096), nullable=True)
    status = Column(String(128))
    pid = Column(Integer(), nullable=True)  # has no pid before started
    create_datetime = Column(DateTime())
    last_update_datetime = Column(DateTime(), nullable=True)
    message = Column(Text(), nullable=True)  # update

    returncode = Column(Integer(), nullable=True)  # update
    duration = Column(Float(), nullable=True)  # update

    class Status:
        Ready = 'ready'
        Running = 'running'
        Finished = 'finished'


class MessageEntity(Base):
    __tablename__ = 'cd_message'
    id = Column(String(16), primary_key=True )
    author = Column(String(128))
    content = Column(Text(), nullable=True)
    create_datetime = Column(DateTime())


class DatasetEntity(Base):
    __tablename__ = 'cd_dataset'
    # note: Two key as primary
    name = Column(String(128), primary_key=True)
    is_temporary = Column(Boolean(), primary_key=True)

    label_col = Column(String(128), nullable=True)
    status = Column(String(128))
    file_size = Column(Integer())
    n_rows = Column(Integer(), nullable=True)
    n_cols = Column(Integer(), nullable=True)
    has_header = Column(Boolean(), nullable=True)
    features = Column(JSON(), nullable=True)
    hints = Column(JSON(), nullable=True)
    feature_summary = Column(JSON(), nullable=True)
    source_type = Column(String(128))
    file_path = Column(String(4096))
    file_name = Column(String(4096))
    extension = Column(JSON(), nullable=True)  # update result
    create_datetime = Column(DateTime())
    last_update_datetime = Column(DateTime())

    class Status:
        Created = 'created'  # init
        # Uploaded = 'uploaded'  # has a file uploaded
        Analyzed = 'analyzed'
        Failed = 'failed'

    class SourceType:
        Upload = 'upload'
        Import = 'import'

    def get_abs_file_path(self):
        if self.source_type == DatasetEntity.SourceType.Upload:
            return P.join(consts.DATA_DIR, self.file_path)
        else:
            return self.file_path

    def to_dataset_stats(self):
        return \
            DatasetStats(label_col=self.label_col,
                         file_path=self.file_path,
                         has_header=self.has_header,
                         n_rows=self.n_rows,
                         n_cols=self.n_cols,
                         features=Feature.load_dict_list(self.features),
                         feature_summary=self.feature_summary,
                         create_datetime=self.create_datetime)


class ModelEntity(Base):
    __tablename__ = 'cd_model'
    # note: Two key as primary
    name = Column(String(128), primary_key=True)
    dataset_name = Column(String(128))

    no_experiment = Column(Integer())
    framework = Column(String(128))

    model_file_size = Column(Integer(), nullable=True)

    inputs = Column(JSON())
    task_type = Column(String(128))
    performance = Column(JSON(128), nullable=True)
    model_path = Column(String(128), nullable=True)
    status = Column(String(128))
    pid = Column(Integer(), nullable=True)
    score = Column(Float(), nullable=True)
    progress = Column(String(128))
    train_job_name = Column(String(128))
    train_trail_no = Column(Integer(), nullable=True)
    trails = Column(JSON(), nullable=True)
    extension = Column(JSON(), nullable=True)  # update
    create_datetime = Column(DateTime())
    finish_datetime = Column(DateTime(), nullable=True)
    last_update_datetime = Column(DateTime())

    def to_model_bean(self):
        # Just run in session scope
        performance = Performance.load_dict(self.performance)
        # if performance is not None:
        #     metrics = performance.metrics
        #     if metrics is not None:
        #         performance.metrics = IgnoreCaseDict(metrics)

        m = \
            Model(name=self.name, framework=self.framework, dataset_name=self.dataset_name, no_experiment=self.no_experiment,
                  model_file_size=self.model_file_size, inputs=ModelFeature.load_dict_list(self.inputs),
                  task_type=self.task_type, performance=performance,
                  model_path=self.model_path, score=self.score, status=self.status, pid=self.pid,
                  progress=self.progress, train_job_name=self.train_job_name,
                  train_trail_no=self.train_trail_no, trails=TrainTrail.load_dict_list(self.trails), extension=self.extension,
                  create_datetime=self.create_datetime, finish_datetime=self.finish_datetime, last_update_datetime=self.last_update_datetime)
        return m


def initialize_database():
    from cooka.dao import db
    Base.metadata.create_all(db.engine, checkfirst=True)


if __name__ == '__main__':
    # !! Re Build DB dost not support update schema
    initialize_database()

