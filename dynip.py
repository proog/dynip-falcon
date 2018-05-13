import falcon
import sqlite3
from datetime import datetime
from falcon import Request, Response, HTTPNotFound, HTTPBadRequest, HTTPUnauthorized


class Store:

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

        sql = "INSERT OR REPLACE INTO ips (name, ip, updated) VALUES (?, ?, ?)"
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
