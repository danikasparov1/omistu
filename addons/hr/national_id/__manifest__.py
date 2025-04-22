{
    'name': 'National ID Fields',
    'version': '1.0',
    'summary': 'Adds FAN and FIN national ID fields to partners, users and employees',
    'description': """
        Adds validation for 16-digit FAN numbers and 8-digit FIN numbers
        to partners, users and employees.
    """,
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'category': 'Tools',
    'depends': ['base', 'hr'],
    'data': [
        'views/national_id_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}