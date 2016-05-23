from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from myapp.subunitdb import models


class SubunitClient(object):
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, connection_string):
        self.engine = create_engine(
            connection_string, pool_size=100, max_overflow=0)
        self.attachments = models.Attachments
        self.run_metadata = models.RunMetadata
        self.runs = models.Run
        self.test_metadata = models.TestMetadata
        self.test_run_metadata = models.TestRunMetadata
        self.test_runs = models.TestRun
        self.tests = models.Test

    def get_runs(
            self, run_after=None, run_before=None,
            limit=100, page=1, status='all', **metadata):
        if type(limit) != int:
            limit = int(limit)
        if type(page) != int:
            page = int(page)

        session = Session(self.engine)
        main_query = session.query(self.runs)
        if metadata:
            for k, v in metadata.items():
                sub_query = session.query(self.run_metadata.run_id)
                main_query = main_query.filter(self.runs.id.in_(
                    sub_query.filter_by(key=str(k), value=str(v))))

        if run_after is not None:
            main_query = main_query.filter(self.runs.run_at > run_after)

        if run_before is not None:
            main_query = main_query.filter(self.runs.run_at < run_before)

        if status == 'passed':
            main_query = main_query.filter(self.runs.fails == 0)
        elif status == 'failed':
            main_query = main_query.filter(self.runs.fails > 0)

        main_query = main_query.limit(limit).offset(limit*(page-1))
        return models.ListModel.from_sqlalchemy(
            main_query.all(), models.RunModel)

    def get_run_by_id(self, id_):
        session = Session(self.engine)
        main_query = session.query(self.runs)
        main_query = main_query.filter(self.runs.id == id_)
        for result in main_query.all():
            model = models.RunModel.from_sqlalchemy(result)
            return model
        return None

    def get_tests(
            self, run_after=None, run_before=None,
            limit=100, page=1, **metadata):
        if type(limit) != int:
            limit = int(limit)
        if type(page) != int:
            page = int(page)

        session = Session(self.engine)
        main_query = session.query(self.tests)
        if metadata:
            for k, v in metadata.items():
                sub_query = session.query(
                    self.test_metadata.test_id)
                main_query = main_query.filter(self.test.id.in_(
                    sub_query.filter_by(key=str(k), value=str(v))))

        main_query = main_query.limit(limit).offset(limit*(page-1))
        return models.ListModel.from_sqlalchemy(
            main_query.all(), models.TestsModel)

    def get_test_by_id(self, id_):
        session = Session(self.engine)
        main_query = session.query(self.test_runs).filter(
            self.test_runs.id == id_)
        for result in main_query.all():
            model = models.TestModel.from_sqlalchemy(result)
            return model
        return None

    def get_tests_by_run_id(self, run_id):
        session = Session(self.engine)
        main_query = session.query(self.test_runs).filter_by(
            run_id=run_id)
        return models.ListModel.from_sqlalchemy(
            main_query.all(), models.TestModel)
