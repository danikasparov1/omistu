from odoo.http import Controller, route
from werkzeug.utils import redirect


DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'
DEFAULT_IMAGE = "/addis_systems_theme/static/src/img/login_page_bg.jpg"


class DashboardBackground(Controller):
    @route(["/dashboard"], type="http", auth="public")
    def dashboard(self, **post):
        return redirect(DEFAULT_IMAGE)



