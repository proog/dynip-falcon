import sqlite3
import mysql.connector
from datetime import datetime


class Store:

    def save(self, name, ip):
        raise NotImplementedError

    def load(self, name):
        raise NotImplementedError


class SqliteStore(Store):

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS ips (
                name text NOT NULL PRIMARY KEY,
                ip text NOT NULL,
                updated text NOT NULL
            )
            """
        )

    def save(self, name, ip):
        updated = datetime.utcnow().isoformat()

        sql = "REPLACE INTO ips (name, ip, updated) VALUES (?, ?, ?)"
        self.db.execute(sql, (name, ip, updated))
        self.db.commit()

        return {"ip": ip, "updated": updated}

    def load(self, name):
        sql = "SELECT ip, updated FROM ips WHERE name = ?"
        info = self.db.execute(sql, (name,)).fetchone()

        if info is not None:
            ip, updated = info
            return {"ip": ip, "updated": updated}

        return None


class MySqlStore(Store):

    def __init__(self, db: mysql.connector.MySQLConnection):
        self.db = db
        cursor = db.cursor()
        cursor.execute("SET NAMES utf8mb4")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ips (
                name varchar(50) NOT NULL PRIMARY KEY,
                ip varchar(50) NOT NULL,
                updated varchar(50) NOT NULL
            )
            """
        )
        cursor.close()

    def save(self, name, ip):
        updated = datetime.utcnow().isoformat()

        sql = "REPLACE INTO ips (name, ip, updated) VALUES (%s, %s, %s)"
        cursor = self.db.cursor()
        cursor.execute(sql, (name, ip, updated))
        self.db.commit()
        cursor.close()

        return {"ip": ip, "updated": updated}

    def load(self, name):
        sql = "SELECT ip, updated FROM ips WHERE name = %s"
        cursor = self.db.cursor()
        cursor.execute(sql, (name,))
        info = cursor.fetchone()
        self.db.commit()
        cursor.close()

        if info is not None:
            ip, updated = info
            return {"ip": ip, "updated": updated}

        return None
