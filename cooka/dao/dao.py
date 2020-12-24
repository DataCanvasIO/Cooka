# -*- encoding: utf-8 -*-
from cooka.common import util
from cooka.common.exceptions import EntityNotExistsException
from cooka.common.model import Model, ModelStatusType
from cooka.dao.entity import ExperimentEntity, DatasetEntity
from sqlalchemy.sql import func


class BaseDao:

    def require_one(self, items, entity_name):
        one = self.checkout_one(items)
        if one is None:
            raise ValueError(f"Entity name = {entity_name} does not exists in db.")
        else:
            return one

    def checkout_one(self, list_result):
        if list_result is None:
            return None
        else:
            if len(list_result) > 0:
                return list_result[0]
            else:
                return None


class ExperimentDao(BaseDao):

    def find_by_name(self, session, model_name) -> ExperimentEntity:
        model = session.query(ExperimentEntity).filter(ExperimentEntity.name == model_name).all()
        return self.require_one(model, model_name)

    def require_by_name(self, s, model_name):
        model = self.find_by_name(s, model_name)
        if model is None:
            raise EntityNotExistsException(Model, model_name)
        return model

    def find_by_dataset_name(self, session, dataset_name, page_num, page_size):
        offset = (page_num - 1) * page_size
        query = session\
            .query(ExperimentEntity)\
            .filter(ExperimentEntity.dataset_name == dataset_name)
        total = query.count()
        models = query.order_by(ExperimentEntity.create_datetime.desc()) \
            .limit(page_size).offset(offset).all()

        return [m.to_model_bean() for m in models], total

    def find_running_model(self, session):
        models = session \
            .query(ExperimentEntity) \
            .filter(ExperimentEntity.status == ModelStatusType.Running) \
            .order_by(ExperimentEntity.create_datetime.desc()) \
            .all()
        return [m.to_model_bean() for m in models]

    def update_model_by_name(self, session, model_name, properties):
        n_affect = session \
            .query(ExperimentEntity) \
            .filter(ExperimentEntity.name == model_name) \
            .update(properties)
        if n_affect != 1:
            raise Exception(f"Update model = {model_name} status failed, affect rows = {n_affect}, properties = {properties}")

    def find_by_train_job_name(self, session, train_job_name):
        models = session.query(ExperimentEntity).filter(ExperimentEntity.train_job_name == train_job_name).all()
        one = self.checkout_one(models)

        if one is None:
            raise ValueError(f"No model of train job name = {train_job_name}")
        return one

    def get_max_experiment(self,session, dataset_name):
        no_experiment = session.query(func.max(ExperimentEntity.no_experiment)).filter(ExperimentEntity.dataset_name == dataset_name).one_or_none()[0]
        if no_experiment is None:
            return 0  # start from 1
        else:
            return no_experiment

    def query_n_experiment(self, session, dataset_name):
        sql = f"select count(distinct(no_experiment)) from {ExperimentEntity.__tablename__} where dataset_name = '{dataset_name}'"
        return session.execute(sql).fetchone()[0]


class DatasetDao(BaseDao):

    def require_by_name(self, session, dataset_name) -> DatasetEntity:
        d = self.find_by_name(session, dataset_name)
        if d is None:
            raise ValueError(f"Dataset name = {dataset_name} does not exists in db.")
        else:
            return d

    def find_by_name(self, session, dataset_name) -> DatasetEntity:
        list_result = session.query(DatasetEntity).filter(DatasetEntity.name == dataset_name).all()
        return self.checkout_one(list_result)

    def pagination(self, session, page_num, page_size, query_key, order_by, order):
        # !! is False can not use
        query = session.query(DatasetEntity).filter(DatasetEntity.is_temporary == False).filter(DatasetEntity.status == DatasetEntity.Status.Analyzed)

        # page_num should > 1
        if query_key is not None and len(query_key) > 0:
            query = query.filter(DatasetEntity.name.like(f'%{query_key}%'))

        total = query.count()

        offset = (page_num - 1) * page_size
        # Dataset.create_datetime.desc()
        order_by_col = getattr(getattr(DatasetEntity, order_by), order)()

        datasets = query.order_by(order_by_col).limit(page_size).offset(offset).all()

        return datasets, total

    def delete(self, session, dataset_name):
        model = session.query(DatasetEntity).filter(DatasetEntity.name == dataset_name).all()
        self.require_one(model, dataset_name)
        session.query(DatasetEntity).filter(DatasetEntity.name == dataset_name).delete()

    def update_by_name(self, session, dataset_name, properties):
        n_affect = session \
            .query(DatasetEntity) \
            .filter(DatasetEntity.name == dataset_name) \
            .update(properties)
        if n_affect != 1:
            raise Exception(f"Update dataset = {dataset_name} status failed, affect rows = {n_affect}, properties = {properties}")