from myapp.models.base import BaseModel
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
            run_id=data.get("run_id"),
            test_id=data.get("test_id"),
            attachment_id=data.get("attachment_id"))
