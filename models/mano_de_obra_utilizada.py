# -*- coding: utf-8 -*-

from odoo import models, fields


class ManoDeObraUtilizada(models.Model):
    _name = 'ofreser.mano_de_obra_utilizada'
    _description = 'Mano de Obra Utilizada'

    user_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Operador')
    orden_de_trabajo_id = fields.Many2one(
        comodel_name='ofreser.orden_de_trabajo',
        string='Orden de trabajo')
    porcentaje = fields.Float(string='Porcentaje')
