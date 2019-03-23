import os
import dotenv
from dynip import create_app
from stores import SqliteStore, MySqlStore


def create_store(config):
    if config["database"] == "mysql":
        print("Using MySQL")

        options = dict(config["mysql"])

        # pymysql can't deal with a port string
        if "port" in options:
            options["port"] = int(options["port"])

        return MySqlStore(**options)

    print("Using SQLite")
    return SqliteStore(**config["sqlite"])


dotenv.load_dotenv()
config = {
    "database": os.getenv("DYNIP_DATABASE", "sqlite"),
    "sqlite": {"database": os.getenv("DYNIP_SQLITE_DATABASE", "dynip.db")},
    "mysql": {
        "host": os.getenv("DYNIP_MYSQL_HOST", "127.0.0.1"),
        "port": os.getenv("DYNIP_MYSQL_PORT", "3306"),
        "database": os.getenv("DYNIP_MYSQL_DATABASE"),
        "user": os.getenv("DYNIP_MYSQL_USER"),
        "password": os.getenv("DYNIP_MYSQL_PASSWORD"),
        "charset": os.getenv("DYNIP_MYSQL_CHARSET", "utf8mb4"),
    },
}

store = create_store(config)
secret = os.getenv("DYNIP_SECRET")
print("Not using a secret" if secret is None else 'Using secret "%s"' % secret)

app = create_app(store, secret)
