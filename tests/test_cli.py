import textwrap

from encryptedsecrets.__main__ import cli


def test_export_format_bash(cli_runner):
    result = cli_runner.invoke(cli, ['export', '-f', 'tests/data/example-secrets.yml', '--import-privkey-from-file', 'tests/keys/github-actions.priv'])

    assert result.exit_code == 0, result.stderr
    assert result.stdout == textwrap.dedent('''\
    export simple_key=thing;
    export simple_plain_key=plain;
    export simple_plain_number=1;
    ''')


def test_export_format_github(cli_runner):
    result = cli_runner.invoke(cli, [
        'export', '-f', 'tests/data/example-secrets.yml', '--format=github', '--import-privkey-from-file', 'tests/keys/github-actions.priv'
    ])

    assert result.exit_code == 0, result.stderr
    assert result.stdout == textwrap.dedent('''\
    ::add-mask::thing
    ::set-env name=simple_key::thing
    ::add-mask::plain
    ::set-env name=simple_plain_key::plain
    ::add-mask::1
    ::set-env name=simple_plain_number::1
    ''')
