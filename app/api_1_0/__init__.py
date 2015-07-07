from flask import Blueprint
api = Blueprint('api', __name__)

from . import test
from . import token
from . import user
from . import profile
from . import like_and_match
from . import admin