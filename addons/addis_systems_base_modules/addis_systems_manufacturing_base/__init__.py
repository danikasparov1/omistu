from . import models
from . import controller


def _pre_init_hook(env):
    maintenance = env["ir.module.module"].sudo().search([("name", "=", "maintenance")])
    maintenance.button_install()