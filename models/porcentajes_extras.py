# -*- coding: utf-8 -*-

from odoo import models, fields


class PorcentajeExtra(models.Model):
    _name = 'ofreser.porcentaje_extra'
    _description = 'Porcentaje Extra'

    user_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Operador'
    )
    orden_de_trabajo_id = fields.Many2one(
        comodel_name='ofreser.orden_de_trabajo',
        string='Orden de trabajo'
    )
    porcentaje = fields.Float(string='Porcentaje')
