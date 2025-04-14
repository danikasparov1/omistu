# -*- coding: utf-8 -*-
{
    'name' : 'Datetime Calendar',
    'version' : '16.0',
    'summary': 'Datetime Calendar',
    'sequence': -1,
    'description': """Datetime Calendar""",
    'category': 'Hidden',
    'depends' : ['web', 'sale'],
    'data': [
        #'views/sale_order.xml'
    ],
    'installable': True,
    'application': False,
    'assets': {
        'web.assets_backend': [
            'date_picker_amharic/static/src/css/redmond.calendars.picker.css',
            'date_picker_amharic/static/src/css/*.css',
            'date_picker_amharic/static/src/components/date_time.xml',
            'date_picker_amharic/static/src/components/date_time.js',
             'date_picker_amharic/static/src/components/patched_date_time.js',
             'date_picker_amharic/static/src/components/patched_date_time.xml'

        ],
    },
}