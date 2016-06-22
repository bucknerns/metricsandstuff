import json
import re
from base64 import b64decode

import falcon
import six

from myapp.common.constants import (
    RUN_STATUSES, TEST_STATUSES, DEFAULT_LIMIT, DEFAULT_PAGE, MAX_LIMIT,
    FILTER_TYPES)
from myapp.common.utils import parse_date_string


class BaseAPI(object):
    route = None

    def __init__(self, redis_client, files_client):
        self.redis = redis_client
        self.files = files_client

    # falcon helpers
    @staticmethod
    def bad_request(message):
        raise falcon.HTTPBadRequest(
            description=message, title=falcon.HTTP_400, code=400)

    @staticmethod
    def not_found(message="The requested resource does not exist"):
        raise falcon.HTTPNotFound(description=message, code=falcon.HTTP_404)

    @staticmethod
    def redirect(location):
        raise falcon.HTTPMovedPermanently(location)

    # api specific handle methods
    def handle_test_id(self, test_id, required=True):
        if required:
            self.handle_required(test_id, "test_id")
        elif test_id is None:
            return None
        if not self.redis.is_valid_test(test_id):
            self.bad_request("Invalid 'test_id'.")
        return test_id

    def handle_attachment_id(self, attachment_id, required=True):
        if required:
            self.handle_required(attachment_id, "attachment_id")
        elif attachment_id is None:
            return None
        if not self.redis.is_valid_attachment(attachment_id):
            self.bad_request("Invalid 'attachment_id'.")
        return attachment_id

    def handle_run_id(self, run_id, required=True):
        if required:
            self.handle_required(run_id, "run_id")
        elif run_id is None:
            return None
        if not self.redis.is_valid_run(run_id):
            self.bad_request("Invalid 'run_id'.")
        return run_id

    def handle_filter_regex(self, name, regex, exists):
        self.handle_filter_name(name, exists)
        return name, self.handle_regex(regex, "regex")

    def handle_filter_name(self, name, exists):
        name = self.handle_string(name, "name")
        if exists != self.redis.has_filter(name):
            if exists:
                self.bad_request("Filter does not exist: {0}".format(name))
            self.bad_request("Filter already exists")
        return name

    @classmethod
    def handle_run_status(cls, status, required=True):
        return cls.handle_stringlist(status, "status", RUN_STATUSES, required)

    @classmethod
    def handle_test_status(cls, status, required=True):
        return cls.handle_stringlist(status, "status", TEST_STATUSES, required)

    @classmethod
    def handle_filter_type(cls, type_, required=True):
        return cls.handle_stringlist(type_, "status", FILTER_TYPES, required)

    @classmethod
    def handle_limit(cls, limit):
        if limit is None:
            limit = DEFAULT_LIMIT
        return cls.handle_int(limit, "limit", min_=1, max_=MAX_LIMIT)

    @classmethod
    def handle_page(cls, page):
        if page is None:
            page = DEFAULT_PAGE
        return cls.handle_int(page, "page", min_=1)

    # generic helpers
    @classmethod
    def handle_stringlist(cls, value, value_name, accepted_values, required):
        if required:
            cls.handle_required(value, value_name)
        elif value is None:
            return None
        if value and value not in accepted_values:
            cls.bad_request("'{0}' not in {1}.".format(
                value_name, accepted_values))
        return value

    @classmethod
    def handle_int(cls, number, var_name, min_=None, max_=None, required=True):
        if required:
            cls.handle_required(number, var_name)
        elif number is None:
            return None
        try:
            number = int(number)
        except ValueError:
            cls.bad_request("'{0}' must be an integer.".format(var_name))

        if max_ is not None:
            if number > max_:
                cls.bad_request(
                    "'{0}' must be less than or equal to {1}.".format(
                        var_name, max_))
        if min_ is not None:
            if number < min_:
                cls.bad_request(
                    "'{0}' must be greater than or equal to {1}.".format(
                        var_name, min_))
        return number

    @classmethod
    def handle_string(cls, string, var_name, required=True):
        if required:
            cls.handle_required(string, var_name)
        elif string is None:
            return None
        if not isinstance(string, six.string_types):
            cls.bad_request("'{0}' must be a string".format(var_name))
        return string

    @classmethod
    def handle_float(cls, number, var_name, required=True):
        if required:
            cls.handle_required(number, var_name)
        elif number is None:
            return None
        try:
            return float(number)
        except ValueError:
            cls.bad_request("'{0}' must be a float.".format(var_name))

    @classmethod
    def handle_dict(cls, dic, var_name, required=False, nested=False):
        if required:
            cls.handle_required(dic, var_name)
        elif dic is None:
            return None
        if not isinstance(dic, dict):
            cls.bad_request("'{0}' must be a dictionary.".format(var_name))

        if not nested:
            for k, v in dic.items():
                if isinstance(v, (list, dict)):
                    cls.bad_request(
                        "'{0}' does not support nested dictionary.".format(
                            var_name))
        return dic

    @classmethod
    def handle_date(cls, date, var_name, required=True):
        date = cls.handle_string(date, var_name, required)
        try:
            return date if date is None else parse_date_string(date)
        except:
            cls.bad_request(
                "'{0}' must be a valid iso format date.".format(var_name))

    @classmethod
    def handle_required(cls, var, var_name):
        if var is None:
            cls.bad_request("'{0}' is required.".format(var_name))
        return var

    @classmethod
    def handle_base64(cls, var, var_name, required=False):
        var = cls.handle_string(var, var_name, required)
        try:
            return var if var is None else b64decode(var)
        except:
            cls.bad_request("'{0}' must be valid base64.".format(
                var_name))

    @classmethod
    def handle_regex(cls, regex, var_name, required=True):
        regex = cls.handle_string(regex, var_name, required)
        try:
            return regex if regex is None else re.compile(regex)
        except re.error:
            cls.bad_request("'{0}' must be a valid regex.".format(var_name))

    @classmethod
    def handle_json(cls, data):
        try:
            return json.loads(data)
        except:
            cls.bad_request("Invalid Json in body of request.")

    @classmethod
    def handle_list(cls, list_, var_name, required=False, nested=False):
        if required:
            cls.handle_required(list_, var_name)
        elif list_ is None:
            return None
        if not isinstance(list_, list):
            cls.bad_request("'{0}' must be a dictionary.".format(var_name))

        if not nested:
            for v in list_:
                if isinstance(v, (list, dict)):
                    cls.bad_request(
                        "'{0}' does not support nested lists.".format(
                            var_name))
        return list_
