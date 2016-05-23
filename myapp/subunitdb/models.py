import json
import datetime
import six

import sqlalchemy as sa
from sqlalchemy.ext import declarative

BASE = declarative.declarative_base()


class Test(BASE):
    __tablename__ = 'tests'
    __table_args__ = (sa.Index('ix_test_ids', 'id', 'test_id',
                               mysql_length={'test_id': 30}),
                      sa.Index('ix_tests_test_id', 'test_id',
                               mysql_length=30))
    id = sa.Column(sa.BigInteger, primary_key=True)
    test_id = sa.Column(sa.String(256),
                        nullable=False)
    run_count = sa.Column(sa.Integer())
    success = sa.Column(sa.Integer())
    failure = sa.Column(sa.Integer())
    run_time = sa.Column(sa.Float())


class Run(BASE):
    __tablename__ = 'runs'
    __table_args__ = (sa.Index('ix_run_at', 'run_at'),
                      sa.Index('ix_run_uuid', 'uuid'))
    uuid = sa.Column(sa.String(36),
                     default=lambda: six.text_type(uuid.uuid4()))
    id = sa.Column(sa.BigInteger, primary_key=True)
    skips = sa.Column(sa.Integer())
    fails = sa.Column(sa.Integer())
    passes = sa.Column(sa.Integer())
    run_time = sa.Column(sa.Float())
    artifacts = sa.Column(sa.Text())
    run_at = sa.Column(sa.DateTime,
                       default=datetime.datetime.utcnow)


class TestRun(BASE):
    __tablename__ = 'test_runs'
    __table_args__ = (sa.Index('ix_test_id_status', 'test_id', 'status'),
                      sa.Index('ix_test_id_start_time', 'test_id',
                               'start_time'),
                      sa.Index('ix_test_runs_test_id', 'test_id'),
                      sa.Index('ix_test_runs_run_id', 'run_id'),
                      sa.Index('ix_test_runs_start_time', 'start_time'),
                      sa.Index('ix_test_runs_stop_time', 'stop_time'),
                      sa.UniqueConstraint('test_id', 'run_id',
                                          name='uq_test_runs'))

    id = sa.Column(sa.BigInteger, primary_key=True)
    test_id = sa.Column(sa.BigInteger)
    run_id = sa.Column(sa.BigInteger)
    status = sa.Column(sa.String(256))
    start_time = sa.Column(sa.DateTime())
    start_time_microsecond = sa.Column(sa.Integer(), default=0)
    stop_time = sa.Column(sa.DateTime())
    stop_time_microsecond = sa.Column(sa.Integer(), default=0)
    test = sa.orm.relationship(Test, backref=sa.orm.backref('test_run_test'),
                               foreign_keys=test_id,
                               primaryjoin=test_id == Test.id)
    run = sa.orm.relationship(Run, backref=sa.orm.backref('test_run_run'),
                              foreign_keys=run_id,
                              primaryjoin=run_id == Run.id)


class RunMetadata(BASE):
    __tablename__ = 'run_metadata'
    __table_args__ = (sa.Index('ix_run_key_value', 'key', 'value'),
                      sa.Index('ix_run_id', 'run_id'),
                      sa.UniqueConstraint('run_id', 'key', 'value',
                                          name='uq_run_metadata'))

    id = sa.Column(sa.BigInteger, primary_key=True)
    key = sa.Column(sa.String(255))
    value = sa.Column(sa.String(255))
    run_id = sa.Column(sa.BigInteger)
    run = sa.orm.relationship(Run, backref='run', foreign_keys=run_id,
                              primaryjoin=run_id == Run.id)


class TestRunMetadata(BASE):
    __tablename__ = 'test_run_metadata'
    __table_args__ = (sa.Index('ix_test_run_key_value', 'key', 'value'),
                      sa.Index('ix_test_run_id', 'test_run_id'),
                      sa.UniqueConstraint('test_run_id', 'key', 'value',
                                          name='uq_test_run_metadata'))

    id = sa.Column(sa.BigInteger, primary_key=True)
    key = sa.Column(sa.String(255))
    value = sa.Column(sa.String(255))
    test_run_id = sa.Column(sa.BigInteger)
    test_run = sa.orm.relationship(TestRun,
                                   backref=sa.orm.backref('test_run_meta'),
                                   foreign_keys=test_run_id,
                                   primaryjoin=test_run_id == TestRun.id)


class TestMetadata(BASE):
    __tablename__ = 'test_metadata'
    __table_args__ = (sa.Index('ix_test_key_value', 'key', 'value'),
                      sa.Index('ix_test_id', 'test_id'),
                      sa.UniqueConstraint('test_id', 'key', 'value',
                                          name='uq_test_metadata'))

    id = sa.Column(sa.BigInteger, primary_key=True)
    key = sa.Column(sa.String(255))
    value = sa.Column(sa.String(255))
    test_id = sa.Column(sa.BigInteger)
    test = sa.orm.relationship(Test, backref='test', foreign_keys=test_id,
                               primaryjoin=test_id == Test.id)


class Attachments(BASE):
    __tablename__ = 'attachments'
    __table_args__ = (sa.Index('ix_attach_test_run_id', 'test_run_id'),)
    id = sa.Column(sa.BigInteger, primary_key=True)
    test_run_id = sa.Column(sa.BigInteger)
    label = sa.Column(sa.String(255))
    attachment = sa.Column(sa.LargeBinary())
    test_run = sa.orm.relationship(TestRun, backref='test_run_attach',
                                   foreign_keys=test_run_id,
                                   primaryjoin=test_run_id == TestRun.id)


class BaseModel(object):
    def __init__(self, kwargs):
        for k, v in kwargs.items():
            if k != "self":
                setattr(self, k, v)

    def to_json(self):
        return json.dumps(self.to_dict())


class ListModel(list):
    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return [i.to_dict() for i in self]

    @classmethod
    def from_sqlalchemy(cls, obj_list, model):
        ret_val = cls()
        for obj in obj_list:
            ret_val.append(model.from_sqlalchemy(obj))
        return ret_val


class RunModel(BaseModel):
    def __init__(
        self, id=None, skips=None, fails=None, passes=None, run_at=None,
            run_time=None, metadata=None):
        super(RunModel, self).__init__(locals())

    def to_dict(self):
        try:
            time = self.run_at.strftime(self.TIME_FORMAT)
        except:
            time = str(self.run_at)

        dic = {
            "id": self.id,
            "skips": self.skips,
            "fails": self.fails,
            "passes": self.passes,
            "run_at": time,
            "run_time": self.run_time}
        if self.metadata is not None:
            dic["metadata"] = self.metadata
        return dic

    @classmethod
    def from_sqlalchemy(cls, obj):
        if obj.run:
            metadata = {k: v for k, v in [(o.key, o.value) for o in obj.run]}
        else:
            metadata = None
        return cls(
            id=obj.id,
            skips=obj.skips,
            fails=obj.fails,
            passes=obj.passes,
            run_at=obj.run_at,
            run_time=obj.run_time,
            metadata=metadata)


class TestsModel(BaseModel):
    def __init__(
        self, id=None, test_id=None, run_count=None, success=None, failure=None,
            run_time=None, metadata=None):
        super(TestsModel, self).__init__(locals())

    def to_dict(self):
        dic = {
            "id": self.id,
            "test_id": self.test_id,
            "run_count": self.run_count,
            "success": self.success,
            "failure": self.failure,
            "run_time": self.run_time}
        if self.metadata is not None:
            dic["metadata"] = self.metadata
        return dic

    @classmethod
    def from_sqlalchemy(cls, obj):
        if obj.test_meta:
            metadata = {k: v for k, v in
                        [(o.key, o.value) for o in obj.test_meta]}
        else:
            metadata = None

        return cls(
            id=obj.id,
            test_id=obj.test_id,
            run_count=obj.run_count,
            success=obj.success,
            failure=obj.failure,
            run_time=obj.run_time,
            metadata=metadata)


class TestModel(BaseModel):
    def __init__(
        self, id=None, test_id=None, run_id=None, status=None, start_time=None,
        stop_time=None, start_time_microsecond=None,
            stop_time_microsecond=None, metadata=None, test_name=None):
        super(TestModel, self).__init__(locals())

    def to_dict(self):
        try:
            start = self.start_time.strftime(self.TIME_FORMAT)
        except:
            start = str(self.start_time)

        try:
            stop = self.stop_time.strftime(self.TIME_FORMAT)
        except:
            stop = str(self.stop_time)

        dic = {
            "id": self.id,
            "test_id": self.test_id,
            "run_id": self.run_id,
            "status": self.status,
            "start_time": start,
            "stop_time": stop,
            "start_time_microsecond": self.start_time_microsecond,
            "stop_time_microsecond": self.stop_time_microsecond,
            "test_name": self.test_name}
        if self.metadata is not None:
            dic["metadata"] = self.metadata
        return dic

    @classmethod
    def from_sqlalchemy(cls, obj):
        if obj.test_run_meta:
            metadata = {k: v for k, v in
                        [(o.key, o.value) for o in obj.test_run_meta]}
        else:
            metadata = None
        return cls(
            id=obj.id,
            test_id=obj.test_id,
            run_id=obj.run_id,
            status=obj.status,
            start_time=obj.start_time,
            stop_time=obj.stop_time,
            start_time_microsecond=obj.start_time_microsecond,
            stop_time_microsecond=obj.stop_time_microsecond,
            test_name=obj.test.test_id,
            metadata=metadata)
