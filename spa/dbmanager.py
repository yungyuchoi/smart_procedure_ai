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
        if mgr:
            mgr.db_conn.rollback()
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
        if mgr:
            mgr.db_conn.rollback()
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
            cur.execute('create database %s' % dbname)
        mgr.db_conn.commit()
    except psycopg2.Error as err:
        logger.error('creating database failed: %s' % str(err).strip())
        if mgr:
            mgr.db_conn.rollback()
    finally:
        if mgr:
            mgr.disconnect()


def drop_test_db(dbhost, dbport, dbname,
                         dbuser, dbpass, dbadmuser, dbadmpass):
    mgr = DBManager()
    try:
        mgr.connect(dbhost, dbport, 'postgres', dbadmuser, dbadmpass)
        mgr.db_conn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        with mgr.db_conn.cursor() as cur:
            cur.execute('drop database %s' % dbname)
        mgr.db_conn.commit()
    except psycopg2.Error as err:
        logger.error('dropping database failed: %s' % str(err).strip())
        if mgr:
            mgr.db_conn.rollback()
    finally:
        if mgr:
            mgr.disconnect()


def create_test_report_result(data, **kwargs):
    mgr = DBManager()
    try:
        mgr.connect(**kwargs)
        sql = """
            INSERT INTO report_result (report_id, step_id, task_id, action_id, result) VALUES %s"""
        data_iter = ((
            data[row]['report_id'],
            data[row]['step_id'],
            data[row]['task_id'],
            data[row]['action_id'],
            data[row]['result'],
        ) for row in data)
        mgr.modify_values(sql, data_iter, 1000)
    except psycopg2.Error as err:
        logger.error('creating test report_result test_data failed: %s' % str(err).strip())
        if mgr:
            mgr.db_conn.rollback()
    finally:
        if mgr:
            mgr.disconnect()


def create_test_report(data, **kwargs):
    mgr = DBManager()
    try:
        mgr.connect(**kwargs)
        sql = """
            INSERT INTO report ( id, guide_id, result ) VALUES %s"""
        data_iter = ((
            data[row]['report_id'],
            data[row]['guide_id'],
            data[row]['result'],
        ) for row in data)
        mgr.modify_values(sql, data_iter, 1000)
    except psycopg2.Error as err:
        logger.error('creating test report test_data failed: %s' % str(err).strip())
        if mgr:
            mgr.db_conn.rollback()
    finally:
        if mgr:
            mgr.disconnect()


def get_guide_fields(guide_id, **kwargs):
    mgr = DBManager()
    try:
        mgr.connect(**kwargs)
        with mgr.db_conn.cursor() as cur:
            sql = """
                    SELECT	ST.id AS step_id, TK.id AS task_id, AC.id AS action_id, TK.type
                    FROM	(
                                SELECT  id
                                FROM    guide
                                WHERE   id = {guide_id}
                            )	AS GD
                            JOIN step AS ST ON ST.guide_id = GD.id
                            JOIN (
                                SELECT  id, step_id, type
                                FROM    task
                                WHERE   is_analytics = True
                            ) AS TK ON TK.step_id = ST.id
                            JOIN task_action AS AC ON AC.task_id = TK.id
                    ORDER BY TK.step_id, TK.id, AC.id;
            """.format(guide_id=guide_id)
            rows = mgr.get_all_rows(sql)
            x = dict()
            if rows:
                for r in rows:
                    x[str(r[0]) + '_' + str(r[1]) + '_' + str(r[2])] = 0
            x['result'] = 0
            return x
    except psycopg2.Error as err:
        logger.error('selecting table failed: %s' % str(err).strip())
    finally:
        if mgr:
            mgr.disconnect()


def get_report_values(guide_id, **kwargs):
    mgr = DBManager()
    try:
        mgr.connect(**kwargs)
        with mgr.db_conn.cursor() as cur:
            sql = """
                SELECT  RR.report_id, RR.step_id, RR.task_id, RR.action_id
                        , CASE WHEN TP.TYPE = 'RADIO' OR TP.TYPE = 'CHECK' 
                        THEN ( CASE WHEN RR.result = 'true' THEN 1 ELSE 0 END )
                        ELSE CAST(RR.result AS FLOAT) END AS action_value
                FROM    report_result AS RR 
                        LEFT OUTER JOIN ( 
                            SELECT	id
                            FROM	report
                            WHERE	guide_id = {guide_id}
                        ) AS RE ON RR.report_id = RE.id
                        LEFT OUTER JOIN ( 
                            SELECT	ST.id AS step_id, TK.id AS task_id, AC.id AS action_id, TK.type
                            FROM	(
                                        SELECT  id
                                        FROM    guide
                                        WHERE   id = {guide_id}
                                    )	AS GD
                                    JOIN step AS ST ON ST.guide_id = GD.id
                                    JOIN (
                                        SELECT  id, step_id, type
                                        FROM    task
                                        WHERE   is_analytics = True
                                    ) AS TK ON TK.step_id = ST.id
                                    JOIN task_action AS AC ON AC.task_id = TK.id
                        ) AS TP ON  RR.step_id = TP.step_id
                                AND RR.task_id = TP.task_id
                                AND RR.action_id = TP.action_id
                WHERE RE.ID is not NULL
                ;	
            """.format(guide_id=guide_id)
            rows = mgr.get_all_rows(sql)
            x = dict()
            if rows:
                for r in rows:
                    try:
                        _ = x[r[0]]
                    except KeyError as e:
                        x[r[0]] = dict()
                    key = str(r[1]) + '_' + str(r[2]) + '_' + str(r[3])
                    x[r[0]][key] = r[4]
            return x
    except psycopg2.Error as err:
        logger.error('creating table failed: %s' % str(err).strip())
    finally:
        if mgr:
            mgr.disconnect()


def get_report_results(guide_id, **kwargs):
    mgr = DBManager()
    try:
        mgr.connect(**kwargs)
        with mgr.db_conn.cursor() as cur:
            sql = """
                SELECT	id, result
                FROM	report
                WHERE	guide_id = {guide_id}
                ;	
            """.format(guide_id=guide_id)
            rows = mgr.get_all_rows(sql)
            x = dict()
            if rows:
                for r in rows:
                    x[r[0]] = int(r[1])
            return x
    except psycopg2.Error as err:
        logger.error('creating table failed: %s' % str(err).strip())
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

    def modify_values(self, sql, iter, chunksize=1000):
        try:
            with self.db_conn.cursor() as cur:
                logger.debug("sql: %s" % sql)
                psycopg2.extras.execute_values(cur, sql, iter, page_size=chunksize)
        except psycopg2.Error as err:
            logger.error("query '%s' failed: %s" % ('', err))

    def get_all_rows(self, sql):
        try:
            with self.db_conn.cursor() as cur:
                logger.debug("sql: %s" % sql)
                cur.execute(sql)
                return cur.fetchall()
        except psycopg2.Error as err:
            logger.error("query '%s' failed: %s" % (sql, err))
