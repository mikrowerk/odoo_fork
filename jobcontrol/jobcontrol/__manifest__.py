# -*- coding: utf-8 -*-
{
    'name': "jobcontrol",

    'summary': "Controlling Jobs in a clever way",

    'description': """
The JobControl module allows you to keep track of all associated records, which belongs to a job aka project.
This includes sales orders & invoices, purchases, material & time spend
    """,

    'author': "Mikrowerk",
    'website': "https://www.mikrowerk.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'license': "OPL-1",
    'category': 'Productivity',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'purchase', 'mail', 'stock', 'project'],
    'application': True,

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/job_views.xml',
        'views/job_category_views.xml',
        'views/job_costs_views.xml',
        'views/job_templates.xml',
        'views/sales_order_exented_view.xml',
        'views/purchase_order_exented_view.xml',
        'views/invoice_exented_view.xml',
        'views/jobcontrol_menu.xml',
        'views/event_views.xml',
        'views/location_views.xml',
        'views/event_menu.xml',
        'views/stock_picking_extended_view.xml',
        'views/project_extended_view.xml',
        'reports/event_report_action.xml',
        'reports/event_report_template.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
