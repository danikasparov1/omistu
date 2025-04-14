{
    'name': 'AOSQA Telegram Bot Discuss',
    'version': '17.0.1.0',
    'author': 'Abdulselam M.',
    'depends': ['base', 'mail','project'],
    'data': [
                "security/ir.model.access.csv",

        'views/telegram_channel_views.xml',
        'views/res_partner_view.xml',
        'views/gitlab_event.xml',
        'views/subtask.xml',
        'views/commit_sequence.xml'
    ],
    'installable': True,
    'application': True,
}
