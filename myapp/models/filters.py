from myapp.models.base import ListModel, BaseModel


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
    def from_user_dict(cls, data):
        return cls(
            name=data.get("name"),
            regex=data.get("regex"))
