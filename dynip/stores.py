import sqlite3
import pymysql
from datetime import datetime


class Store:
    def save(self, name, ip):
        raise NotImplementedError

    def load(self, name):
        raise NotImplementedError


class SqliteStore(Store):
    def __init__(self, **options):
        self.db_options = options

        db = self._connect()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS ips (
                name text NOT NULL PRIMARY KEY,
                ip text NOT NULL,
                updated text NOT NULL
            )
            """
        )
        db.commit()
        db.close()

    def save(self, name, ip):
        updated = datetime.utcnow().isoformat()

        db = self._connect()
        sql = "REPLACE INTO ips (name, ip, updated) VALUES (?, ?, ?)"
        db.execute(sql, (name, ip, updated))
        db.commit()
        db.close()

        return {"ip": ip, "updated": updated}

    def load(self, name):
        db = self._connect()
        sql = "SELECT ip, updated FROM ips WHERE name = ?"
        info = db.execute(sql, (name,)).fetchone()
        db.close()

        if info is not None:
            ip, updated = info
            return {"ip": ip, "updated": updated}

        return None

    def _connect(self):
        return sqlite3.connect(**self.db_options)


class MySqlStore(Store):
    def __init__(self, **options):
        self.db_options = options

        db = self._connect()
        with db.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ips (
                    name varchar(50) NOT NULL PRIMARY KEY,
                    ip varchar(50) NOT NULL,
                    updated varchar(50) NOT NULL
                )
                """
            )
        db.close()

    def save(self, name, ip):
        updated = datetime.utcnow().isoformat()

        db = self._connect()
        with db.cursor() as cursor:
            sql = "REPLACE INTO ips (name, ip, updated) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, ip, updated))
        db.commit()
        db.close()

        return {"ip": ip, "updated": updated}

    def load(self, name):
        db = self._connect()
        with db.cursor() as cursor:
            sql = "SELECT ip, updated FROM ips WHERE name = %s"
            cursor.execute(sql, (name,))
            info = cursor.fetchone()
        db.close()

        if info is not None:
            ip, updated = info
            return {"ip": ip, "updated": updated}

        return None

    def _connect(self):
        return pymysql.connect(**self.db_options)
