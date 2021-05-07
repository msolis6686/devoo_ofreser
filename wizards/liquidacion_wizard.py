# -*-coding: utf-8 -*-

# Odoo
from odoo import models, fields, api


class LiquidacionDetalle(models.Model):
    _name = 'ofreser.liquidacion_detalle_wizard'
    """ Genera el detalle de las liquidaciones para el operador que se van a generar """
    _description = 'Detalle de Liquidacion'
    _order = 'fecha'

    mano_de_obra_liquidacion_id = fields.Many2one(
        comodel_name='ofreser.mano_de_obra_liquidacion',
        string='Liquidacion de Mano de Obra'
    )
    liquidacion_id = fields.Many2one(
        comodel_name='ofreser.liquidacion',
        string='Liquidación'
    )
    orden_de_trabajo_id = fields.Many2one(
        comodel_name='ofreser.orden_de_trabajo',
        string='Orden de Trabajo',
        related='liquidacion_id.orden_de_trabajo_id'
    )
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        related='orden_de_trabajo_id.partner_id'
    )
    factura = fields.Char(
        string='Factura',
        related='orden_de_trabajo_id.factura'
    )
    domicilio_cliente = fields.Char(
        string='Dirección',
        related='orden_de_trabajo_id.domicilio'
    )
    tipo_de_trabajos_ids = fields.Char(
        string='Tipo de Trabajo',
        compute='_compute_tipo_de_trabajos_ids'
    )
    precio_orden_de_trabajo = fields.Float(
        string="Precio Orden",
        related='liquidacion_id.orden_de_trabajo_id.precio'
    )
    operador_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Operador',
        related='mano_de_obra_liquidacion_id.empleado_id'
    )
    fecha = fields.Datetime(
        string='Fecha de Servicio',
        related='liquidacion_id.orden_de_trabajo_id.fecha_servicio',
        store=True
    )
    pagado = fields.Selection(
        selection=[('si', 'Si'), ('no', 'No')],
        string='Orden Pagada',
        related='liquidacion_id.orden_de_trabajo_id.pagado'
    )

    porcentaje_mano_de_obra = fields.Float(
        string='Por Mano de obra',
        related='mano_de_obra_liquidacion_id.porcentaje_mano_de_obra'
    )
    porcentaje_num_mano_de_obra = fields.Float(
        string='%',
        related='mano_de_obra_liquidacion_id.porcentaje_num_mano_de_obra'
    )

    porcentaje_maquina = fields.Float(
        string='Por Máquinas',
        related='mano_de_obra_liquidacion_id.porcentaje_maquina'
    )
    porcentaje_num_maquina = fields.Float(
        string='%',
        related='mano_de_obra_liquidacion_id.porcentaje_num_maquina'
    )

    porcentaje_movilidad = fields.Float(
        string='Por Movilidad',
        related='mano_de_obra_liquidacion_id.porcentaje_movilidad'
    )
    porcentaje_num_movilidad = fields.Float(
        string='%',
        related='mano_de_obra_liquidacion_id.porcentaje_num_movilidad'
    )

    porcentaje_promocion = fields.Float(
        string='Por Promoción',
        related='mano_de_obra_liquidacion_id.porcentaje_promocion'
    )
    porcentaje_num_promocion = fields.Float(
        string='%',
        related='mano_de_obra_liquidacion_id.porcentaje_num_promocion'
    )

    porcentaje_extra_bool = fields.Boolean(
        string='Extra?'
    )
    porcentaje_extra = fields.Float(
        string='Por Extras',
        related='mano_de_obra_liquidacion_id.porcentaje_extra'
    )

    total_a_pagar = fields.Float(
        string='A cobrar',
        related='mano_de_obra_liquidacion_id.total_a_pagar'
    )

    ##################################################
    # COMPUTES
    ##################################################
    #@api.one
    def _compute_tipo_de_trabajos_ids(self):
        tipos = [tipo for tipo in self.orden_de_trabajo_id.tipos_de_trabajo_ids]
        tipos_de_trabajo = ''
        length = len(tipos)
        for i, tipo in enumerate(tipos):
            if i != length - 1:
                tipos_de_trabajo += u'{} - '.format(tipo.name)
            else:
                tipos_de_trabajo += u'{}'.format(tipo.name)
            self.tipo_de_trabajos_ids = tipos_de_trabajo

    ##################################################
    # ONCHANGES
    ##################################################
    # @api.onchange('porcentaje_extra_bool')
    # def _onchange_porcentaje_extra_bool(self):
    #     if self.porcentaje_extra_bool:
    #         self.porcentaje_extra = self.orden_de_trabajo_id.precio * 0.03
    #     else:
    #         self.porcentaje_extra = 0

    @api.onchange('porcentaje_extra')
    def _onchange_porcentaje_extra(self):
        base = self.porcentaje_mano_de_obra + self.porcentaje_maquina + self.porcentaje_movilidad + self.porcentaje_promocion
        extra = 0
        if self.porcentaje_extra:
            extra = (base * self.porcentaje_extra) / 100
        else:
            extra = 0

        self.total_a_pagar = base + extra

    # @api.onchange('porcentaje_num_mano_de_obra')
    # def _onchange_porcentaje_num_mano_de_obra(self):
    #     if self.porcentaje_num_mano_de_obra:
    #         self.porcentaje_mano_de_obra = self.porcentaje_num_mano_de_obra / 100 * self.precio_orden_de_trabajo

    # @api.onchange('porcentaje_num_maquina')
    # def _onchange_porcentaje_num_maquina(self):
    #     if self.porcentaje_num_maquina:
    #         self.porcentaje_maquina = self.porcentaje_num_maquina / 100 * self.precio_orden_de_trabajo

    # @api.onchange('porcentaje_num_movilidad')
    # def _onchange_porcentaje_num_movilidad(self):
    #     if self.porcentaje_num_movilidad:
    #         self.porcentaje_movilidad = self.porcentaje_num_movilidad / 100 * self.precio_orden_de_trabajo

    # @api.onchange('porcentaje_num_promocion')
    # def _onchange_porcentaje_num_promocion(self):
    #     if self.porcentaje_num_promocion:
    #         self.porcentaje_promocion = self.porcentaje_num_promocion / 100 * self.precio_orden_de_trabajo
