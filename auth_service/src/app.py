from flask import redirect, request, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from api.v1.errors import bad_request, too_many
from core import Config, create_app

app = create_app()


@app.before_request
def before_request():
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        raise RuntimeError("request id is required")


@app.errorhandler(400)
def handle_bad_request(exc):
    return bad_request(exc.get_description())


@app.errorhandler(429)
def ratelimit_handler(e):
    return too_many("ratelimit exceeded %s" % e.description)


@app.route("/")
def hello():
    return redirect(url_for("api_v1.hello"))


if __name__ == "__main__":
    app.run(debug=True)
