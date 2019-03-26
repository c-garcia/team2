import pytest
from mbtest import server
from mbtest.imposters import Imposter, Stub, Response, Predicate


@pytest.fixture(scope='session')
def mock_jira(request):
    return server.mock_server(request)


@pytest.fixture
def jira_123(mock_jira) -> str:
    imposter = Imposter(Stub(Predicate(path="/"), Response(body="hey")))
    with mock_jira(imposter) as srv:
        yield str(imposter.url)
