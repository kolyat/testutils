#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import stat
import shutil
import re
import datetime
import logging
import paramiko
from paramiko import ssh_exception

from . import settings


def rm_readonly(fun, path, _):
    """Clear the readonly bit and reattempt directory removal
    """
    os.chmod(path, stat.S_IWRITE)
    fun(path)


class TransportError(Exception):
    """Exception class for Transport errors"""
    pass


class Transport:
    """Class for establishing SFTP session and file download"""

    def __init__(self):
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._transport = None
        self._sftp = None

    def connect(self, host=settings.HOST, port=settings.PORT,
                user=settings.USER, password=settings.PASSWORD):
        """Connect to server

        :param host: host name
        :param port: SFTP port
        :param user: username
        :param password: password

        :raise TransportError on client exception
        """
        logging.info('Connecting to {}@{}:{}'.format(user, host, port))
        try:
            self._client.connect(hostname=host, port=port,
                                 username=user, password=password)
            logging.info('Connected successfully')
        except ssh_exception.BadHostKeyException as e:
            logging.error(
                'Connection error - {}@{}:{} - '
                'server’s host key could not be verified: {}'.format(
                    user, host, port, e)
            )
            raise TransportError('Server’s host key could not be verified', e)
        except ssh_exception.AuthenticationException as e:
            logging.error(
                'Connection error - {}@{}:{} - authentication failure: {}'
                ''.format(user, host, port, e)
            )
            raise TransportError('Authentication failure', e)
        except (ssh_exception.SSHException,
                ssh_exception.NoValidConnectionsError) as e:
            logging.error(
                'Connection error - {}@{}:{} - connection failure: {}'
                ''.format(user, host, port, e)
            )
            raise TransportError('Connection failure', e)
        logging.info('Setting up SFTP session')
        self._transport = self._client.get_transport()
        try:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            logging.info('SFTP session established')
        except paramiko.SSHException as e:
            logging.error(
                '{}@{}:{} - SFTP session failure: {}'
                ''.format(user, host, port, e)
            )
            raise TransportError('SFTP session failure', e)

    def disconnect(self):
        """Disconnect from server
        """
        try:
            self._sftp.close()
            logging.info('SFTP session closed')
        except AttributeError:
            pass
        try:
            self._client.close()
            logging.info('Connection to server closed')
        except AttributeError:
            pass

    def download(self, source_dir=settings.REMOTE_DIR,
                 dest_dir=settings.RAW_DIR, mask=settings.LOGFILE_MASK):
        """Download files specified by mask

        :param source_dir: remote directory path
        :param dest_dir: local directory path
        :param mask: file mask

        :return: list with filename and download result
        """
        logging.info('Download files')
        logging.info('Source: {}'.format(source_dir))
        logging.info('Destination: {}'.format(dest_dir))
        logging.info('Mask: {}'.format(mask))
        remote_dir = self._sftp.normalize(source_dir)
        files = self._sftp.listdir(remote_dir)
        logging.info('All files: {}'.format(files))
        log_files = filter(lambda f: re.match(mask, f), files)
        logging.info('Log files: {}'.format(log_files))
        for l in log_files:
            result = [l]
            try:
                self._sftp.get(os.path.join(remote_dir, l),
                               os.path.join(dest_dir, l))
                result.append('OK')
                logging.info('OK - {}'.format(l))
            except IOError:
                result.append('Fail')
                logging.error('Failed - {}'.format(l))
            finally:
                yield result
        logging.info('Download completed')

    def __del__(self):
        self.disconnect()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Selection pattern for log strings is not defined')
        sys.exit(1)

    print('Reaper is coming')
    # Prepare working directories
    access_bits = stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO
    print('Preparing working directories... ')
    if os.path.exists(settings.WORKING_DIR):
        shutil.rmtree(settings.WORKING_DIR, onerror=rm_readonly)
        print('Removed {}'.format(settings.WORKING_DIR))
    os.mkdir(settings.WORKING_DIR, access_bits)
    print('Created {}'.format(settings.WORKING_DIR))
    os.mkdir(settings.RAW_DIR, access_bits)
    print('Created {}'.format(settings.RAW_DIR))
    os.mkdir(settings.PROCESSED_DIR, access_bits)
    print('Created {}'.format(settings.PROCESSED_DIR))
    print('Done')

    # Download log files
    transport = Transport()
    print('Connecting to {}@{}:{} ... '.format(settings.USER, settings.HOST,
                                               settings.PORT), end='')
    try:
        transport.connect()
        print('Success')
        print('Downloading log files')
        [print('    {:.<30}...{}'.format(*r)) for r in transport.download()]
        print('Done')
    except TransportError as err:
        print('Failed')
        print(err)
    finally:
        transport.disconnect()

    # Filter raw logs
    print('Will refine harvest: {}'.format(settings.RAW_DIR))
    raw_logs = os.listdir(settings.RAW_DIR)
    for raw_log in raw_logs:
        print('    {:.<30}...'.format(raw_log), end='')
        source = open(os.path.join(settings.RAW_DIR, raw_log), 'rt')
        destination = open(os.path.join(settings.PROCESSED_DIR, raw_log), 'wt')
        [destination.write(line) for line in source if sys.argv[1] in line]
        destination.close()
        source.close()
        print('Done')

    # Delete all empty files from processed directory
    print('Clean up: delete all empty files from {}'.format(
        settings.PROCESSED_DIR))
    processed_logs = os.listdir(settings.PROCESSED_DIR)
    for file in processed_logs:
        print('    {:.<30}...'.format(file), end='')
        if os.path.getsize(os.path.join(settings.PROCESSED_DIR, file)) == 0:
            os.remove(os.path.join(settings.PROCESSED_DIR, file))
            print('Deleted')
        else:
            print('Skipped')

    # Begin reconstruction
    rfilepath = os.path.join(settings.WORKING_DIR, 'reconstructed.htm')
    print('Will now reconstruct to {}'.format(rfilepath))
    processed_files = os.listdir(settings.PROCESSED_DIR)
    if not processed_files:
        print('No refined logs are available')
        sys.exit(2)
    log_items = list()
    for processed_file in processed_files:
        pf = open(os.path.normpath(os.path.join(
            settings.PROCESSED_DIR, processed_file)), 'rt')
        for line in pf:
            for p in settings.compiled_time_patterns:
                r = p.search(line)
                if r:
                    timestamp = datetime.datetime(
                        int(r.group('year')), int(r.group('month')),
                        int(r.group('day')), int(r.group('hour')),
                        int(r.group('min')), int(r.group('sec')),
                        int(r.group('ms')) * 1000
                    ).timestamp()
                    log_items.append(
                        (timestamp, processed_file, line.replace('\n', '')))
                    break
        pf.close()
    sorted_items = sorted(log_items, key=lambda _item: _item[0])
    # Open output file
    reconstructed_file = open(rfilepath, 'wt')
    reconstructed_file.write("""<!DOCTYPE html>
<html>
<body>
<style type='text/css'>
  table, td {
    border: 0px;
  }
  table {
    font-family: sans-serif;
    font-size: 75%;
  }
  td {
    padding: 5px;
    text-align: left;
    vertical-align: top;
  }
</style>
<table>\n""")
    for item in sorted_items:
        reconstructed_file.write("""  <tr style='color:black;'>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
  </tr>\n""".format(*item))
    # Close output file and finish
    reconstructed_file.write('</table>\n</body>\n</html>\n')
    reconstructed_file.close()
    print('Reconstruction completed')
    print('Reaper is fading away')
    sys.exit(0)
