# -*- coding: utf:8 -*-
from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    razon_social = fields.Char('Razon Social', placeholder='Razón Social')
    rubro_id = fields.Many2one('ofreser.rubro', placeholder='Rubro')
    promotor_id = fields.Many2one('hr.employee', placeholder='Promotor')
    cuit = fields.Char(string='CUIT/L')
    orden_de_trabajo_ids = fields.One2many(
        comodel_name='ofreser.orden_de_trabajo',
        inverse_name='partner_id',
        string='Trabajos Realizados'
    )

    @api.multi
    def name_get(self):
        if self.env.context.get('with_address'):
            result = []
            name = self._rec_name
            if name in self._fields:
                convert = self._fields[name].convert_to_display_name
                for record in self:
                    result.append((record.id, convert("%s - %s" % (record[name], record.street), record)))
            else:
                for record in self:
                    result.append((record.id, "%s - %s,%s" % (record._name, record.street, record.id)))

        else:
            result = super(ResPartner, self).name_get()
        return result
