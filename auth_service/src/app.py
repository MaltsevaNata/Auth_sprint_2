from flask import redirect, url_for, request

from core import create_app, Config
from core.bucket import Bucket
from core.redis import get_redis
from api.v1.errors import bad_request, too_many

redis = get_redis()
bucket = Bucket(
        key=Config.BUCKET_KEY,
        rate=Config.BUCKET_RATE,
        capacity=Config.BUCKET_CAPACITY,
        storage=redis
    )
app = create_app()


@app.before_request
def before_request():
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        raise RuntimeError("request id is required")

    
@app.errorhandler(400)
def handle_bad_request(exc):
    return bad_request(exc.get_description())


@app.before_request
def rate_limit():
    if not bucket.consume():
        return too_many("Too Many Requests")


@app.route("/")
def hello():
    return redirect(url_for("api_v1.hello"))


if __name__ == "__main__":
    app.run(debug=True)
