import sys
from abc import ABC

from hamcrest.core.base_matcher import BaseMatcher
from typing import List, Optional, Any
from subprocess import CompletedProcess


class CompletedProcessMatcher(BaseMatcher, ABC):
    def __init__(self):
        super().__init__()

    @staticmethod
    def _output_str(cmd_result: CompletedProcess) -> Optional[str]:
        return cmd_result.stdout.decode(sys.stdout.encoding) if cmd_result.stdout is not None else None

    @staticmethod
    def _output_lines(cmd_result: CompletedProcess) -> Optional[List[str]]:
        res = CompletedProcessMatcher._output_str(cmd_result)
        return res.split('\n') if res is not None else None

    @staticmethod
    def _output_cell(cmd_result: CompletedProcess, row: int, col: str) -> Optional[str]:
        try:
            lines = CompletedProcessMatcher._output_lines(cmd_result)
            vals = dict(zip(lines[0].split(','), lines[row + 1].split(',')))
            return vals[col]
        except (IndexError, AttributeError, KeyError, TypeError):
            return None

    @staticmethod
    def _error_str(cmd_result: CompletedProcess) -> str:
        return cmd_result.stderr.decode(sys.stderr.encoding) if cmd_result.stderr is not None else None

    @staticmethod
    def _error_lines(cmd_result: CompletedProcess) -> List[str]:
        res = CompletedProcessMatcher._error_str(cmd_result)
        return res.split("\n") if res is not None else None


class HeaderHasColumnsMatcher(CompletedProcessMatcher):
    def __init__(self, columns: List[str]):
        super().__init__()
        self.columns = columns

    def _matches(self, cmd_result: CompletedProcess) -> bool:
        lines = self._output_lines(cmd_result)
        if lines is None:
            return False
        try:
            actual = lines[0].split(",")
            return set(self.columns) == set(actual)
        except (IndexError, AttributeError):
            return False

    def describe_to(self, description):
        description.append_text(f'Header line to have these columns: {",".join(self.columns)}')


def has_header_with_all_columns_in(cols: List[str]):
    return HeaderHasColumnsMatcher(cols)


class HeaderHasColumnsInOrderMatcher(CompletedProcessMatcher):
    def __init__(self, columns: List[str]):
        super().__init__()
        self.columns = columns

    def _matches(self, cmd_result: CompletedProcess) -> bool:
        lines = self._output_lines(cmd_result)
        if lines is None:
            return False
        try:
            return self.columns == lines[0].split(',')
        except (IndexError, AttributeError):
            return False

    def describe_to(self, description):
        description.append_text(f'Header line to have these columns, in the same order: {",".join(self.columns)}')


def has_header_with_columns_in_the_same_order(cols: List[str]):
    return HeaderHasColumnsInOrderMatcher(cols)


class HeaderHasColumnsInLexicographicalOrderMatcher(CompletedProcessMatcher):
    def __init__(self, columns: List[str]):
        super().__init__()
        self.columns = columns

    def _matches(self, cmd_result: CompletedProcess) -> bool:
        lines = self._output_lines(cmd_result)
        if lines is None:
            return False
        try:
            return sorted(self.columns) == lines[0].split(',')
        except (IndexError, AttributeError):
            return False

    def describe_to(self, description):
        description.append_text(
            f'Header line to have these columns, in lexicographical order: {",".join(self.columns)}')


def has_header_with_columns_in_lexicographical_order(cols: List[str]):
    return HeaderHasColumnsInLexicographicalOrderMatcher(cols)


class CommandSuccededMatcher(CompletedProcessMatcher):
    def __init__(self):
        super().__init__()

    def _matches(self, cmd_result: CompletedProcess) -> bool:
        return cmd_result.returncode == 0

    def describe_to(self, description):
        description.append_text('Expected command to have a returncode == 0')


def completed_successfully():
    return CommandSuccededMatcher()


class CellHasValueMatcher(CompletedProcessMatcher):
    def __init__(self, row: int, col: str, expected: str):
        super().__init__()
        self.row = row
        self.col = col
        self.expected = expected

    def _matches(self, cmd_result: CompletedProcess) -> bool:
        return CompletedProcessMatcher._output_cell(cmd_result, self.row, self.col) == self.expected

    def describe_to(self, description):
        description.append_text(f'Expected cell ({self.row}, {self.col}) to have {self.expected}')


def output_cell_has_value(row: int, col: str, expected: Any):
    return CellHasValueMatcher(row, col, str(expected))
