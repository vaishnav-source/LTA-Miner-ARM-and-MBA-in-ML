from flask import Blueprint

# Blueprint definition (must NOT specify template_folder)
rules_bp = Blueprint('rules', __name__)

from . import routes