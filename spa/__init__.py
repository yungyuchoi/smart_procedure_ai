# Copyright 2020 Zinnotech, all rights reserved

"""
Library of components for the Zinnotech SPA implementation.
"""

__version__ = '0.1.0'
__pkgname__ = 'spa'

import locale
import logging
import os
import platform
import sys
from urllib.parse import urlparse
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

logger = logging.getLogger(__name__)


def add_basic_options(parser):
    parser.add_option("--version", action="store_true",
                      help="display the version")
    parser.add_option("--log", dest="log_file", metavar="LOG_FILE",
                      help="log file")
    parser.add_option("--log-dir", dest="log_dir", metavar="LOG_DIR",
                      help="log directory")
    parser.add_option("--debug", action="store_true",
                      help="emit extra diagnostic information")
    parser.add_option("--config", dest="config_file", metavar="CONFIG_FILE",
                      help="configuration file")


def add_db_options(parser, dbadm_opts=False):
    """add the standard db options to the command-line parser"""
    parser.add_option("--db-uri",
                      help="database connection parameters as a URI")
    parser.add_option("--db-host",
                      help="host name/address on which database is running")
    parser.add_option("--db-port", type=int,
                      help="port on which database server is listening")
    parser.add_option("--db-name",
                      help="name of the database")
    parser.add_option("--db-user",
                      help="database username")
    parser.add_option("--db-pass",
                      help="database password")
    if dbadm_opts:
        parser.add_option("--db-admin-user",
                          help="database administrative username")
        parser.add_option("--db-admin-pass",
                          help="database administrative password")


def platform_info():
    lines = ['SPA: %s' % __version__,
             'Python: %s' % sys.version.replace('\n', ' '),
             'Host: %s' % platform.node(),
             'Platform: %s' % platform.platform(),
             'Locale: %s' % locale.setlocale(locale.LC_ALL)]
    return lines


def prompt(prompt_str):
    ans = None
    while ans not in ['y', 'n']:
        ans = input(prompt_str)
    return ans


def get_dbinfo(db_host=None, db_port=None, db_name=None,
               db_user=None, db_pass=None, db_admuser=None, db_admpass=None,
               db_dict=dict(), db_uri=None,
               dbinfo_filename="~/.config/oms/dbinfo"):
    """
    get database connection information.  start with defaults.  override
    with whatever we find in the specified dbinfo file.  override that with
    anything in the db dictionary.  override that with any items specified
    in the URI.  override that with any items specified individually.
    """
    from spa.defaults import Defaults

    dbinfo = dict()
    for n in ['dbhost', 'dbport', 'dbname', 'dbuser', 'dbpass',
              'dbadmuser', 'dbadmpass']:
        dbinfo[n] = None

    dbinfo['dbhost'] = Defaults.DB_HOST
    dbinfo['dbport'] = Defaults.DB_PORT
    dbinfo['dbname'] = Defaults.DB_NAME
    # default to the user running this program, fallback to default oms user
    dbinfo['dbuser'] = os.environ.get('USER', Defaults.DB_USER)

    fn = os.path.abspath(os.path.expanduser(dbinfo_filename))

    try:
        with open(fn, 'r') as f:
            for line in f:
                i = line.find('#')
                if i >= 0:
                    line = line[0:i]
                if '=' in line:
                    name, value = line.split('=')
                    dbinfo[name.strip()] = value.strip()
    except IOError:
        pass

    if db_dict:
        dbinfo.update(db_dict)

    if db_uri:
        parts = parse_db_uri(db_uri)
        dbinfo.update(parts)

    if db_host is not None:
        dbinfo['dbhost'] = db_host
    if db_port is not None:
        dbinfo['dbport'] = db_port
    if db_user is not None:
        dbinfo['dbuser'] = db_user
    if db_pass is not None:
        dbinfo['dbpass'] = db_pass
    if db_name is not None:
        dbinfo['dbname'] = db_name
    if db_admuser is not None:
        dbinfo['dbadmuser'] = db_admuser
    if db_admpass is not None:
        dbinfo['dbadmpass'] = db_admpass
    return dbinfo


def parse_db_uri(uri):
    """
    Parse a database URI of the form:

    psql://[username[:password]@]host[:port]/database
    """
    dbinfo = dict()
    parts = urlparse(uri)
    if parts.scheme == 'psql':
        dbinfo['dbhost'] = parts.hostname
        if parts.port is not None:
            dbinfo['dbport'] = parts.port
        if parts.path:
            dbinfo['dbname'] = parts.path[1:]
        if parts.username:
            dbinfo['dbuser'] = parts.username
        if parts.password:
            dbinfo['dbpass'] = parts.password
    return dbinfo


def setup_logging(appname=None, appvers=None, debug=None, filename=None,
                  dirname=None, max_bytes=None, backup_count=None,
                  interval=None, log_dict=dict(), emit_platform_info=False):
    """Provide a sane set of defaults for logging.

    directory - where to put log files, current dir if nothing specified
    filename - the base name to use for the log file, appname if not specified
    max_bytes - when the log exceeds this size, the log will rotate
    interval - time in minutes
    backup_count - maximum number of files to retain

    Configure a rotating log file that rotates when the file size exceeds a
    specified number of bytes or when the time exceeds the specified interval.
    Then naming of the rotated files uses this pattern:

    filename.log
    filename.log.YYYY-mm-dd_HH-MM
    """

    # start with values from the dict, override with any specific arguments
    if debug is None:
        debug = to_bool(log_dict.get('debug', False))
    if filename is None:
        filename = log_dict.get('filename')
    if dirname is None:
        dirname = log_dict.get('directory')
    if max_bytes is None:
        max_bytes = int(log_dict.get('max_bytes', 10 * 1024 * 1024))  # 10 MB
    if interval is None:
        interval = int(log_dict.get('interval', 1440))  # 1 day
    if backup_count is None:
        backup_count = int(log_dict.get('backup_count', 30))

    # set the log level
    level = logging.DEBUG if debug else logging.INFO
    # if a log dir was specified, use it.  default to appname if no filename
    # was specified.
    if dirname is not None:
        if filename is None and appname is not None:
            filename = "%s.log" % appname
        if filename is not None:
            filename = os.path.join(dirname, filename)

    # otherwise, if a filename was specified, use it.  if not, we go to stdout.
    if filename is None:
        hand = logging.StreamHandler()
    else:
        hand = EnhancedRotatingFileHandler(filename=filename, when='M', interval=interval, maxBytes=max_bytes,
                                           backupCount=backup_count)

    fmt = '%(asctime)s.%(msecs)03d %(processName)s %(threadName)s %(name)s %(funcName)s: %(message)s' \
        if level == logging.DEBUG else '%(asctime)s.%(msecs)03d %(processName)s %(threadName)s %(message)s'
    datefmt = '%Y.%m.%d %H:%M:%S'
    hand.setFormatter(logging.Formatter(fmt, datefmt))

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = []
    root_logger.addHandler(hand)

    if emit_platform_info:
        if appname and appvers:
            logger.info('%s: %s' % (appname, appvers))
        for line in platform_info():
            logger.info(line)


class EnhancedRotatingFileHandler(TimedRotatingFileHandler, RotatingFileHandler):

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0,
                 encoding=None, delay=0, when='h', interval=1, utc=False):
        TimedRotatingFileHandler.__init__(
            self, filename, when, interval, backupCount, encoding, delay, utc)
        RotatingFileHandler.__init__(
            self, filename, mode, maxBytes, backupCount, encoding, delay)

    def computeRollover(self, currentTime):
        return TimedRotatingFileHandler.computeRollover(self, currentTime)

    def getFilesToDelete(self):
        return TimedRotatingFileHandler.getFilesToDelete(self)

    def doRollover(self):
        return TimedRotatingFileHandler.doRollover(self)

    def shouldRollover(self, record):
        """ Determine if rollover should occur. """
        return (TimedRotatingFileHandler.shouldRollover(self, record)
                or RotatingFileHandler.shouldRollover(self, record))


def read_config_file(filename):
    import configobj
    cfg = dict()
    try:
        cfg = configobj.ConfigObj(filename, file_error=True)
    except IOError as e:
        logger.error("cannot read configuration: %s" % e)
        raise
    return cfg


def to_bool(x):
    if x is None:
        return None
    if isinstance(x, str) and x.lower() == 'none':
        return None
    try:
        if x.lower() in ['true', 'yes', 't']:
            return True
        elif x.lower() in ['false', 'no', 'f']:
            return False
    except AttributeError:
        pass
    try:
        return bool(int(x))
    except (ValueError, TypeError):
        pass
    raise ValueError("Unknown boolean specifier: '%s'." % x)
