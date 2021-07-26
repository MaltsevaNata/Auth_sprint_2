from flask import Blueprint

bp = Blueprint("api_v1", __name__)

from . import user_administration
from . import role_administration
from . import two_fa
