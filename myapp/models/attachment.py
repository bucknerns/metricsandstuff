from base64 import b64decode

from myapp.models.base import BaseModel, ListModel
from myapp.redis.db_layout import Attachment


class AttachmentModel(BaseModel):
    def __init__(
            self, attachment_id=None, name=None, location=None, data=None,
            run_id=None, test_id=None):
        super(AttachmentModel, self).__init__(locals())

    def to_dict(self):
        return {
            "name": self.name, "location": self.location,
            "attachment_id": self.attachment_id}

    @classmethod
    def from_redis(cls, data):
        return cls(
            attachment_id=data.get(Attachment.ATTACHMENT_ID),
            name=data.get(Attachment.NAME),
            location=data.get(Attachment.LOCATION))

    @classmethod
    def from_dict(cls, data):
        encoded_data = data.get("data")
        if encoded_data is not None:
            decoded_data = b64decode(encoded_data)

        return cls(
            name=data.get("name"),
            data=decoded_data,
            run_id=data.get("run_id"),
            test_id=data.get("test_id"),
            attachment_id=data.get("attachment_id"))


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

    def to_dict(self):
        return {"name": self.name, "regex": self.regex}

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name"),
            regex=data.get("regex"))
