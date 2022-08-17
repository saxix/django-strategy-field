#!/usr/bin/env python
import ast
import os
import re

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
init = os.path.join(ROOT, 'src', 'strategy_field', '__init__.py')

_version_re = re.compile(r'__version__\s+=\s+(.*)')
_name_re = re.compile(r'NAME\s+=\s+(.*)')

with open(init, 'rb') as f:
    content = f.read().decode('utf-8')
    VERSION = str(ast.literal_eval(_version_re.search(content).group(1)))
    NAME = str(ast.literal_eval(_name_re.search(content).group(1)))

base_url = 'https://github.com/saxix/django-strategy-field/'


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        import sys

        sys.path.insert(0, os.path.join(ROOT, 'tests', 'demoapp'))
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name=NAME,
    version=VERSION,
    url='https://github.com/saxix/django-strategy-field',
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    long_description=open('README.rst').read(),
    license='MIT License',
    setup_requires=['pytest-runner', ],
    install_requires=(
        'pytz',
    ),
    extras_require={
        'drf': (
            'django-rest-framework',
        ),
        'test': (
            'coverage',
            'django_dynamic_fixture',
            'django-webtest',
            'factory-boy',
            'faker',
            'flake8',
            'isort',
            'pytest<7',
            'pytest-coverage',
            'pytest-django',
            'pytest-echo',
            'pytest-pythonpath>=0.7.4',
            'twine',
            'tox',
            'webtest',
        ),
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    # platforms=['any']
)
