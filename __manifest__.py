# -*- coding: utf-8 -*-
{
    'name': "Jml Custom Repair Maintenance",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Khondokar Md. Mehedi Hasan",
    'website': "https://github.com/mehedi360272",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase'],

    # always loaded
    'data': [
        'views/jml_repair_maintenance_views.xml',
        'views/menus.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}

