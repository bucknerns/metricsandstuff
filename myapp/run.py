import falcon
from api import runs, tests
from myapp.subunitdb.client import SubunitClient


client = SubunitClient("mysql://root:abc123@127.0.0.1/subunit")
calls = [runs.TestsByRunID, tests.Tests, tests.Test, runs.Runs, runs.Run]


def handle_404(req, resp):
    raise falcon.HTTPNotFound(
        description="The requested resource does not exist",
        code=falcon.HTTP_404)

app = falcon.API()
for class_ in calls:
    app.add_route(class_.route, class_(client))

app.add_sink(handle_404, '')
