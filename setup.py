#!/usr/bin/env python
import ast
import os
import re
import codecs

from setuptools import find_packages, setup

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
init = os.path.join(ROOT, "src", "strategy_field", "__init__.py")


_version_re = re.compile(r'__version__\s+=\s+(.*)')
_name_re = re.compile(r'NAME\s+=\s+(.*)')

with open(init, 'rb') as f:
    content = f.read().decode('utf-8')
    version = str(ast.literal_eval(_version_re.search(content).group(1)))
    name = str(ast.literal_eval(_name_re.search(content).group(1)))


def fread(*parts):
    return [l[:-1] for l in codecs.open(os.path.join(ROOT, *parts), encoding="utf-8").readlines() if l[0] != '#']

install_requires = fread('src/requirements', 'install.any.pip')
tests_require = fread('src/requirements', 'testing.pip')
dev_require = fread('src/requirements', 'develop.pip')

setup(
    name=name,
    version=version,
    url='https://github.com/saxix/django-strategy-field',
    description="Django custom field to implement the strategy pattern",
    long_description=open("README.rst").read(),
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
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers'
    ]
)
