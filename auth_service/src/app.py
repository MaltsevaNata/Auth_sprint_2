from flask import redirect, url_for, request

from core import create_app
from core.redis import get_redis
from api.v1.errors import bad_request

redis = get_redis()

app = create_app()


@app.before_request
def before_request():
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        raise RuntimeError("request id is required")

    
@app.errorhandler(400)
def handle_bad_request(exc):
    return bad_request(exc.description)


@app.route("/")
def hello():
    return redirect(url_for("api_v1.hello"))


if __name__ == "__main__":
    app.run(debug=True)
