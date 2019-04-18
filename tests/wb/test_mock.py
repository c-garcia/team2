import sys
import pytest

from hamcrest import assert_that, equal_to


def test_mock_version(mocker):
    mocker.patch.object(sys, 'version',  new='FAKEVERSION')
    assert_that(sys.version, equal_to('FAKEVERSION'))


if __name__ == '__main__':
    pytest.main([])
