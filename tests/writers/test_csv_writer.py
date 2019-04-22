import csv
import io

import pytest
from hamcrest import assert_that, contains

from writers import CSV


@pytest.fixture
def example_map():
    return dict(
        TO_DO=1,
        IN_PROGRESS=2,
        DONE=3
    )


@pytest.mark.parametrize(
    'desc,keys,header,row, default', [
        ('No keys passed, it shows existing ones in order', None,
         ['DONE', 'IN_PROGRESS', 'TO_DO'], ['3', '2', '1'], None),
        ('All keys, different order, shows new order', ['TO_DO', 'IN_PROGRESS', 'DONE'],
         ['TO_DO', 'IN_PROGRESS', 'DONE'], ['1', '2', '3'], None),
        ('Keys are subset of existing ones', ['TO_DO', 'DONE'], ['TO_DO', 'DONE'], ['1', '3'], None),
        ('Non existing keys show as default', ['TO_DO', 'NON_EXISTING'], ['TO_DO', 'NON_EXISTING'], ['1', '0'], '0')
    ]
)
def test_write(example_map, desc, keys, header, row, default):
    out = io.StringIO()
    CSV.write_map(out, example_map, keys=keys, default=default)
    [actual_header, actual_row] = list(csv.reader(io.StringIO(out.getvalue())))
    assert_that(actual_header, contains(*header), desc)
    assert_that(actual_row, contains(*row), desc)


if __name__ == '__main__':
    pytest.main(['-vv'])
