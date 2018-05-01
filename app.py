import redis
import os
from dynip import create_app, Store

store = Store({}, redis.StrictRedis())

secret = os.getenv("DYNIP_SECRET")
print("Not using a secret" if secret is None else 'Using secret "%s"' % secret)

app = create_app(store, secret)
