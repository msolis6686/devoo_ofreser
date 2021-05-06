# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ManoDeObraLiquidacion(models.Model):
    _name = 'ofreser.mano_de_obra_liquidacion'
    _description = 'Liquidacion de Mano de Obra'
    _rec_name = 'liquidacion_id'
    _order = 'fecha asc'

    empleado_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Operador')
    liquidacion_id = fields.Many2one(
        comodel_name='ofreser.liquidacion',
        string='Orden de Trabajo')
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        related='liquidacion_id.orden_de_trabajo_id.partner_id',
        store=True
    )
    factura = fields.Char(
        string='Factura',
        related='liquidacion_id.orden_de_trabajo_id.factura'
    )
    domicilio = fields.Char(
        string='Domicilio',
        related='liquidacion_id.orden_de_trabajo_id.domicilio',
        store=True
    )
    fecha = fields.Datetime(
        string="Fecha de Servicio",
        related='liquidacion_id.orden_de_trabajo_id.fecha_servicio',
        readonly=True)
    porcentaje_num_mano_de_obra = fields.Float(string='%')
    porcentaje_mano_de_obra = fields.Float(string='Por Mano de obra')
    mano_de_obra_utlizada_id = fields.Many2one(comodel_name='ofreser.mano_de_obra_utilizada', string='Mano de Obra Utilizada')

    porcentaje_num_maquina = fields.Float(string='%')
    porcentaje_maquina = fields.Float(string='Por Máquinas')
    maquina_utilizada_id = fields.Many2one(comodel_name='ofreser.maquina_utilizada', string='Maquina Utilizada')

    porcentaje_num_movilidad = fields.Float(string='%')
    porcentaje_movilidad = fields.Float(string='Por Movilidad')
    movilidad_utilizadas_id = fields.Many2one(comodel_name='ofreser.movilidad_utilizada', string='Movilidad Utilizada')

    porcentaje_num_promocion = fields.Float(string='%')
    porcentaje_promocion = fields.Float(string='Por Promoción')
    promotor_id = fields.Many2one(comodel_name='ofreser.promotor', string='Por Promoción')

    porcentaje_extra = fields.Float(string='Por Extras')

    total_a_pagar = fields.Float(string='A cobrar')
    monto_pagado = fields.Float(string='Pagado')
    saldo_a_pagar = fields.Float(string='Saldo')
    liquidado = fields.Boolean(
        string='Liquidado',
        default=False
    )
    fecha_liquidacion = fields.Date(
        string='Fecha de Liquidación'
    )
    liquidacion_lote_id = fields.Many2one(
        comodel_name='ofreser.liquidacion_en_lote',
        string='Lote'
    )

    ##################################################
    # ONCHANGES
    ##################################################
    @api.onchange('monto_pagado')
    def onchange_monto_pagado(self):
        self.saldo_a_pagar = self.total_a_pagar - self.monto_pagado

    ##################################################
    # ORM OVERRIDES
    ##################################################
    @api.multi
    def write(self, vals):
        res = super(ManoDeObraLiquidacion, self).write(vals)
        return res
