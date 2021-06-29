# -*- encoding: UTF-8 -*-

{
    'name': 'Ver Factura FEL',
    'summary': """Imprimir Formato Factura""",
    'version': '14.0.1.0.',
    'description': """Imprimir Formato Factura Electronica para Guatemala. (Solo con INFILE)""",
    'author': 'Osmin Cano --> osmincano@gmail.com',
    'maintainer': 'Osmin Cano',
    'website': 'http://odoo.com',
    'category': 'account',
    'depends': ['account', 'fel'],
    'license': 'AGPL-3',
    'data': [
                'views/invoice_view.xml',
            ],
    'demo': [],
    'sequence': 4,
    'installable': True,
    'auto_install': False,
    'application': False,


}