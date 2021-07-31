from flask import jsonify, request
from flask_jwt_extended import (create_access_token, create_refresh_token)

from app import redis
from core import db
from models import RefreshToken, LoginHistory


def auth_user(user):
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'roles': user.get_roles()
        }
    )
    refresh_token = create_refresh_token(identity=user.id)

    db.session.add(RefreshToken(user_id=user.id, token=refresh_token))
    # log to login history
    db.session.add(
        LoginHistory(
            user_id=user.id,
            user_agent=request.user_agent.string,
            ip_addr=request.remote_addr,
            user_device=request.user_agent.string
        )
    )
    db.session.commit()

    redis.delete(f"{user.id}-soa")

    return jsonify(access_token=access_token,
                   refresh_token=refresh_token,
                   msg="Signed in")