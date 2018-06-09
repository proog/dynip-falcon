import os
import sqlite3
import mysql.connector
from configparser import ConfigParser
from dynip import create_app
from stores import SqliteStore, MySqlStore


def create_store(config):
    if config["dynip"]["database"] == "mysql":
        print("Using MySQL")
        return MySqlStore(mysql.connector.connect(**config["mysql"]))

    print("Using SQLite")
    return SqliteStore(sqlite3.connect(**config["sqlite"]))


env = os.getenv("DYNIP_ENVIRONMENT", "dev")
config = ConfigParser()
config.read("dynip.%s.ini" % env)

store = create_store(config)
secret = config["dynip"].get("secret")
print("Not using a secret" if secret is None else 'Using secret "%s"' % secret)

app = create_app(store, secret)
