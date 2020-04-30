=================
encrypted-secrets
=================

Inspired by hiera-eyaml__, but for integration in to Python projects

.. __: https://github.com/voxpupuli/hiera-eyaml

Purpose
=======

This module encrypts *part* of a YAML file so that the file can be committed in
to git, and have the value not be in plain text, but still have somewhat-useful
git diffs, that is, so a PR can show that a value changed, even **what**
changed in the value is hidden.

Creating the GPG key
====================

For this module/action to work, it need a GPG private key to use, and since it
is used in CI/operator-less environments it is not possible to ask for a GPG
key. As result it is recommended that you create a dedicated GPG keypair just
for this purpose. That can be achieved with the following commands:

.. code-block:: bash

     install -d --mode 700 gpg-temp
     gpg --homedir=gpg-temp --passphrase '' --batch --quick-gen-key 'Project CI Secrets <project-ci-secrets@invalid>' futuredefault
     gpg --homedir=gpg-temp --armor --export-secret-keys airflow-github-actions@invalid > project-ci-gpg.priv
     gpg --homedir=gpg-temp --armor --export-keys airflow-github-actions@invalid > project-ci-gpg.pub

The contents of the .priv key should be placed in the CI environment using it's
native secret settings (i.e. Secret for Github Actions). Once that single
setting is created, all other secrets for CI can be tracked in git and added
via a PR.

Using in Github Actions
=======================

This repo published with an ``action.yml`` to make it available for Github Actions.

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
