# Database.py
#
# performs all actions to support SQLITE database usage
# for PingTrend

import sqlite3
from sqlite3 import Error
import logging

logger = logging.getLogger(__name__)


class Database:

    def __init__(self, file):
        self.file = file
        try:
            self.conn = sqlite3.connect(self.file, isolation_level=None)   # autocommit
            self.cur = self.conn.cursor()
            logger.info(f"Opened {self.file} with SQL version {sqlite3.sqlite_version}")
        except Error as e:
            logger.error(f"Failed to connect to database {file}: {e}")
            raise

    def execute(self, sql):
        """Execute a SQL statement (INSERT, UPDATE, DELETE)."""
        try:
            logger.debug(f"Executing: {sql}")
            self.cur.execute(sql)
        except Error as e:
            logger.error(f"Execute failed: {e}")
            raise

    def insert(self, sql, values):
        """Insert data into database with parameter binding."""
        try:
            logger.debug(f"Inserting: {sql} with values {values}")
            self.cur.execute(sql, values)
        except Error as e:
            logger.error(f"Insert failed: {e}")
            raise

    def select(self, sql, params=None):
        """Query database and return results."""
        try:
            if params:
                logger.debug(f"Selecting: {sql} with params {params}")
                self.cur.execute(sql, params)
            else:
                logger.debug(f"Selecting: {sql}")
                self.cur.execute(sql)
        except Error as e:
            logger.error(f"Select failed: {e}")
            raise
        return self.cur.fetchall()

    def db_file(self):
        """Return the database file path."""
        return self.file

    def close(self):
        """Close database connection."""
        try:
            if self.cur:
                self.cur.close()
            if self.conn:
                self.conn.close()
            logger.info(f"Closed database: {self.file}")
        except Error as e:
            logger.error(f"Error closing database: {e}")
        finally:
            self.conn = None
            self.cur = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.close()
        return False
