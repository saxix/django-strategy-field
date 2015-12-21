#!/usr/bin/env python
import os
import sys
import codecs

from setuptools import find_packages, setup

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
app = __import__('strategy_field')


def fread(*parts):
    return codecs.open(os.path.join(ROOT, *parts), encoding="utf-8").read()

install_requires = fread('requirements', 'install.any.pip')
tests_require = fread('requirements', 'testing.pip')
dev_require = fread('requirements', 'develop.pip')

setup(
    name=app.NAME,
    version=app.get_version(),
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
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers'
    ]
)
