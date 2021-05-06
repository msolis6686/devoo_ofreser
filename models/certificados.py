# -*- coding: utf-8 -*-
from odoo import fields, models


class Certificado(models.Model):
    _name = 'ofreser.certificado'
    _description = 'Certificado'
    _rec_name = 'numero'
    _order = 'numero desc'

    numero = fields.Integer('Número de Certificado')
    orden_de_trabajo_id = fields.Many2one(
        comodel_name='ofreser.orden_de_trabajo',
        string='Orden de Trabajo'
    )
    estado = fields.Selection(
        selection=[('no_usado', 'No Usado'), ('usado', 'Usado'), ('cancelado', 'Cancelado')],
        string="Estado",
        default='no_usado'
    )
    nota = fields.Char(string='Nota')

    _sql_constraints = [('numero_unique', 'unique(numero)', 'Este número de certificado ya está creado')]
