{
    'name': 'Plant Nursery Management',
    'version': '1.0',
    'category': 'Agriculture',
    'summary': 'Manage seeds, pre-nursery, and main nursery processes',
    'author': 'Handry Pangestiaji',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/plant_nursery_views.xml',
        'views/plant_nursery_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}