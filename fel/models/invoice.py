# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
#from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP

class AccountMove(models.Model):
        _inherit = "account.move"

        uuid = fields.Char("Numero Autorizacion", readonly=True, states={'draft': [('readonly', False)]})
        serie = fields.Char("Serie", readonly=True, states={'draft': [('readonly', False)]})
        numero_dte = fields.Char("Numero DTE", readonly=True, states={'draft': [('readonly', False)]})
        dte_fecha = fields.Datetime("Fecha Autorizacion", readonly=True, states={'draft': [('readonly', False)]})
        cae = fields.Text("CAE", readonly=True, states={'draft': [('readonly', False)]})
        letras = fields.Text("Total Letras", readonly=True, states={'draft': [('readonly', False)]})
        retencion = fields.Float(string="Retencion", readonly=True, states={'draft': [('readonly', False)]})
        tipo_f = fields.Selection([
            ('normal', 'Factura Normal'),
            ('especial', 'Factura Especial'),
            ('cambiaria', 'Factura Cambiaria'),
            ('cambiaria_exp', 'Factura Cambiaria Exp.'),
            ('exportacion', 'Factura Exenta'),
            ('fac_exp', 'Factura Exportacion'),
            ], string='Tipo Factura', default='normal', readonly=True, states={'draft': [('readonly', False)]})
        regimen_antiguo = fields.Boolean(string="Nota de credito rebajando regimen antiguo", readonly=True, states={'draft': [('readonly', False)]}, default=False)
        nota_abono = fields.Boolean(string="Nota de Abono", readonly=True, states={'draft': [('readonly', False)]}, default=False)

AccountMove()

