import pytest
from mbtest import server


@pytest.fixture(scope="session")
def mock_jira(request):
    return server.mock_server(request)
