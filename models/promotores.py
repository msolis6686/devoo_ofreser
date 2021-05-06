# -*- coding: utf-8 -*-

from odoo import models, fields


class Promotor(models.Model):
    _name = 'ofreser.promotor'
    _description = 'Promotor'

    promotor_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Promotor')
    orden_de_trabajo_id = fields.Many2one(
        comodel_name='ofreser.orden_de_trabajo',
        string='Orden de trabajo')
    porcentaje = fields.Float(string='Porcentaje')
