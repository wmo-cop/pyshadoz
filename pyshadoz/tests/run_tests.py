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

from datetime import date, time
import os
import unittest

from pyshadoz import DataAccessError, InvalidDataError, load, loads, SHADOZ

THISDIR = os.path.dirname(os.path.realpath(__file__))


class SHADOZTest(unittest.TestCase):
    """Test suite for package shadoz"""
    def setUp(self):
        """setup test fixtures, etc."""

        pass

    def tearDown(self):
        """return to pristine state"""

        pass

    def test_read_shadoz(self):
        """test reading shadoz files or strings"""

        # test reading a non-shadoz file:
        with self.assertRaises(InvalidDataError):
            filename = get_abspath('non-shadoz-file.dat')
            with open(filename) as ff:
                s = SHADOZ(ff)

        with self.assertRaises(InvalidDataError):
            filename = get_abspath('hilo_20160223_V05.1_R-bad-line.dat')
            with open(filename) as ff:
                s = SHADOZ(ff)

        with self.assertRaises(InvalidDataError):
            filename = get_abspath('hilo_20160223_V05.1_R-no-version.dat')
            with open(filename) as ff:
                s = SHADOZ(ff)

        with self.assertRaises(InvalidDataError):
            filename = get_abspath('hilo_20160223_V05.1_R-bad-version.dat')
            with open(filename) as ff:
                s = SHADOZ(ff)

        with self.assertRaises(InvalidDataError):
            filename = get_abspath('hilo_20160223_V05.1_R-fields-mismatch.dat')
            with open(filename) as ff:
                s = SHADOZ(ff)

        filename = get_abspath('hilo_20160223_V05.1_R.dat')
        s = load(filename)

        with open(get_abspath('hilo_20160223_V05.1_R.dat')) as ff:
            s = SHADOZ(ff, filename='hilo_20160223_V05.1_R.dat')

            # test core properties
            self.assertEqual(s.filename, 'hilo_20160223_V05.1_R.dat')
            self.assertEqual(s.version, 5.1)

            # test metadata
            self.assertEqual(s.metadata['NASA/GSFC/SHADOZ Archive'],
                             'http://croc.gsfc.nasa.gov/shadoz')

            self.assertEqual(s.metadata['SHADOZ format data created'],
                             date(2017, 2, 2))

            self.assertEqual(s.metadata['Launch Time (UT)'], time(23, 18, 37))

            self.assertEqual(s.metadata['Latitude (deg)'], 19.43)

            self.assertEqual(s.metadata['Longitude (deg)'], -155.04)

            # test data fields and units
            df = ['Time', 'Press', 'Alt', 'Temp', 'RH', 'O3', 'O3', 'O3',
                  'W Dir', 'W Spd', 'T Pump', 'I O3', 'GPSLon', 'GPSLat',
                  'GPSAlt']

            self.assertEqual(len(s.data_fields), 15)
            self.assertEqual(s.data_fields, df)

            dfu = ['sec', 'hPa', 'km', 'C', '%', 'mPa', 'ppmv', 'du', 'deg',
                   'm/s', 'C', 'uA', 'deg', 'deg', 'km']

            self.assertEqual(len(s.data_fields_units), 15)
            self.assertEqual(s.data_fields_units, dfu)

            fields = s.get_data_fields()
            self.assertEqual(len(fields), 15)
            self.assertEqual(fields[0], ('Time', 'sec'))
            self.assertEqual(fields[-1], ('GPSAlt', 'km'))

            # test data
            data = s.get_data()
            self.assertEqual(len(data), 4342)
            self.assertEqual(data[0][4], 71.0)
            self.assertEqual(data[-1][2], 30.727)
            self.assertEqual(data[19][7], 1.415)

            # test data with field
            data = s.get_data(data_field='Press')
            self.assertEqual(max(data), 1013.85)
            self.assertEqual(min(data), 10.33)

            # test data with field and unit
            data = s.get_data(data_field='GPSLon', data_field_unit='deg')
            self.assertEqual(max(data), -154.389)
            self.assertEqual(min(data), -155.054)

            with self.assertRaises(DataAccessError):
                data = s.get_data(data_field='GPSLon', data_field_unit='foo')

            with open(get_abspath('hilo_20160223_V05.1_R-alt-date.dat')) as ff:
                s = SHADOZ(ff)

    def test_write_shadoz(self):
        """test writing shadoz files or strings"""

        s = SHADOZ()
        s.version = 5.1

        # build metadata dict
        s.metadata['NASA/GSFC/SHADOZ Archive'] = \
            'http://croc.gsfc.nasa.gov/shadoz'
        s.metadata['SHADOZ Version'] = 5.1
        s.metadata['SHADOZ format data created'] = date(2017, 2, 2)
        s.metadata['Launch Date'] = date(2016, 2, 23)
        s.metadata['Launch Time (UT)'] = time(23, 18, 37)

        # build data fields
        s.data_fields = ['Time', 'Press', 'Alt', 'Temp', 'RH', 'O3', 'O3',
                         'O3', 'W Dir', 'W Spd', 'T Pump', 'I O3', 'GPSLon',
                         'GPSLat', 'GPSAlt']

        # build data field units
        s.data_fields_units = ['sec', 'hPa', 'km', 'C', '%', 'mPa', 'ppmv',
                               'du', 'deg', 'm/s', 'C', 'uA', 'deg', 'deg',
                               'km']

        # build data
        s.data = [
            [0, 1013.85, 0.01, 24.22, 71.0, 32.91, 32.91, 0.0, 32.91, 5.29,
             32.91, 9000.0, -155.049, 19.717, 0.041],
            [0, 1013.66, 0.012, 23.89, 70.0, 32.79, 32.79, 0.049, 32.79, 5.01,
             32.79, 9000.0, -155.049, 19.717, 0.045]
        ]

        # serialize data
        shadoz_data = s.write()

        # test output
        s2 = loads(shadoz_data)
        self.assertEqual(s2.metadata['NASA/GSFC/SHADOZ Archive'],
                         'http://croc.gsfc.nasa.gov/shadoz')
        self.assertEqual(s2.data[0][1], 1013.85)
        self.assertEqual(s2.data[-1][-2], 19.717)
        self.assertEqual(s2.data[1][-1], 0.045)
        self.assertEqual(s2.metadata['SHADOZ format data created'],
                         date(2017, 2, 2))
        self.assertEqual(s2.metadata['Launch Date'],
                         date(2016, 2, 23))
        self.assertEqual(s2.metadata['Launch Time (UT)'], time(23, 18, 37))


def get_abspath(filepath):
    """helper function absolute file access"""

    return os.path.join(THISDIR, filepath)


if __name__ == '__main__':
    unittest.main()
