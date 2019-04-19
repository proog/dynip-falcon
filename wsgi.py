import os
import dotenv
from dynip.app import create_app, create_store

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
secret = os.getenv("DYNIP_SECRET")

store = create_store(config)
application = create_app(store, secret)
