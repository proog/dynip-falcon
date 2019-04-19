import falcon
from .resources import IPResource
from .stores import SqliteStore, MySqlStore


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


def create_app(store, secret):
    print("Not using a secret" if secret is None else 'Using secret "%s"' % secret)

    app = falcon.API(media_type=falcon.MEDIA_TEXT)

    resource = IPResource(store, secret)
    app.add_route("/{name}", resource)

    return app
