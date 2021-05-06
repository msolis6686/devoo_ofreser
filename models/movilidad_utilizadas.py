# -*- coding: utf-8 -*-

from odoo import models, fields


class MovilidadUtilizadas(models.Model):
    _name = 'ofreser.movilidad_utilizada'
    _description = 'Movilidad Utilizada'

    movilidad_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Movilidad')
    orden_de_trabajo_id = fields.Many2one(
        comodel_name='ofreser.orden_de_trabajo',
        string='Orden de trabajo')
    responsable_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Responsable',
        related='movilidad_id.conductor_id')
    porcentaje = fields.Float(string='Porcentaje')
