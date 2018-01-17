VERSION=2.1.0
BUILDDIR=build
PYTHONPATH=${PWD}
DBENGINE?=postgres

develop:
	pip install -e .[dev]

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


demo:
	cd tests/demo && ./manage.py syncdb
	cd tests/demo && ./manage.py runserver
