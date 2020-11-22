import os
import sys
import re


# SFTP connection settings
HOST = 'testhost'
PORT = 22
USER = ''
PASSWORD = ''

# Working directories
if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
    HOME = os.environ['HOME']
elif sys.platform.startswith('win'):
    HOME = os.environ['ALLUSERSPROFILE']
else:
    HOME = ''
WORKING_DIR = os.path.normpath(os.path.join(HOME, 'harvest'))
RAW_DIR = os.path.normpath(os.path.join(WORKING_DIR, 'raw'))
PROCESSED_DIR = os.path.normpath(os.path.join(WORKING_DIR, 'processed'))
REMOTE_DIR = ''

LOGFILE_MASK = '[a-zA-Z_-]*.log$'

TIME_PATTERNS = (
    '(?P<day>\d\d)-(?P<month>\d\d)-(?P<year>\d{4}).'
    '(?P<hour>\d\d):(?P<min>\d\d):(?P<sec>\d\d).(?P<ms>\d{3})',

    '(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d).'
    '(?P<hour>\d\d):(?P<min>\d\d):(?P<sec>\d\d).(?P<ms>\d{3})'
)
compiled_time_patterns = [re.compile(p) for p in TIME_PATTERNS]
