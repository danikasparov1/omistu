{
    "name": "Addis Systems Human Resources Extra Base",
    "version": "17.0.1.0",
    "sequence": 5,
    "summary": "Addis Systems Human Resources Extra Base",
    "description": """
        This is a Base Module for Addis Systems Human Resources Extra Base.
            ========================================
    """,
    "category": "Addis Systems/Human Resources",
    "author": "Addis Systems/Beruk W.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_theme", "addis_systems_base", "addis_systems_human_resources_base", "website_mass_mailing", "hr_skills", "hr_holidays", "hr_attendance", "hr_expense", "hr_recruitment", "om_hr_payroll"],
    "external_dependencies": {"python": ["deep-translator", "amharic_keyboard", "holidays"]},
    "data": [
        "data/AddisSystemsHRExtraData.xml"
    ],
    "assets": {
        "web._assets_primary_variables": [],
        "web._assets_backend_helpers": [],
        "web.assets_backend": [],
        "web.assets_frontend": [],
        "web.assets_tests": [],
        "web.qunit_suite_tests": [],
        "web.assets_qweb": [],
    },
    "demo": [],
    "installable": True,
    "price": 49.99,
    "currency": "ETB",
    "application": False,
    'auto_install': ["addis_systems_theme", "addis_systems_base", "addis_systems_human_resources_base", "website_mass_mailing", "hr_skills", "hr_holidays", "hr_attendance", "hr_expense", "hr_recruitment", "om_hr_payroll"],
}
