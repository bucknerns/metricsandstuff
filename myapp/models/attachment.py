import json

from myapp.models.base import BaseModel, ListModel
from myapp.redis.db_layout import Attachment


class AttachmentModel(BaseModel):
    def __init__(
            self, attachment_id=None, name=None, location=None, data=None,
            run_id=None, test_id=None):
        super(AttachmentModel, self).__init__(locals())

    def to_dict(self):
        return {
            "name": self.name,
            "location": self.location,
            "attachment_id": self.attachment_id}

    @classmethod
    def from_redis(cls, data):
        return cls(
            attachment_id=data.get(Attachment.ATTACHMENT_ID),
            name=data.get(Attachment.NAME),
            location=data.get(Attachment.LOCATION))

    @classmethod
    def from_user_dict(cls, data):
        return cls(
            name=cls._api.handle_string(data.get("name"), "name", False),
            data=cls._api.handle_base64(data.get("data"), "data", False),
            run_id=cls._api.handle_run_id(data.get("run_id"), False),
            test_id=cls._api.handle_test_id(data.get("test_id"), False),
            attachment_id=cls._api.handle_attachment_id(
                data.get("attachment_id"), False))


class FiltersModel(ListModel):
    @classmethod
    def from_redis(cls, dic):
        ret_val = cls()
        for name, regex in dic.items():
            ret_val.append(FilterModel(name, regex))
        return ret_val


class FilterModel(BaseModel):
    def __init__(self, name=None, regex=None):
        super(FilterModel, self).__init__(locals())

    @classmethod
    def from_user(cls, data, update=False):
        try:
            dic = json.loads(data)
        except:
            cls._api.bad_request("Invalid Json in body of request.")

        return cls.from_user_dict(dic, update)

    def to_dict(self):
        return {"name": self.name, "regex": self.regex}

    @classmethod
    def from_user_dict(cls, data, update):
        return cls(*cls._api.handle_filter(
            name=data.get("name"),
            regex=data.get("regex"),
            exists=update))
