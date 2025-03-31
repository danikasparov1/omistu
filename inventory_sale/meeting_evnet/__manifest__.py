{
    'name': 'Event Management',
    'version': '1.0',
    'category': 'Event',
    'summary': 'Manage events, guests, services, and more',
    'author': 'Gebrehiwot',
    'depends': ['base','account', 'event',  'lunch', 'product',
        'stock',
        'point_of_sale', ],
    'data': [
        'security/ir.model.access.csv',

        'views/event_views.xml',
        'views/event_food_booking_line_views.xml',
        # 'views/service_views.xml',
    ],
    'installable': True,
    'application': True,
}
