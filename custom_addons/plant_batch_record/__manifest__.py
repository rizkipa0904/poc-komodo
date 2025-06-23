{
    'name': 'Plant Batch Record',
    'version': '1.0',
    'summary': 'Module to store Plant Code, Batch Number, and Date',
    'author': 'Meyliana',
    'category': 'Custom',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/plant_batch_views.xml',
        'views/plant_activity_form.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'plant_batch_record/static/src/css/plant_batch.css',
            'plant_batch_record/static/src/client_action/**/*',
            'plant_batch_record/static/src/js/**/*',
        ],
        'web.assets_frontend': [
            'plant_batch_record/static/src/js/**/*',
        ],
    },
    'installable': True,
    'application': True,
}