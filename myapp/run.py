from ConfigParser import SafeConfigParser
import sys

import falcon

from api import runs, tests
from myapp.subunitdb.client import SubunitClient


config = SafeConfigParser()
config.read("{0}/.metricsandstuff/my.cnf".format(sys.prefix))
connection_string = config.get('database', 'connection_string')
username = config.get('database', 'username')
password = config.get('database', 'password')
url = config.get('database', 'url')
database = config.get('database', 'database')

client = SubunitClient("{0}://{1}:{2}@{3}/{4}".format(
    connection_string, username, password, url, database))
calls = [runs.TestsByRunID, tests.Tests, tests.Test, runs.Runs, runs.Run]


def handle_404(req, resp):
    raise falcon.HTTPNotFound(
        description="The requested resource does not exist",
        code=falcon.HTTP_404)

app = falcon.API()
for class_ in calls:
    app.add_route(class_.route, class_(client))

app.add_sink(handle_404, '')
