import redis
import os
import sqlite3
from dynip import create_app, Store

store = Store(sqlite3.connect("dynip.db"), redis.StrictRedis())

secret = os.getenv("DYNIP_SECRET")
print("Not using a secret" if secret is None else 'Using secret "%s"' % secret)

app = create_app(store, secret)
