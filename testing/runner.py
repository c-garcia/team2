import subprocess

EXEC = 'team2.py'


class CommandRunner:
    def __init__(self):
        self._cmd = ['python', EXEC]
        self._argument = None
        self._options = []
        self._global_options = []
        self._subcommand = None

    def with_option(self, name, value=None) -> 'CommandRunner':
        self._options.append(name)
        if value is not None:
            self._options.append(value)
        return self

    def with_subcommand(self, subcommand: str) -> 'CommandRunner':
        self._subcommand = subcommand
        return self

    def with_global_option(self, name, value=None) -> 'CommandRunner':
        self._global_options.append(name)
        if value is not None:
            self._global_options.append(value)
        return self

    def with_argument(self, arg: str) -> 'CommandRunner':
        self._argument = arg
        return self

    def run(self) -> subprocess.CompletedProcess:
        cmd = [*self._cmd, *self._global_options]
        if self._subcommand is not None:
            cmd.append(self._subcommand)
            cmd = [*cmd, *self._options]
        if self._argument is not None:
            cmd.append(self._argument)
        return subprocess.run(
            cmd,
            stdout=subprocess.PIPE
        )


def command() -> CommandRunner:
    return CommandRunner()
