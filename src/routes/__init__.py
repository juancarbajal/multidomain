from flask import Blueprint

routes_api = Blueprint('routes_api', __name__)

from .default import * 
