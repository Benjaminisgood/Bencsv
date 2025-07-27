from flask import Blueprint

budget_bp = Blueprint(
    'budget',
    __name__,
    url_prefix='/budget',
    template_folder='templates'  # ✅ 相对 modules/budget/
)

from . import routes