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
import os
import re

from setuptools import find_namespace_packages, setup


def fpath(*parts):
    return os.path.join(os.path.dirname(__file__), *parts)


def read(*parts):
    return open(fpath(*parts)).read()


def desc():
    return read('README.rst')


# https://packaging.python.org/guides/single-sourcing-package-version/
def find_version(*paths):
    version_file = read(*paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def or_fallback(fn, *args, fallback, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception:
        return fallback


VERSION = or_fallback(find_version, 'encryptedsecrets', '__init__.py', fallback='0.0.0-dev1')

setup(
    name='encrypted-secrets',
    version=VERSION,
    url='https://github.com/astronomer/encrypted-python-secrets',
    license='Apache2',
    author='astronomerio',
    author_email='humans@astronomer.io',
    description='Store secrets in an encrypted YAML file, inspired by hiera-eyaml',
    long_description=or_fallback(desc, fallback=''),
    long_description_content_type="text/rst",
    packages=find_namespace_packages(include=('encryptedsecrets', 'encryptedsecrets.*')),
    package_data={
        '': ['LICENSE'],
    },
    include_package_data=True,
    zip_safe=True,
    platforms='any',
    entry_points={
        'console_scripts': ['encrypted-secrets = encryptedsecrets.__main__:cli']
    },
    install_requires=[
        'encrypteddict',
        'pyyaml',
        'click'
    ],
    setup_requires=[
        'pytest-runner~=4.0',
    ],
    tests_require=[
        'encrypted-secrets[test]',
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-mock',
            'pytest-flake8',
        ],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
