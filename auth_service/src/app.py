from flask import redirect, url_for

from core import create_app
from core.redis import get_redis
from api.v1.errors import bad_request

redis = get_redis()

app = create_app()

@app.errorhandler(400)
def handle_bad_request(exc):
    return bad_request(exc.description.messages)

@app.route("/")
def hello():
    return redirect(url_for("api_v1.hello"))


if __name__ == "__main__":
    app.run()
