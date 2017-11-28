# =================================================================
#
# Terms and Conditions of Use
#
# Unless otherwise noted, computer program source code of this
# distribution # is covered under Crown Copyright, Government of
# Canada, and is distributed under the MIT License.
#
# The Canada wordmark and related graphics associated with this
# distribution are protected under trademark law and copyright law.
# No permission is granted to use them outside the parameters of
# the Government of Canada's corporate identity program. For
# more information, see
# http://www.tbs-sct.gc.ca/fip-pcim/index-eng.asp
#
# Copyright title to all 3rd party software distributed with this
# software is held by the respective copyright holders as noted in
# those files. Users are asked to read the 3rd Party Licenses
# referenced with those assets.
#
# Copyright (c) 2017 Government of Canada
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

from collections import OrderedDict
from datetime import date, datetime, time
import logging
import os
import re
import sys

import click
from six import StringIO

__version__ = '0.1.2'

LOGGER = logging.getLogger(__name__)


def _get_value_type(field, value):
    """
    Derive true type from data value

    :param field: data field name
    :param value: data value

    :returns: value as a native Python data type
    """

    field2 = field.lower()
    value2 = None

    if value == '':  # empty
        return None

    if field2 == 'shadoz format data created':
        try:
            value2 = datetime.strptime(value, '%d, %B, %Y').date()
        except ValueError:
            value2 = datetime.strptime(value, '%d %B, %Y').date()
    elif field2 == 'launch date':
        value2 = datetime.strptime(value, '%Y%m%d').date()
    elif field2 == 'launch time (ut)':
        if ':' not in value:
            raise InvalidDataError('Bad Launch time')
        if 'GMT' in value:
            LOGGER.warning('Launch time seconds has GMT timezone')
        try:
            hms = [int(v) for v in value.replace('GMT', '').split(':')]
        except ValueError:
            LOGGER.debug('Launch time specifies microseconds')
            tmp, microseconds = value.split('.')
            hms = [int(v) for v in tmp.replace('GMT', '').split(':')]
            hms.append(int(microseconds))
        if len(hms) == 2:  # hh:mm
            LOGGER.warning('Launch time has no seconds')
            value2 = time(hms[0], hms[1])
        elif len(hms) == 3:  # hh:mm:ss
            value2 = time(hms[0], hms[1], hms[2])
        elif len(hms) == 4:  # hh:mm:ss.SSS
            value2 = time(hms[0], hms[1], hms[2], hms[3])
        else:
            raise InvalidDataError('Bad Launch time')
    else:
        try:
            if '.' in value:  # float?
                value2 = float(value)
            elif len(value) > 1 and value.startswith('0'):
                value2 = value
            else:  # int?
                value2 = int(value)
        except ValueError:  # string (default)?
                value2 = value

    return value2


class SHADOZ(object):
    """NASA SHADOZ object model"""

    def __init__(self, ioobj=None, version=5, filename=None):
        """
        Initialize a SHADOZ object

        :param ioobj: file or StringIO object
        :param version: SHADOZ version (default=5)

        :returns: pyshadoz.SHADOZ instance
        """

        self.version = None
        """SHADOZ version"""

        self.filename = filename
        """filename (optional)"""

        self.metadata = OrderedDict()
        """metadata fields"""

        self.data_fields = []
        """data fields"""

        self.data_fields_units = []
        """data field units"""

        self.data = []  # list of lists
        """list of lists of data lines"""

        if filename is not None:
            self.filename = os.path.basename(filename)

        if ioobj is None:  # serializer
            return

        filelines = ioobj.readlines()

        LOGGER.debug('Detecting if file is a SHADOZ file')
        is_shadoz = [s for s in filelines if 'SHADOZ Version' in s]
        if not is_shadoz:
            raise InvalidDataError('Unable to detect SHADOZ format')

        try:
            metadatalines = int(filelines[0])
        except ValueError:
            raise InvalidDataError('Invalid SHADOZ metadata lines value')

        LOGGER.debug('Parsing metadata')
        for metadataline in filelines[1:metadatalines-2]:
            try:
                key, value = [v.strip() for v in metadataline.split(': ', 1)]
                self.metadata[key] = _get_value_type(key, value)
            except ValueError:
                LOGGER.warning('No value found for {}'.format(key))
                self.metadata[key] = None

        if isinstance(self.metadata['SHADOZ Version'], str):
            self.version = float(self.metadata['SHADOZ Version'].split()[0])
        else:
            self.version = float(self.metadata['SHADOZ Version'])
        LOGGER.debug('Checking major version')
        if int(self.version) != int(version):
            raise InvalidDataError('Invalid SHADOZ version')

        LOGGER.debug('Parsing data fields')
        tmp = re.split(r'\s{2,}', filelines[metadatalines-2].strip())
        self.data_fields = [v.strip() for v in tmp]

        LOGGER.debug('Parsing data fields units')
        tmp = re.split(r'\s{2,}', filelines[metadatalines-1].strip())
        self.data_fields_units = [v.strip() for v in tmp]

        if len(self.data_fields) != len(self.data_fields_units):
            raise InvalidDataError(
                'Number of fields not equal to number of field units')

        LOGGER.debug('Parsing data')
        for dl in filelines[metadatalines:]:
            data = [_get_value_type('default', v) for v in dl.strip().split()]

            if len(data) != len(self.data_fields):
                raise InvalidDataError(
                    'Data length not equal to number of fields')

            self.data.append(data)

    def write(self):
        """
        SHADOZ writer

        :returns: SHADOZ data as string
        """

        lines = []

        line0 = len(self.metadata.keys()) + 3

        lines.append(str(line0))

        mwidth = max(map(len, self.metadata))

        for key, value in self.metadata.items():
            if key == 'SHADOZ format data created':
                value2 = value.strftime('%d %B, %Y')
            elif isinstance(value, time):
                value2 = value.strftime('%H:%M:%S')
            elif isinstance(value, datetime) or isinstance(value, date):
                value2 = value.strftime('%Y%m%d')
            else:
                value2 = value
            lines.append('{0: <{width}}: {value}'.format(key, width=mwidth,
                                                         value=value2))

        dfl = ' '.join([df.rjust(10) for df in self.data_fields])
        dfl = dfl.replace('      Time', 'Time')
        lines.append(dfl)

        dful = ' '.join([dfu.rjust(10) for dfu in self.data_fields_units])
        dful = dful.replace('      sec', 'sec')
        lines.append(dful)

        for data_ in self.data:
            dl = ' '.join([repr(d).rjust(10) for d in data_])
            dl.replace('     ', '')
            lines.append(dl)

        return '\n'.join([re.sub('^     ', '', l) for l in lines])

    def get_data_fields(self):
        """
        get a list of data fields and units

        :returns: list of tuples of data fields and associated units
        """

        return list(zip(self.data_fields, self.data_fields_units))

    def get_data(self, data_field=None, data_field_unit=None,
                 by_index=None):
        """
        get all data from a data field/data field unit

        :param data_field: data field name
        :param data_field_unit: data field name unit
        :param by_index: index of data in table


        :returns: list of lists of all data (default) or filtered by
                  field/unit or index
        """

        if by_index is not None:
            return [row[by_index] for row in self.data]

        if data_field is None and data_field_unit is None:  # return all data
            return self.data

        data_field_indexes = \
            [i for i, x in enumerate(self.data_fields) if x == data_field]

        if data_field_unit is None:  # find first match
            return [row[data_field_indexes[0]] for row in self.data]
        else:
            data_field_unit_indexes = \
                [i for i, x in enumerate(self.data_fields_units)
                 if x == data_field_unit]

            data_index = set(data_field_indexes).intersection(
                data_field_unit_indexes)

            if data_index:
                data_index2 = list(data_index)[0]
                return [row[data_index2] for row in self.data]
            else:
                raise DataAccessError('Data field/unit mismatch')

    def get_data_index(self, data_field, data_field_unit=None):
        """
        Get a data field's index

        :param data_field: data field name
        :param data_field_units: data field name unit

        :returns: index of data field/unit
        """

        data_field_indexes = \
            [i for i, x in enumerate(self.data_fields) if x == data_field]

        data_field_unit_indexes = \
            [i for i, x in enumerate(self.data_fields_units)
             if x == data_field_unit]

        if data_field_unit is None:
            return data_field_indexes[0]
        else:
            data_index = set(data_field_indexes).intersection(
                data_field_unit_indexes)

            if data_index:
                return list(data_index)[0]

    def __repr__(self):
        """repr function"""
        return '<SHADOZ (filename: {})>'.format(self.filename)


class DataAccessError(Exception):
    """Exception stub for invalid data access by data field/unit"""
    pass


class InvalidDataError(Exception):
    """Exception stub for format reading errors"""
    pass


def load(filename):
    """
    Parse SHADOZ data from from file
    :param filename: filename
    :returns: pyshadoz.SHADOZ object
    """

    with open(filename) as ff:
        return SHADOZ(ff, filename=filename)


def loads(strbuf):
    """
    Parse SHADOZ data from string
    :param strbuf: string representation of SHADOZ data
    :returns: pyshadoz.SHADOZ object
    """

    s = StringIO(strbuf)
    return SHADOZ(s)


@click.command()
@click.version_option(version=__version__)
@click.option('--file', '-f', 'file_',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to SHADOZ data file')
@click.option('--directory', '-d', 'directory',
              type=click.Path(exists=True, resolve_path=True,
                              dir_okay=True, file_okay=False),
              help='Path to directory of SHADOZ data files')
@click.option('--recursive', '-r', is_flag=True,
              help='process directory recursively')
@click.option('--verbose', '-v', is_flag=True, help='verbose mode')
def shadoz_info(file_, directory, recursive, verbose=False):
    """parse shadoz data file(s)"""

    if verbose:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        LOGGER.addHandler(ch)
    else:
        LOGGER.addHandler(logging.NullHandler())

    if file_ is not None and directory is not None:
        msg = '--file and --directory are mutually exclusive'
        raise click.ClickException(msg)

    if file_ is None and directory is None:
        msg = 'One of --file or --directory is required'
        raise click.ClickException(msg)

    files = []
    if directory is not None:
        if recursive:
            for root, dirs, files_ in os.walk(directory):
                for f in files_:
                    files.append(os.path.join(root, f))
        else:
            for files_ in os.listdir(directory):
                files.append(os.path.join(directory, files_))
    elif file_ is not None:
        files = [file_]

    for f in files:
        click.echo('Parsing {}'.format(f))
        with open(f) as ff:
            try:
                s = SHADOZ(ff, filename=f)
                click.echo('SHADOZ file: {}\n'.format(s.filename))
                click.echo('Metadata:')
                for key, value in s.metadata.items():
                    click.echo(' {}: {}'.format(key, value))
                click.echo('\nData:')
                click.echo(' Number of records: {}'.format(len(s.data)))
                click.echo(' Attributes:')
                for df in s.get_data_fields():
                    data_field_data = sorted(s.get_data(df[0], df[1]))
                    click.echo('  {} ({}): (min={}, max={})'.format(df[0],
                               df[1], data_field_data[0], data_field_data[-1]))
            except InvalidDataError as err:
                raise click.ClickException(str(err))
