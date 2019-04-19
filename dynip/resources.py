import falcon
from falcon import Request, Response, HTTPNotFound, HTTPBadRequest, HTTPUnauthorized
from .stores import Store


def normalize_name(req, res, resource, params: dict):
    params["name"] = params["name"].lower().strip()


def validate_name(req, res, resource, params: dict):
    l = len(params["name"])
    if l < 1 or l > 50:
        raise HTTPBadRequest()


@falcon.before(normalize_name)
@falcon.before(validate_name)
class IPResource:
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
