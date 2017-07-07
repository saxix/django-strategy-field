#!/usr/bin/env python
import os
import re
import codecs

from setuptools import find_packages, setup

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
init = os.path.join(ROOT, "src", "strategy_field", "__init__.py")

def get_version(*file_paths):
    """Retrieves the version from django_mb/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = [\"]([^\"]*)[\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def fread(*parts):
    return [l[:-1] for l in codecs.open(os.path.join(ROOT, *parts), encoding="utf-8").readlines() if l[0] != '#']

install_requires = fread('src/requirements', 'install.any.pip')
tests_require = fread('src/requirements', 'testing.pip')
dev_require = fread('src/requirements', 'develop.pip')

setup(
    name='django-strategy-field',
    version=get_version(init),
    url='https://github.com/saxix/django-strategy-field',
    description="Django custom field to implement the strategy pattern",
    author='sax',
    author_email='sax@os4d.org',
    license='BSD',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    extras_require={
        'tests': tests_require,
        'dev': dev_require + tests_require,
    },
    platforms=['linux'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers'
    ]
)
