# pyshadoz

[![Build Status](https://travis-ci.org/woudc/woudc-data-registry.png)](https://travis-ci.org/woudc/woudc-data-registry)
[![Coverage Status](https://coveralls.io/repos/github/woudc/woudc-data-registry/badge.svg?branch=master)](https://coveralls.io/github/woudc/woudc-data-registry?branch=master)

## Overview

WOUDC Data Registry is a platform that manages Ozone and Ultraviolet
Radiation data in support of the [World Ozone and Ultraviolet Radiation Data
Centre (WOUDC)](http://woudc.org), one of six World Data Centres as part of
the [Global Atmosphere Watch](http://www.wmo.int/gaw) programme of the
[WMO](http://www.wmo.int).


## Installation

### Requirements
- Python 3 and above
- [virtualenv](https://virtualenv.pypa.io/)

### Dependencies
Dependencies are listed in [requirements.txt](requirements.txt). Dependencies
are automatically installed during woudc-data-registry installation.

### Installing woudc-data-registry

```bash
# setup virtualenv
virtualenv --system-site-packages -p python3 woudc-data-registry
cd woudc-data-registry
source bin/activate

# clone codebase and install
git clone https://github.com/woudc/woudc-data-registry.git
cd woudc-data-registry
python setup.py build
python setup.py install

# set system environment variables
cp default.env foo.env
vi foo.env  # edit database connection parameters, etc.
. foo.env

# create database
make ENV=foo.env createdb

# drop database
make ENV=foo.env dropdb

# initialize model (database tables)
woudc-data-registry model setup

# cleanups

# re-initialize model (database tables)
woudc-data-registry model teardown
woudc-data-registry model setup

# drop database
make ENV=foo.env dropdb

```

### Running woudc-data-registry

```bash
# ingest directory of files (walks directory recursively)
woudc-data-registry data ingest -d /path/to/dir

# ingest single file
woudc-data-registry data ingest -f foo.dat

# verify directory of files (walks directory recursively)
woudc-data-registry data ingest -d /path/to/dir --verify

# verify single file
woudc-data-registry data ingest -f foo.dat --verify

```

### Running Tests

```bash
# install dev requirements
pip install -r requirements-dev.txt

# run tests like this:
cd woudc_data_registry/tests
python run_tests.py

# or this:
python setup.py test

# measure code coverage
coverage run --source=woudc_data_registry -m unittest woudc_data_registry.tests.run_tests
coverage report -m
```

### Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues are managed on [GitHub](https://github.com/woudc/woudc-data-registry/issues).

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)