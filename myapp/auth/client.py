from datetime import timedelta
import json
import os
import pickle

import requests

from myapp.common.utils import parse_date_datetime


class AuthClient(object):
    def __init__(self, url, username, api_key):
        self.url = url
        self.username = username
        self.api_key = api_key
        self.s = requests.Session()
        self.s.verify = False
        self.s.headers = {
            "Accept": "application/json", "Content-Type": "application/json"}
        self.path = "/tmp/auth_cache"

    def _auth(self):
        data = json.dumps({
            "auth": {"RAX-KSKEY:apiKeyCredentials": {
                "username": self.username, "apiKey": self.api_key}}})
        url = "{0}/tokens".format(self.url)
        return self.s.post(url, data=data)

    @property
    def token(self):
        if os.path.exists(self.path):
            try:
                dic = pickle.loads(open(self.path).read())
                # add an hour so we don't use a token that is about to expire
                now = parse_date_datetime() + timedelta(hours=1)
                if dic.get("expires") > now:
                    return dic.get("id")
            except:
                pass

        if not os.path.exists(os.path.dirname(self.path)):
            os.mkdir(os.path.dirname(self.path))
        fp = open(self.path, "wb")
        token = self._auth().json().get("access", {}).get("token", {})
        token["expires"] = parse_date_datetime(token.get("expires"))
        fp.write(pickle.dumps(token))
        fp.close()
        return token.get("id")
