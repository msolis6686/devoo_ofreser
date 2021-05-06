# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models


class OfreserTipoDeTrabajo(models.Model):
    _name = 'ofreser.tipo_de_trabajo'
    _description = 'Ofreser - Tipos de Trabajo'

    name = fields.Char('Nombre')
    porcentaje_maximo_mano_obra = fields.Integer('Porcentaje Máximo - Mano de obra')
    porcentaje_maximo_promotores = fields.Integer('Porcentaje Máximo - Promotores')
    orden_de_trabajo_id = fields.Many2one(
        comodel_name='ofreser.orden_de_trabajo',
        string='Orden de Trabajo'
    )

    ##################################################
    # ONCHANGES
    ##################################################
    @api.onchange('porcentaje_maximo_mano_obra', 'porcentaje_maximo_promotores')
    def _onchange_porcentajes(self):
        if not self.env.user.has_group('devoo_ofreser.grupo_administracion_ordenes'):
            raise exceptions.ValidationError('No tiene permiso para modificar este campo')
