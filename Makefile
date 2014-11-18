VERSION=2.1.0
MAIN_MODULE=wfp_auth
SETTINGS=wfp_auth.site.settings.testing
TEST_SETTINGS=wfp_auth.site.settings.testing
TEST_DBNAME=wfp_auth
BUILDDIR=~build
PYTHONPATH=${PWD}
DBENGINE?=postgres

DJANGO_14?='django>=1.4,<1.5'
DJANGO_15?='django>=1.5,<1.6'
DJANGO_16?='django>=1.6,<1.7'
DJANGO_17?='django>=1.7'
DJANGO_DEV?=git+git://github.com/django/django.git

PIP_VERSION=1.5.6
PIP_EXTRA_INDEX_URL=--extra-index-url=http://pypi.wfp.org/simple/
PIP_INSECURE_EXTERNALS= \
	--allow-external wfp-django-crashlog \
	--allow-external wfp-djangolib \
	--allow-external wfp-django-ldap \
	--allow-external wfp-djangosecurity \
	--allow-external wfp_commonlib \
	--allow-external wfp_auth \
	--allow-external cx-Oracle \
	--allow-unverified cx-Oracle


clean:
	# Cleaning..
	@rm -fr ${BUILDDIR} dist *.egg-info .coverage .pytest MEDIA_ROOT MANIFEST .cache *.egg build STATIC
	@find . -name __pycache__ -prune | xargs rm -rf
	@find . -name .cache -prune | xargs rm -rf
	@find . -name "*.py?" -prune | xargs rm -rf
	@find . -name "*.orig" -prune | xargs rm -rf
	@rm -f coverage.xml flake.out pep8.out pytest.xml coverage.xml


mkbuilddir:
	@mkdir -p ${BUILDDIR}


install-django:
	# installing Django==${DJANGO}
	#pip uninstall -y django
	@sh -c "if [ '${DJANGO}' = '1.4.x' ]; then pip install ${DJANGO_14}; fi"
	@sh -c "if [ '${DJANGO}' = '1.5.x' ]; then pip install ${DJANGO_15}; fi"
	@sh -c "if [ '${DJANGO}' = '1.6.x' ]; then pip install ${DJANGO_16}; fi"
	@sh -c "if [ '${DJANGO}' = '1.7.x' ]; then pip install ${DJANGO_17}; fi"
	@sh -c "if [ '${DJANGO}' = 'dev' ]; then pip install ${DJANGO_DEV}; fi"
	@echo "# installed  Django=="`django-admin.py --version`


install-deps:
	@pip install -q pip==${PIP_VERSION}
	@pip install --pre -qr ${MAIN_MODULE}/requirements/install.pip ${PIP_EXTRA_INDEX_URL} ${PIP_INSECURE_EXTERNALS}
	@pip install --pre -qr ${MAIN_MODULE}/requirements/testing.pip ${PIP_EXTRA_INDEX_URL} ${PIP_INSECURE_EXTERNALS}


test:
	py.test -vv ${MAIN_MODULE}


fullclean: clean
	find . -name *.sqlite -prune | xargs rm -rf
	rm -fr .tox


docs:
	sphinx-build -b html docs/ ~build/docs/ >/dev/null
	docs/intersphinx.py get ~build/docs/objects.inv -p ${MAIN_MODULE} -i docs/intershpinx.rst
	sphinx-build -n docs/ ~build/docs/
ifdef BROWSE
	firefox ${BUILDDIR}/docs/index.html
endif


coverage: mkbuilddir
	py.test tests -m "not integration" -x -vv --cov-report=html --cov-report=xml --junitxml=${BUILDDIR}/pytest.xml --cov-config=tests/.coveragerc --cov ${MAIN_MODULE}
ifdef BROWSE
	firefox ${BUILDDIR}/coverage/index.html
endif


pep8: mkbuilddir
	@pep8 ${MAIN_MODULE} | tee pep8.out


clonedigger: mkbuilddir
	clonedigger ${MAIN_MODULE} -l python -o ${BUILDDIR}/clonedigger.html --ignore-dir=migrations,tests --fast


flake: mkbuilddir
	@flake8 ${MAIN_MODULE} | tee ${BUILDDIR}/flake.out


setup-env: clean mkbuilddir install-django install-deps init-db


init-db:
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then mysql -e 'DROP DATABASE IF EXISTS ${TEST_DBNAME};'; fi"
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then mysql -e 'CREATE DATABASE IF NOT EXISTS ${TEST_DBNAME} COLLATE=utf8_general_ci;'; fi"
	@sh -c "if [ '${DBENGINE}' = 'mysql' ]; then pip install -q MySQL-python; fi"

	@sh -c "if [ '${DBENGINE}' = 'postgres' ]; then psql -c 'DROP DATABASE IF EXISTS ${TEST_DBNAME};' -U postgres; fi"
	@sh -c "if [ '${DBENGINE}' = 'postgres' ]; then psql -c 'CREATE DATABASE ${TEST_DBNAME};' -U postgres; fi"
	@sh -c "if [ '${DBENGINE}' = 'postgres' ]; then pip install -q psycopg2; fi"


ci_test: setup-env
	@${MAKE} coverage
	@${MAKE} flake pep8


.PHONY: docs

demo:
	django-admin.py syncdb --migrate --settings=tests.settings
	django-admin.py runserver --settings=tests.settings

rtd:
	curl -X POST http://readthedocs.wfp.org/build/wfp-django-auth


jenkins:
	git push && curl http://ci.wfp.org/job/wfp-auth/build?token=DJANGOAUTH_BUILD
