import pytest
from mbtest import server
from mbtest.imposters import Imposter,Stub,Response,Predicate


@pytest.fixture(scope='session')
def mock_jira(request):
    return server.mock_server(request, "../node_modules/.bin/mb")


@pytest.fixture
def jira_123(mock_jira):
    imposter = Imposter(Stub(Predicate(path="/"), Response(body="hey")))
    with mock_jira(imposter) as srv:
        yield srv.server_url
