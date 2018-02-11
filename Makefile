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


docs:
	sphinx-build -b html docs/ ~build/docs/ >/dev/null
	docs/intersphinx.py get ~build/docs/objects.inv -p ${MAIN_MODULE} -i docs/intershpinx.rst
	sphinx-build -n docs/ ~build/docs/
ifdef BROWSE
	firefox ${BUILDDIR}/docs/index.html
endif


demo:
	cd tests/demo && ./manage.py syncdb
	cd tests/demo && ./manage.py runserver
