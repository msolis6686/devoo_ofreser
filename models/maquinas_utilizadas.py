# -*- coding: utf-8 -*-

from odoo import models, fields


class MaquinasUtilizadas(models.Model):
    _name = 'ofreser.maquina_utilizada'
    _description = 'Maquina Utilizada'

    maquina_id = fields.Many2one(
        comodel_name='ofreser.maquina',
        string='Máquina')
    orden_de_trabajo_id = fields.Many2one(
        comodel_name='ofreser.orden_de_trabajo',
        string='Orden de trabajo')
    responsable_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Responsable',
        related='maquina_id.responsable_id')
    porcentaje = fields.Float(string='Porcentaje')
