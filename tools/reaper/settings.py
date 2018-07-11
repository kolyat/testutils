import os
import sys


# Connection settings
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
