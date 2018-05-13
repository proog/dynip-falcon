import falcon
import json
import redis
from datetime import datetime
from falcon import Request, Response, HTTPNotFound, HTTPBadRequest, HTTPUnauthorized


class Store:
    redis_prefix = "dynip:"

    def __init__(self, inmemory_store: dict, redis_store: redis.StrictRedis):
        self.inmemory = inmemory_store if inmemory_store is not None else {}
        self.redis = redis_store

        if redis_store is not None:
            try:
                redis_store.ping()
            except:
                print("Redis unavailable, falling back to in-memory store")
                self.redis = None

    def save(self, name, ip):
        info = {"ip": ip, "updated": datetime.utcnow().isoformat()}

        if self.redis is None:
            self.inmemory[name] = info
        else:
            self.redis.set(self.redis_prefix + name, json.dumps(info))

        return info

    def load(self, name):
        if self.redis is None:
            return self.inmemory.get(name)

        info = self.redis.get(self.redis_prefix + name)

        if info is not None:
            info = json.loads(info.decode("utf-8"))

        return info


def normalize_name(req, res, resource, params: dict):
    params["name"] = params["name"].lower().strip()


def validate_name(req, res, resource, params: dict):
    if len(params["name"]) == 0:
        raise HTTPBadRequest()


@falcon.before(normalize_name)
@falcon.before(validate_name)
class Resource:

    def __init__(self, store: Store, secret: str):
        self.store = store
        self.secret = secret

    def on_get(self, req: Request, res: Response, name: str):
        info = self.store.load(name)

        if info is None:
            raise HTTPNotFound()

        res.body = info["ip"]
        res.set_header("X-Updated", info["updated"])

    def on_put(self, req: Request, res: Response, name: str):
        secret_header = req.get_header("X-Secret")

        if self.secret is not None and secret_header != self.secret:
            print("PUT %s (invalid secret %s)" % (name, secret_header))
            raise HTTPUnauthorized()

        info = self.store.save(name, req.access_route[0])
        print("PUT %s = %s" % (name, info["ip"]))

        res.body = info["ip"]
        res.set_header("X-Updated", info["updated"])


def create_app(store, secret):
    app = falcon.API(media_type=falcon.MEDIA_TEXT)

    resource = Resource(store, secret)
    app.add_route("/{name}", resource)

    return app
