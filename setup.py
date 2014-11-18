#!/usr/bin/env python
import os
import codecs
from distutils.config import PyPIRCCommand
from setuptools import setup, find_packages

dirname = 'wfp_auth'

app = __import__(dirname)


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), 'r').read()


PyPIRCCommand.DEFAULT_REPOSITORY = 'http://pypi.wfp.org/pypi/'

tests_require = read('wfp_auth/requirements/testing.pip')

setup(
    name=app.NAME,
    version=app.get_version(),
    url='http://pypi.wfp.org/pypi/%s/' % app.NAME,
    author='UN World Food Programme',
    author_email='pasport.competence.centre@wfp.org',
    license="WFP Property",
    description='Django application auth ',
    long_description=read('README.md'),
    packages=find_packages('.'),
    include_package_data=True,
    dependency_links=['http://pypi.wfp.org/simple/'],
    install_requires=read('wfp_auth/requirements/install.pip'),
    tests_require=tests_require,
    keywords='security authentication authorization',
    platforms=['linux'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: Other/Proprietary License',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.5',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7c2',
        'Operating System :: Linux',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Django Modules',
    ],
    scripts=[])
