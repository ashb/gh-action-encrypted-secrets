import contextlib
import io
import warnings

import pytest
from click.testing import CliRunner

"""
In your tests:
  def test_foo(cli_runner):
    r = cli_runner.invoke(mycli, ["mycommand"])
    assert r.exit_code == 0
In `some_command()`, add:
  @cli.command()
  def mycommand():
    import pytest; pytest.set_trace()
Then run via:
  pytest --pdb-trace ...

Note any tests checking CliRunner stdout/stderr values will fail when --pdb-trace is set.
"""


def pytest_addoption(parser):
    parser.addoption(
        "--pdb-trace",
        action="store_true",
        default=False,
        help="Allow calling pytest.set_trace() in Click's CliRunner",
    )


class MyCliRunner(CliRunner):
    def __init__(self, *args, in_pdb=False, **kwargs):
        self._in_pdb = in_pdb
        super().__init__(*args, **kwargs)

    def invoke(self, cli, args=None, **kwargs):
        params = kwargs.copy()
        if self._in_pdb:
            params['catch_exceptions'] = False

        return super().invoke(cli, args=args, **params)

    def isolation(self, input=None, env=None, color=False):
        if self._in_pdb:
            if input or env or color:
                warnings.warn("CliRunner PDB un-isolation doesn't work if input/env/color are passed")
            else:
                return self.isolation_pdb()

        return super().isolation(input=input, env=env, color=color)

    @contextlib.contextmanager
    def isolation_pdb(self):
        s = io.BytesIO(b"{stdout not captured because --pdb-trace}")
        yield (
            s,
            not self.mix_stderr and s
        )


@pytest.fixture
def cli_runner(request):
    """ A wrapper round Click's test CliRunner to improve usefulness """
    return MyCliRunner(
        # workaround Click's environment isolation so debugging works.
        in_pdb=request.config.getoption("--pdb-trace"),
        mix_stderr=False,
    )
