#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Script generates test data for reaper"""

import radar
import forgery_py
from datetime import date


DATE_FORMAT = '%d-%m-%Y'
DATETIME_FORMAT = DATE_FORMAT + ' %H:%M:%S.%f'
DATETIME_PARSE = [(DATETIME_FORMAT, True)]

LOG_FILES = ['A', 'B', 'C', 'D', 'E']
NUMBER_OF_LINES = 15


def test_parse(timestamp):
    return radar.utils.parse(timestamp, formats=DATETIME_PARSE)


def generate_test_logs():
    current_date = date.today().strftime(DATE_FORMAT)
    test_files = [f+'.log' for f in LOG_FILES]
    for test_file in test_files:
        f = open(test_file, 'wt')
        for _ in range(NUMBER_OF_LINES):
            r = radar.random_datetime(start=current_date+' 00:00:00.000000',
                                      stop=current_date+' 23:59:59.999999',
                                      parse=test_parse)
            f.write('{} -- {}\n'.format(r.strftime('%d-%m-%Y %H:%M:%S.%f'),
                                        forgery_py.lorem_ipsum.sentence()))
        f.close()


if __name__ == '__main__':
    generate_test_logs()
