VERSION=2.1.0
BUILDDIR=~build
PYTHONPATH=${PWD}
DBENGINE?=postgres

develop:
	pip install -e .[dev]


mkbuilddir:
	@mkdir -p ${BUILDDIR}

clean:
	rm -fr ${BUILDDIR} dist src/*.egg-info .coverage coverage.xml .eggs .pytest_cache *.log
	find src -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find tests -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf

fullclean:
	rm -fr .tox .cache DEMODB.sqlite
	$(MAKE) clean


demo:
	cd tests/demoapp && ./manage.py makemigrations
	cd tests/demoapp && ./manage.py migrate
	cd tests/demoapp && ./manage.py runserver
