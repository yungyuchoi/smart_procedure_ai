# Copyright 2020 Zinnotech, all rights reserved
"""
Database management utilities.

This file contains generic database interface definitions.
"""

import logging
import psycopg2
import psycopg2.extras
import psycopg2.extensions

from spa.schema import schema_def

logger = logging.getLogger(__name__)


def mkdbstr(dbhost, dbport, dbname, dbuser=None):
    if dbuser is not None:
        return "%s@%s:%s/%s" % (dbuser, dbhost, dbport, dbname)
    return "%s:%s/%s" % (dbhost, dbport, dbname)


def connect(dbhost, dbport, dbname, dbuser, dbpass):
    db_conn_info = "host=%s port=%s database=%s user=%s" % (
        dbhost, dbport, dbname, dbuser)
    logger.debug("db_conn=%s" % (db_conn_info))
    return psycopg2.connect(host=dbhost, port=dbport, database=dbname,
                            user=dbuser, password=dbpass, connect_timeout=5)


def clear_table(which_data='all', **kwargs):
    mgr = DBManager()
    try:
        mgr.connect(**kwargs)
        if which_data == 'all' or which_data == 'report_prediction':
            mgr.modify('DELETE FROM report_prediction')
        if which_data == 'all' or which_data == 'report_prediction_history':
            mgr.modify('DELETE FROM report_prediction_history')
    except psycopg2.Error as err:
        logger.error('clear failed: %s' % str(err).strip())
    finally:
        if mgr:
            mgr.disconnect()


def drop_table(**kwargs):
    mgr = DBManager()
    try:
        mgr.connect(**kwargs)
        mgr.modify('drop trigger if exists prediction_history on report_prediction')
        mgr.modify('drop function if exists report_prediction_trigger()')
        mgr.modify('drop table if exists report_prediction')
        mgr.modify('drop table if exists report_prediction_history')
        mgr.modify('drop sequence if exists report_prediction_history_seq')
    except psycopg2.Error as err:
        logger.error('clear failed: %s' % str(err).strip())
    finally:
        if mgr:
            mgr.disconnect()


def create_table(**kwargs):
    mgr = DBManager()
    try:
        mgr.connect(**kwargs)
        with mgr.db_conn.cursor() as cur:
            for sql in schema_def:
                logger.debug("execute sql:\n%s" % sql)
                cur.execute(sql)
        mgr.db_conn.commit()
    except psycopg2.Error as err:
        logger.error('create table failed: %s' % str(err).strip())
        if mgr:
            mgr.db_conn.rollback()
    finally:
        if mgr:
            mgr.disconnect()


def create_test_db(dbhost, dbport, dbname,
                        dbuser, dbpass, dbadmuser, dbadmpass):
    mgr = DBManager()
    logger.info("create database %s as user %s" %
                (mkdbstr(dbhost, dbport, dbname), dbadmuser))
    try:
        mgr.connect(dbhost, dbport, 'postgres', dbadmuser, dbadmpass)
        mgr.db_conn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        with mgr.db_conn.cursor() as cur:
            cur.execute('create database ai_test')
        mgr.db_conn.commit()
    except psycopg2.Error as err:
        logger.error('create database failed: %s' % str(err).strip())
        if mgr:
            mgr.db_conn.rollback()
    finally:
        if mgr:
            mgr.disconnect()


def drop_test_db(**kwargs):
    mgr = DBManager()
    try:
        mgr.connect(**kwargs)
        with mgr.db_conn.cursor() as cur:
            cur.execute('drop database ai_test')
        mgr.db_conn.commit()
    except psycopg2.Error as err:
        logger.error('drop database failed: %s' % str(err).strip())
        if mgr:
            mgr.db_conn.rollback()
    finally:
        if mgr:
            mgr.disconnect()


class DBManager(object):

    def __init__(self):
        self.uri = None
        self.db_conn = None

    def connect(self, dbhost, dbport, dbname, dbuser, dbpass=None, **kwargs):
        logger.debug("connect: %s@%s:%s/%s" % (dbuser, dbhost, dbport, dbname))
        self.uri = mkdbstr(dbhost, dbport, dbname, dbuser)
        self.db_conn = connect(dbhost, dbport, dbname, dbuser, dbpass)
        self.db_conn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    def disconnect(self):
        if self.db_conn is not None:
            logger.debug("disconnect from %s" % self.uri)
            self.db_conn.close()
            self.db_conn = None

    def modify(self, sql):
        try:
            with self.db_conn.cursor() as cur:
                logger.debug("sql: %s" % sql)
                cur.execute(sql)
        except psycopg2.Error as err:
            logger.error("query '%s' failed: %s" % (sql, err))
