import os
from configparser import ConfigParser
from dynip import create_app
from stores import SqliteStore, MySqlStore


def create_store(config):
    if config["dynip"]["database"] == "mysql":
        print("Using MySQL")

        options = dict(config["mysql"])

        # pymysql can't deal with a port string
        if "port" in options:
            options["port"] = int(options["port"])

        return MySqlStore(**options)

    print("Using SQLite")
    return SqliteStore(**config["sqlite"])


env = os.getenv("DYNIP_ENVIRONMENT", "dev")
config = ConfigParser()
config.read("dynip.%s.ini" % env)

store = create_store(config)
secret = config["dynip"].get("secret")
print("Not using a secret" if secret is None else 'Using secret "%s"' % secret)

app = create_app(store, secret)
