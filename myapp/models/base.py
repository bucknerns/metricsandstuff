import json
from myapp.api.base import BaseAPI


class BaseModel(object):
    _api = BaseAPI

    def __init__(self, kwargs):
        for k, v in kwargs.items():
            if k != "self":
                setattr(self, k, v)

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_user(cls, data):
        return cls.from_user_dict(cls._api.handle_json(data))


class ListModel(list):
    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return [i.to_dict() for i in self]

    @classmethod
    def from_redis(cls, obj_list, model):
        ret_val = cls()
        for obj in obj_list:
            ret_val.append(model.from_redis(obj))
        return ret_val
