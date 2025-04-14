{
    "name": "Addis Systems Theme",
    "version": "17.0.1.0",
    "sequence": 1,
    "summary": "Addis Systems Theme",
    "description": """
        This is a Theme for Addis Systems Instances.
            ========================================
    """,
    "category": "Addis Systems/Base",
    "author": "Addis Systems/Beruk W.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["base", "base_setup", "web", "web_editor"],
    "data": [
        "security/ir.model.access.csv",
        "static/templates/webclient.xml",
        "views/AddisSystemsLoginPageBackgroundImage.xml",
        "views/AddisSystemsEthiopiaAddressAdjustmentView.xml",
        "reports/AddisSystemsReportLayout.xml",
        "data/AddisSystemsThemeData.xml",
        "data/AddisSystemsBaseForEthiopiaAdjustments.xml"
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'addis_systems_theme/static/src/scss/colors.scss'),
            (
                'before',
                'addis_systems_theme/static/src/scss/colors.scss',
                'addis_systems_theme/static/src/scss/colors_light.scss'
            ),
            (
                'after',
                'web/static/src/scss/primary_variables.scss',
                'addis_systems_theme/static/src/scss/colors.scss'
            ),
            (
                'after',
                'web/static/src/scss/primary_variables.scss',
                'addis_systems_theme/static/src/scss/variables.scss'
            )
        ],
        'web._assets_backend_helpers': [
            'addis_systems_theme/static/src/scss/mixins.scss',
        ],
        'web.assets_web_dark': [
            (
                'after',
                'addis_systems_theme/static/src/scss/colors.scss',
                'addis_systems_theme/static/src/scss/colors_dark.scss'
            ),
            (
                'after',
                'addis_systems_theme/static/src/scss/variables.scss',
                'addis_systems_theme/static/src/scss/variables.dark.scss',
            ),
        ],
        'web.assets_backend': [
            (
                'after',
                'web/static/src/webclient/webclient.js',
                'addis_systems_theme/static/src/webclient/webclient.js',
            ),
            (
                'after',
                'web/static/src/webclient/webclient.xml',
                'addis_systems_theme/static/src/webclient/webclient.xml',
            ),
            (
                'after',
                'web/static/src/webclient/webclient.js',
                'addis_systems_theme/static/src/webclient/menus/app_menu_service.js',
            ),
            'addis_systems_theme/static/src/webclient/user_menu/*.js',
            'addis_systems_theme/static/src/webclient/appsbar/*.xml',
            'addis_systems_theme/static/src/webclient/appsbar/*.scss',
            'addis_systems_theme/static/src/webclient/appsbar/*.js',
            'addis_systems_theme/static/src/webclient/appsmenu/*.xml',
            'addis_systems_theme/static/src/webclient/appsmenu/*.scss',
            'addis_systems_theme/static/src/webclient/appsmenu/*.js',
            'addis_systems_theme/static/src/webclient/navbar/*.xml',
            'addis_systems_theme/static/src/webclient/navbar/*.scss',
            'addis_systems_theme/static/src/webclient/navbar/*.js',
            'addis_systems_theme/static/src/views/**/*.scss',
            "addis_systems_theme/static/src/js/web_window_title.js",
            "addis_systems_theme/static/src/js/chart.umd.min.js",
            "addis_systems_theme/static/src/base/**/*.xml",
            "addis_systems_theme/static/src/base/**/*.scss",
            "addis_systems_theme/static/src/base/**/*.js"
        ],
    },
    "demo": [],
    "pre_init_hook": "_pre_init_hook",
    "post_init_hook": "_post_init_hook",
    "uninstall_hook": "_uninstall_cleanup",
    "installable": True,
    "price": 50.00,
    "currency": "ETB",
    "application": False,
    "auto_install": True,
}
