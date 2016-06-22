from hashlib import sha1
from urlparse import urlparse
import ast
import hmac
import json
import re

from myapp.common.utils import parse_date_ts
from myapp.common.client import BaseRaxClient
from myapp.common.constants import EXPIRE_SECONDS


class FilesClient(BaseRaxClient):
    CONTAINER_COUNT = 16

    def __init__(
        self, url, auth_client, temp_url_key, container_prefix="",
            expire=None):
        super(FilesClient, self).__init__(url, auth_client)
        self.temp_url_key = temp_url_key
        self.cp = container_prefix
        self.expire = expire or EXPIRE_SECONDS

    def init_files_account(self):
        self.update_account_headers({
            "X-Account-Meta-Temp-Url-Key": self.temp_url_key})
        headers = {"X-Container-Meta-Access-Control-Allow-Origin": "*"}
        for i in xrange(self.CONTAINER_COUNT):
            container = "{0}{1}".format(self.cp, i)
            self.create_container(container, headers=headers)

    def create_attachment(self, id_, data, name):
        if data is None:
            return
        id_ = int(id_)
        container = "{0}{1}".format(self.cp, id_ % self.CONTAINER_COUNT)
        headers = {
            "Content-Type": "text/plain", "X-Delete-After": self.expire,
            "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
            "Access-Control-Allow-Origin": "*"}
        resp = self.create_object(container, id_, data, headers=headers)
        tempurl = self.create_temp_url(id_, name)
        return tempurl, resp

    def get_attachment(self, id_):
        id_ = int(id_)
        container = "{0}{1}".format(self.cp, id_ % self.CONTAINER_COUNT)
        url = "{0}/{1}/{2}".format(self.url, container, id_)
        return self.get(url)

    @staticmethod
    def _get_group_dict(match):
        dic = match.groupdict()
        for k, v in dic.items():
            try:
                dic[k] = json.loads(v)
            except:
                try:
                    dic[k] = ast.literal_eval(v)
                except:
                    pass
        return dic

    @staticmethod
    def _get_group_tuple(match):
        groups = []
        for v in match.groups():
            try:
                groups.append(json.loads(v))
            except:
                try:
                    groups.append(ast.literal_eval(v))
                except:
                    groups.append(v)
        return tuple(groups)

    def get_attachment_filter(self, id_, regexes, type_=None):
        regexes = regexes or []
        resp = self.get_attachment(id_)
        if not resp.ok:
            raise Exception("File not found")
        matches = [list(re.finditer(regex, resp.content)) for regex in regexes]
        matches = [x for x in matches if x]
        ret_val = []
        while matches:
            min_index, min_match_list = min(
                enumerate(matches), key=lambda x: x[1][0].span()[0])
            match = min_match_list.pop(0)

            if type_ == "groupdict":
                ret_val.append(self._get_group_dict(match))
            elif type_ == "groups":
                ret_val.append(self._get_group_tuple(match))
            elif type_ == "match":
                ret_val.append(match.group(0))
            else:
                dic = self._get_group_dict(match)
                if dic:
                    ret_val.append(dic)
                else:
                    groups = self._get_group_tuple(match)
                    if groups:
                        ret_val.append(groups)
                    else:
                        ret_val.append(match.group(0))

            # remove empty and None
            matches = [x for x in matches if x]
        return ret_val

    def create_temp_url(self, id_, filename):
        id_ = int(id_)
        container = "{0}{1}".format(self.cp, id_ % self.CONTAINER_COUNT)
        path = "{0}/{1}/{2}".format(urlparse(self.url).path, container, id_)
        expires = int(parse_date_ts()) + self.expire
        hmac_body = "{0}\n{1}\n{2}".format("GET", expires, path)
        sig = hmac.new(self.temp_url_key, hmac_body, sha1).hexdigest()
        url = "{0}/{1}/{2}?temp_url_sig={3}&temp_url_expires={4}&filename={5}"
        return url.format(self.url, container, id_, sig, expires, filename)

    def del_prefix(self, prefix=None):
        prefix = prefix or self.cp
        for i in xrange(self.CONTAINER_COUNT):
            container = "{0}{1}".format(prefix, i)
            self.delete_container_r(container)

    # base files funtionality
    def create_object(self, container, obj, data, headers=None):
        url = "{0}/{1}/{2}".format(self.url, container, obj)
        return self.put(url, data=data, headers=headers)

    def delete_container_r(self, container):
        while True:
            files = self.list_objects(container).json()
            if not files:
                break
            for file_ in files:
                self.delete_object(container, file_.get("name"))
        return self.delete_container(container)

    def delete_container(self, container):
        url = "{0}/{1}".format(self.url, container)
        return self.delete(url)

    def delete_object(self, container, obj):
        url = "{0}/{1}/{2}".format(self.url, container, obj)
        return self.delete(url)

    def list_objects(self, container):
        params = {"format": "json"}
        url = "{0}/{1}".format(self.url, container)
        return self.get(url, params=params)

    def update_account_headers(self, headers=None):
        return self.s.post(self.url, headers=headers)

    def create_container(self, container, headers=None):
        url = "{0}/{1}".format(self.url, container)
        return self.put(url, headers=headers)

    def get_object(self, container, obj):
        url = "{0}/{1}/{2}".format(self.url, container, obj)
        return self.get(url)
