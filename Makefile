########################################################

# Makefile for juicer
#
# useful targets (not all implemented yet!):
#   make clean               -- Clean up garbage
#   make pyflakes, make pep8 -- source code checks
#   make test ----------------- run all unit tests (export LOG=true for /tmp/ logging)

########################################################

# > VARIABLE = value
#
# Normal setting of a variable - values within it are recursively
# expanded when the variable is USED, not when it's declared.
#
# > VARIABLE := value
#
# Setting of a variable with simple expansion of the values inside -
# values within it are expanded at DECLARATION time.

########################################################


NAME := juicer
SHORTNAME := juicer
TESTPACKAGE := juicer

RPMSPECDIR := ./contrib/rpm/
RPMSPEC := $(RPMSPECDIR)/juicer.spec

PULPTAG := "2.6-release"
PULPDOCKERTAG := "pulp-docker-1.0.1-0.2.beta"

# VERSION file provides one place to update the software version.
VERSION := $(shell cat VERSION)

# Create sphinx docs
docs: conf.py
	cd docsite; make html; cd -

conf.py: docsite/source/conf.py.in
	sed "s/%VERSION%/$(VERSION)/" $< > docsite/source/conf.py

# Upload sources to pypi/pypi-test
pypi:
	python ./setup.py sdist upload

pypitest:
	python ./setup.py sdist upload -r test

sdist: clean __init__.py
	python setup.py sdist
	rm -fR $(SHORTNAME).egg-info

__init__.py: juicer/__init__.py.in
	sed "s/%VERSION%/$(VERSION)/" $< > juicer/__init__.py

virtualenv: __init__.py
	@echo "#############################################"
	@echo "# Creating a virtualenv"
	@echo "#############################################"
	virtualenv $(NAME)env
# Swig must be install at =< 3.0.4 for M2Crypto
	. $(NAME)env/bin/activate && pip install -r requirements.txt
# Install our unittest tools in the virtual env
	. $(NAME)env/bin/activate && pip install pep8 nose coverage mock
# Install pulp in the virtualenv, only clone if it doesn't exist
	if [ ! -d "pulp" ]; then git clone https://github.com/pulp/pulp.git; fi
	. $(NAME)env/bin/activate && cd pulp && git checkout $(PULPTAG)
	. $(NAME)env/bin/activate && cd pulp/bindings && pip install .
	. $(NAME)env/bin/activate && cd pulp/common && pip install .
# Install pulp_docker in the virtualenv, only clone if it doesn't exist
	if [ ! -d "pulp_docker" ]; then git clone https://github.com/pulp/pulp_docker.git; fi
	. $(NAME)env/bin/activate && cd pulp_docker && git checkout $(PULPDOCKERTAG)
	. $(NAME)env/bin/activate && cd pulp_docker/common && pip install .
# Install pyrpm in the virtualenv, only clone if it doesn't exist
	if [ ! -d "pyrpm" ]; then git clone https://github.com/02strich/pyrpm.git; fi
	. $(NAME)env/bin/activate && cd pyrpm && pip install .
# Install juicer in the virtual env
	. $(NAME)env/bin/activate && pip install .

ci-unittests:
	@echo "#############################################"
	@echo "# Running Unit Tests in virtualenv"
	@echo "#############################################"
	. $(NAME)env/bin/activate && nosetests -v --with-cover --cover-min-percentage=60 --cover-html --cover-package=$(TESTPACKAGE) test/
	@echo "#############################################"
	@echo "# UNIT TESTS RAN. HTML CODE COVERAGE RESULTS:"
	@echo "  % xdg-open ./cover/index.html"
	@echo "#############################################"

ci-list-deps:
	@echo "#############################################"
	@echo "# Listing all pip deps"
	@echo "#############################################"
	. $(NAME)env/bin/activate && pip freeze

ci-pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests in virtualenv"
	@echo "#############################################"
	. $(NAME)env/bin/activate && pep8 --ignore=E501,E121,E124 $(SHORTNAME)/

ci-pyflakes:
	@echo "#############################################"
	@echo "# Running Pyflakes Sanity Tests in virtualenv"
	@echo "# Note: most import errors may be ignored"
	@echo "#############################################"
	-. $(NAME)env/bin/activate && pyflakes $(SHORTNAME)


ci: clean virtualenv ci-list-deps ci-pyflakes ci-pep8 ci-unittests
	:


tests: unittests pep8 pyflakes
	:

unittests:
	@echo "#############################################"
	@echo "# Running Unit Tests"
	@echo "#############################################"
	nosetests -v --with-cover --cover-min-percentage=80 --cover-package=$(TESTPACKAGE) test/


clean:
	@find . -type f -regex ".*\.py[co]$$" -delete
	@find . -type f \( -name "*~" -or -name "#*" \) -delete
	@rm -fR build dist rpm-build MANIFEST htmlcov .coverage $(SHORTNAME).egg-info
	@rm -rf $(NAME)env cover
	@rm -fR docsite/build/html/ docsite/build/doctrees/

pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests"
	@echo "#############################################"
	pep8 --ignore=E501,E121,E124 $(SHORTNAME)/

pyflakes:
	@echo "#############################################"
	@echo "# Running Pyflakes Sanity Tests"
	@echo "# Note: most import errors may be ignored"
	@echo "#############################################"
	-pyflakes $(SHORTNAME)

rpmcommon: sdist
	@mkdir -p rpm-build
	@cp dist/*.gz rpm-build/

srpm: rpmcommon
	@rpmbuild --define "_topdir %(pwd)/rpm-build" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define "_specdir $(RPMSPECDIR)" \
	--define "_sourcedir %{_topdir}" \
	-bs $(RPMSPEC)
	@echo "#############################################"
	@echo "JUICER SRPM is built:"
	@find rpm-build -maxdepth 2 -name 'juicer*src.rpm' | awk '{print "    " $$1}'
	@echo "#############################################"

rpm: rpmcommon
	@rpmbuild --define "_topdir %(pwd)/rpm-build" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define "_specdir $(RPMSPECDIR)" \
	--define "_sourcedir %{_topdir}" \
	-ba $(RPMSPEC)
	@echo "#############################################"
	@echo "JUICER RPMs are built:"
	@find rpm-build -maxdepth 2 -name 'juicer*.rpm' | awk '{print "    " $$1}'
	@echo "#############################################"
