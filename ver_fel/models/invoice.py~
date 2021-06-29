# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, api, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def ver_factura(self):
        uuid = "FAC"
        for invoice in self:
            uuid = invoice.uuid
        sitio ={  'name'     : 'Ver Factura',
                  'res_model': 'ir.actions.act_url',
                  'type'     : 'ir.actions.act_url',
                  'target'   : 'new',
                  'url'      : 'https://report.feel.com.gt/ingfacereport/ingfacereport_documento?uuid='+uuid
               }
        return sitio
