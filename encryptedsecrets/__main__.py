# Copyright 2020 Astronomer Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import io
import os
import shlex
import tempfile

import click
import yaml

from .recrypter import Recrypter


@click.group()
def cli():
    r"""
    This tool allows editing, setting, or getting secrets from GPG-encrypted files
    """


@cli.command()
@click.option(
    '--format',
    help='Output',
    type=click.Choice(['bash', 'github']),
    default='bash',
)
@click.option(
    '-f', '--file',
    'secrets_fh',
    default='.github/secrets.yml',
    help='EYAML file to read',
    type=click.File(),
)
@click.option(
    '--import-privkey-from-env',
    'privkey_from_env',
    metavar='ENV_VAR_NAME',
    help='Import the private key from the named environment var into a temporary GPG Home dir for decryption'
)
@click.option(
    '--import-privkey-from-file',
    'privkey_fh',
    metavar='FILE',
    type=click.File(mode='rb'),
    help='Import the private key from the named environment var into a temporary GPG Home dir for decryption'
)
def export(format, secrets_fh, privkey_from_env, privkey_fh):
    """
    Produce bash-evalable output to set all secrets in the file.

    If `--format=github` is true then the value will be masked from Github logs,
    and also use the special syntax to set the value for all downstream jobs

    """

    gpghome = None
    if privkey_from_env or privkey_fh:
        gpghome = tempfile.TemporaryDirectory(prefix='airflow-gpg-home')
        crypter = Recrypter(gpg_home=gpghome.name)

        if privkey_from_env:
            privkey_fh = io.BytesIO(os.environ[privkey_from_env].encode('ascii'))

        result = crypter.ctx.import_(privkey_fh)
        if result.imported != 1:
            click.echo(click.style('Error importing GPG Private key', fg='red'), err=True)
            click.echo(click.style(repr(_gpg_import_result_to_dict(result)), fg='red'), err=True)
            exit(1)

    else:
        crypter = Recrypter()

    enc = yaml.safe_load(secrets_fh)
    decrypted = crypter.decrypt_all(enc)

    for (key, val) in decrypted.items():
        if not isinstance(val, (str, int, float, bool)):
            click.echo(click.style(f'{key!r} has not a plain value (found {val.__class__}). Only "flat" types are supported by export', fg='red'), err=True)
            exit(1)

        val = str(val)
        if format == "bash":
            print(f'export {key}={shlex.quote(val)};')
        elif format == "github":
            # https://help.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-an-environment-variable
            escaped_data = val.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
            click.echo(f'::add-mask::{escaped_data}')
            click.echo(f'::set-env name={key}::{escaped_data}')

    if gpghome:
        gpghome.cleanup()


def _gpg_import_result_to_dict(result):
    return {
        attr: getattr(result, attr) for attr in dir(result) if not attr.startswith('__')
    }


if __name__ == '__main__':
    cli()
