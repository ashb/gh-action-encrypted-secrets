=================
encrypted-secrets
=================

Inspired by hiera-eyaml__, but for integration in to Python projects

.. __: https://github.com/voxpupuli/hiera-eyaml

Using in Github Actions
=======================

This repo published an `action.yml` to make it available for Github Actions.

Parameters
----------

*gpg-priv_key*:
  The GPG private key to use to decrypt secrets.

  **Required**

  The recommended way of using this is to have the ascii-armored GPG key be set
  in a Github Secret, and then specify this value via
  ``${{ secrets.secretsGpgPrivateKey }}``

*secrets-file*:
  Which file contains the secrets.

  **Default:** ``.github/secrets.yml``

Example use:
------------

.. code-block:: yaml

    jobs:
      Something:
        name: My job
        runs-on: ubuntu-latest
        steps:
        - name: Decrypt Secrets
          uses: ashb/gh-action-encrypted-secrets@v1
          with:
            gpg-priv-key: ''
            gpg-priv-key-file: tests/keys/github-actions.priv
            secrets-file: tests/data/example-secrets.yml
        - name: Test Secrets from env
          run: |
            set -xe
            echo 1
            echo $simple_plain_number
            [[ $simple_plain_number == 1 ]] || echo "should NOT see this"
            [[ $simple_plain_key == plain ]]
            echo "plain should be masked"
            [[ $simple_plain_number == 0 ]] || echo "should see this"

This will set environment for steps later on in the same job, and mask the values printed in the log so that they stay secret.

It **does not** affect other jobs in the Action. Each Job that needs the secret will need to use this action
