# -*- coding: utf-8 -*-
from odoo import models, fields


class OfreserMaquina(models.Model):
    """ Modelo de maquinas de ofreser """
    _name = 'ofreser.maquina'
    _description = 'Ofreser - Maquinaria'

    name = fields.Char('Nombre')
    orden_de_trabajo_id = fields.Many2many(
        comodel_name='ofreser.orden_de_trabajo',
        string='Orden de Trabajo')
    responsable_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Responsable')
