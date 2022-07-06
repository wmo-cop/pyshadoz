# pyshadoz

[![Build Status](https://github.com/wmo-cop/pyshadoz/workflows/build%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/wmo-im/pyshadoz/actions)

## Overview

pyshadoz is a pure Python package to read and write [NASA Southern Hemisphere
ADditional OZonesondes](https://tropo.gsfc.nasa.gov/shadoz/) (SHADOZ) data.


## Installation

The easiest way to install pyshadoz is via the Python [pip](https://pip.pypa.io/en/stable/)
utility:

```bash
pip3 install pyshadoz
```

### Requirements
- Python 3
- [virtualenv](https://virtualenv.pypa.io/)

### Dependencies
Dependencies are listed in [requirements.txt](requirements.txt). Dependencies
are automatically installed during pyshadoz installation.

### Installing pyshadoz

```bash
# setup virtualenv
virtualenv --system-site-packages -p python3 pyshadoz
cd pyshadoz
source bin/activate

# clone codebase and install
git clone https://github.com/wmo-cop/pyshadoz.git
cd pyshadoz
python3 setup.py build
python3 setup.py install
```

## Running

```bash
# help
pyshadoz --help

# get version
pyshadoz --version

# parse a single shadoz file
pyshadoz -f </path/to/shadoz_file>

# add verbose mode
pyshadoz -v -f </path/to/shadoz_file>

# parse a directory of shadoz files
pyshadoz -d </path/to/directory>

# parse a directory of shadoz files recursively
pyshadoz -r -d </path/to/directory>
```

### Using the API
```python
from pyshadoz import SHADOZ

# read SHADOZ data
with open('/path/to/directory') as ff:
    s = SHADOZ(ff)

    for key, value in s.metadata:
        print(key, value)

    print(s.data_fields)
    print(s.data_fields_units)
    print(len(s.data))

    # get index of a data field
    index = s.get_data_index('W Dir')

    # get index of a data field and data field unit
    index = s.get_data_index('W Dir', 'deg')

    # get all data
    data = s.get_data()

    # get data by index
    data = s.get_data(by_index=index)

    # get all data by field
    data = s.get_data('W Spd')

    # get all data by field and unit
    data = s.get_data('O3', 'ppmv')

# read SHADOZ data using convenience functions
# parse file
s = load('/path/to/shadoz_file.dat')  # returns SHADOZ object

# parse string
with open('/path/to/shadoz_file.dat') as ff:
    shadoz_string = ff.read()
s = loads(shadoz_string)  # returns SHADOZ object

# write SHADOZ data
s = SHADOZ()
# build metadata dict
s.metadata['NASA/GSFC/SHADOZ Archive'] = 'http://croc.gsfc.nasa.gov/shadoz'
....
# build data fields
s.data_fields = ['Time', 'Press', 'Alt', 'Temp', 'RH', 'O3', 'O3', 'O3',
                 'W Dir', 'W Spd', 'T Pump', 'I O3', 'GPSLon', 'GPSLat',
                 'GPSAlt']

# build data field units
s.data_fields_units = ['sec','hPa','km', 'C', '%', 'mPa', 'ppmv', 'du', 'deg',
                       'm/s', 'C', 'uA', 'deg', 'deg', 'km']

# build data
s.data = [
    [0, 1013.85, 0.01, 24.22, 71.0, 32.91, 32.91, 0.0, 32.91, 5.29, 32.91, 9000.0, -155.049, 19.717, 0.041],
    [0, 1013.66, 0.012, 23.89, 70.0, 32.79, 32.79, 0.049, 32.79, 5.01, 32.79, 9000.0, -155.049, 19.717, 0.045]
]

# serialize data to file
shadoz_data = s.write()
with open('new_shadoz_file.dat', 'w') as ff:
    ff.write(shadoz_data)
```

## Development

### Running Tests

```bash
# install dev requirements
pip3 install -r requirements-dev.txt

# run tests like this:
python3 pyshadoz/tests/run_tests.py

# or this:
python3 setup.py test
```

## Releasing

```bash
python3 setup.py sdist bdist_wheel --universal
twine upload dist/*
```

### Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues are managed on [GitHub](https://github.com/wmo-cop/pyshadoz/issues).

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
