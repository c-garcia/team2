"""
Set up mountebank for jira dao integration tests
"""

import pytest
from mbtest import server


@pytest.fixture(scope="session")
def mock_jira(request):
    return server.mock_server(request, port=2526)
