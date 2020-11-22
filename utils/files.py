#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import random
import logging


class FileGenerator:
    """Class for file generation"""

    def __init__(self, path, create=True):
        """Get path of a directory, where files will be generated, and create
        it if needed

        :param path: directory path
        :param create: flag to autocreate directory if it does not exits
                       (default = True)

        :raise FileExistsError if path is a file
        :raise Exception when path does not exist and 'create' flag is False
        """
        self.path = os.path.normpath(str(path))
        logging.info('Got path: {}'.format(self.path))
        logging.info('Autocreation flag: {}'.format(create))
        if os.path.isfile(self.path):
            logging.error('Path refers to file: {}'.format(self.path))
            raise FileExistsError(
                'Path refers to file: {}'.format(self.path))
        elif os.path.isdir(self.path):
            logging.warning('Path already exists: {}'.format(self.path))
            pass
        else:
            if create:
                os.mkdir(self.path)
                logging.info('Directory created')
            else:
                logging.error('Path does not exist and autocreation flag '
                              'is {}: {}'.format(create, self.path))
                raise Exception('Path does not exist and autocreation flag '
                                'is {}: {}'.format(create, self.path))

    def generate(self, size, files):
        """Function to create files with random data (random integers from 0
        to 9)

        :param size: file size in bytes
        :param files: number of files

        :raise ValueError:
                   - file size < 0
                   - number of files < 1
        :raise IOError on file opening error
        :raise FileExistsError if file already exists
        """
        logging.info('Got parameters: {} file(s), {} byte(s) each'
                     ''.format(files, size))
        _size = int(size)
        _files = int(files)
        if _size < 0:
            logging.error('File size should be >= 0, not {}'.format(_size))
            raise ValueError('File size should be >= 0, not {}'.format(_size))
        if _files <= 0:
            logging.error('Files number should be > 0, not {}'.format(_files))
            raise ValueError(
                'Files number should be > 0, not {}'.format(_files))
        random.seed()
        logging.info('Generating files')
        for n in range(_files):
            _file = os.path.join(self.path, '{}-{}B'.format(n, _size))
            try:
                f = open(_file, 'x', encoding='utf-8')
            except IOError as e:
                logging.error('Fail - {} - {}'.format(_file, e))
                continue
            except FileExistsError:
                logging.error('Fail - {} - file already exists'.format(_file))
                continue
            [f.write(str(random.randint(0, 9))) for _ in range(_size)]
            f.close()
            logging.info('OK - {}'.format(_file))
        logging.info('File creation completed')


if __name__ == '__main__':
    FILESET = (
        # {'size': 0,        'files': 1},
        {'size': 1,        'files': 1},
        # {'size': 1024,     'files': 1},
        # {'size': 1024*300, 'files': 1},
        # {'size': 2**20,    'files': 1},
        # {'size': 2**20*5,  'files': 1},
        # {'size': 1024,     'files': 300},
    )
    PATH = ''

    filegen = FileGenerator(PATH)
    [filegen.generate(**params) for params in FILESET]
