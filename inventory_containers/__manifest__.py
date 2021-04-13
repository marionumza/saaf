# -*- coding: utf-8 -*-
{
    'name': "Inventory Containers",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Islam Megger (Projomania)",
    'website': "http://projomania.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','fleet','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stock.xml',
        'views/sale.xml',
        'reports/customer_delivery_report.xml',
    ],
}