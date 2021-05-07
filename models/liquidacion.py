# -*- coding: utf-8 -*-

# Odoo
from odoo import api, fields, models

# Utilities
from datetime import date


class Liquidacion(models.Model):
    _name = 'ofreser.liquidacion'
    _description = 'Liquidacion'
    _rec_name = 'orden_de_trabajo_id'

    orden_de_trabajo_id = fields.Many2one(
        comodel_name='ofreser.orden_de_trabajo',
        string='Orden de Trabajo')
    estado = fields.Selection(
        selection=[('liquidado', 'Liquidado'), ('no_liquidado', 'No Liquidado')],
        string='Estado',
        default='no_liquidado')
    fecha_servicio = fields.Datetime(
        string="Fecha de Servicio",
        related='orden_de_trabajo_id.fecha_servicio',
        store=True,
        readonly=True)
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        related='orden_de_trabajo_id.partner_id',
        readonly=True)
    domicilio = fields.Char(
        string='Domicilio',
        related='orden_de_trabajo_id.domicilio',
        readonly=True)
    tipos_de_trabajo_ids = fields.Many2many(
        comodel_name='ofreser.tipo_de_trabajo',
        string='Tipos de trabajo',
        related='orden_de_trabajo_id.tipos_de_trabajo_ids',
        readonly=True)
    precio = fields.Float(
        string='Precio',
        related='orden_de_trabajo_id.precio',
        readonly=True)
    cobrado = fields.Float('Cobrado')
    saldo = fields.Float('Saldo')
    certificado_id = fields.Many2one(
        comodel_name='ofreser.certificado',
        string='N° de Certificado',
        related='orden_de_trabajo_id.certificado_id',
        readonly=True
    )
    factura = fields.Char(
        string='Factura',
        related='orden_de_trabajo_id.factura',
        readonly=True)
    mano_de_obra_liquidacion_ids = fields.One2many(
        comodel_name='ofreser.mano_de_obra_liquidacion',
        inverse_name='liquidacion_id',
        string="Liquidación")
    observaciones = fields.Text(string='Observaciones')

    @api.onchange('cobrado')
    def onchange_cobrado(self):
        self.saldo = self.precio - self.cobrado


class LiquidacionEnLote(models.Model):
    """Liquidacion en Lote

    Guarda los datos de las liquidaciones de orden de trabajo por trabajador y fechas
    """
    _name = 'ofreser.liquidacion_en_lote'
    _description = 'Liquidacion en Lote'

    operador_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Operador'
    )
    fecha_desde = fields.Date('Desde')
    fecha_hasta = fields.Date('Hasta')
    fecha_liquidacion = fields.Date(
        string='Fecha de Liquidación',
        default=lambda d: date.today()
    )
    monto_total = fields.Float('Monto Total')
    liquidada = fields.Boolean('Liquidada', default=False)
    detalle_liquidacion_ids = fields.Many2many(
        comodel_name='ofreser.liquidacion_detalle_wizard',
        relation='detalle_liquidacion_lote_wizard_rel',
        string='Liquidaciones'
    )
    liquidacion_ids = fields.One2many(
        comodel_name='ofreser.mano_de_obra_liquidacion',
        inverse_name='liquidacion_lote_id',
        string='Liquidaciones'
    )

    ##################################################
    # ONCHANGES
    ##################################################

    @api.onchange('operador_id', 'fecha_desde', 'fecha_hasta')
    def _onchange_info(self):
        # Busqueda de liquidaciones
        search_params = [('liquidado', '=', False)]
        if self.fecha_desde:
            search_params.append(('fecha', '>=', self.fecha_desde))
        if self.fecha_hasta:
            search_params.append(('fecha', '<=', self.fecha_hasta))
        if self.operador_id:
            search_params.append(('empleado_id', '=', self.operador_id.id))
        liquidaciones = self.env['ofreser.mano_de_obra_liquidacion'].search(search_params, order='fecha')

        if liquidaciones:
            liquidaciones = liquidaciones.sorted(key=lambda r: r.fecha)
            super_vals = []
            for liquidacion in liquidaciones:
                vals = {
                    'mano_de_obra_liquidacion_id': liquidacion.id,
                    'liquidacion_id': liquidacion.liquidacion_id.id,
                    'fecha': liquidacion.fecha,
                    'pagado': liquidacion.liquidacion_id.orden_de_trabajo_id.pagado,
                    'porcentaje_mano_de_obra': liquidacion.porcentaje_mano_de_obra,
                    'porcentaje_maquina': liquidacion.porcentaje_maquina,
                    'porcentaje_movilidad': liquidacion.porcentaje_movilidad,
                    'porcentaje_extra': liquidacion.porcentaje_extra,
                    'porcentaje_promocion': liquidacion.porcentaje_promocion,
                    'total_a_pagar': liquidacion.total_a_pagar,
                }
                super_vals.append((0, 0, vals))
                # self.detalle_liquidacion_ids = [(0, 0, vals)]
            self.detalle_liquidacion_ids = super_vals
            self.monto_total = sum([liquidacion.total_a_pagar for liquidacion in liquidaciones])
        else:
            self.detalle_liquidacion_ids = None

    ##################################################
    # ACTIONS
    ##################################################
    #@api.multi
    def imprimir(self):
        return self.env['report'].get_action(self, 'devoo_ofreser.liquidacion_en_lote')

    def liquidar(self):
        self.liquidada = True
        if self.detalle_liquidacion_ids:
            for liquidacion in self.detalle_liquidacion_ids:
                # aca setea todos los valores a como te los pasa el detalle seleccionado, override a todo :v
                # liquidacion.mano_de_obra_liquidacion_id.porcentaje_num_mano_de_obra = liquidacion.porcentaje_num_mano_de_obra
                # liquidacion.mano_de_obra_liquidacion_id.porcentaje_mano_de_obra = liquidacion.porcentaje_mano_de_obra

                # liquidacion.mano_de_obra_liquidacion_id.porcentaje_num_maquina = liquidacion.porcentaje_num_maquina
                # liquidacion.mano_de_obra_liquidacion_id.porcentaje_maquina = liquidacion.porcentaje_maquina

                # liquidacion.mano_de_obra_liquidacion_id.porcentaje_num_movilidad = liquidacion.porcentaje_num_movilidad
                # liquidacion.mano_de_obra_liquidacion_id.porcentaje_movilidad = liquidacion.porcentaje_movilidad

                # liquidacion.mano_de_obra_liquidacion_id.porcentaje_num_promocion = liquidacion.porcentaje_num_promocion
                # liquidacion.mano_de_obra_liquidacion_id.porcentaje_promocion = liquidacion.porcentaje_promocion

                liquidacion.mano_de_obra_liquidacion_id.porcentaje_extra = liquidacion.porcentaje_extra
                liquidacion.mano_de_obra_liquidacion_id.liquidado = True
                liquidacion.mano_de_obra_liquidacion_id.fecha_liquidacion = self.fecha_liquidacion

                # Y tiene que cambiar en la orden de trabajo
                # mo_utilizada = liquidacion.orden_de_trabajo_id.mano_de_obra_utilizada_ids.filtered(lambda r: r.user_id.id == liquidacion.operador_id.id)
                # maq_utilizada = liquidacion.orden_de_trabajo_id.maquinas_utilizadas_ids.filtered(lambda r: r.responsable_id.id == liquidacion.operador_id.id)
                # mov_utilizada = liquidacion.orden_de_trabajo_id.movilidad_utilizadas_ids.filtered(lambda r: r.responsable_id.id == liquidacion.operador_id.id)
                # promotor = liquidacion.orden_de_trabajo_id.promotores_ids.filtered(lambda r: r.promotor_id.id == liquidacion.operador_id.id)

                # if mo_utilizada:
                #     mo_utilizada.porcentaje = liquidacion.porcentaje_num_mano_de_obra
                # if maq_utilizada:
                #     maq_utilizada.porcentaje = liquidacion.porcentaje_num_maquina
                # if mov_utilizada:
                #     mov_utilizada.porcentaje = liquidacion.porcentaje_num_movilidad
                # if promotor:
                #     promotor.porcentaje = liquidacion.porcentaje_num_promocion

            liquidacion_ids = [liquidacion.mano_de_obra_liquidacion_id.id for liquidacion in self.detalle_liquidacion_ids]
            self.liquidacion_ids = [(6, 0, liquidacion_ids)]

            self.detalle_liquidacion_ids = None

    #@api.multi
    def actualizar_valores(self):
        self.detalle_liquidacion_ids = None
        search_params = [('liquidado', '=', False)]
        if self.fecha_desde:
            search_params.append(('fecha', '>=', self.fecha_desde))
        if self.fecha_hasta:
            search_params.append(('fecha', '<=', self.fecha_hasta))
        if self.operador_id:
            search_params.append(('empleado_id', '=', self.operador_id.id))
        liquidaciones = self.env['ofreser.mano_de_obra_liquidacion'].search(search_params, order='fecha')

        if liquidaciones:
            super_vals = []
            for liquidacion in liquidaciones:
                vals = {
                    'mano_de_obra_liquidacion_id': liquidacion.id,
                    'liquidacion_id': liquidacion.liquidacion_id.id,
                    'fecha': liquidacion.fecha,
                    'pagado': liquidacion.liquidacion_id.orden_de_trabajo_id.pagado,
                    'porcentaje_mano_de_obra': liquidacion.porcentaje_mano_de_obra,
                    'porcentaje_maquina': liquidacion.porcentaje_maquina,
                    'porcentaje_movilidad': liquidacion.porcentaje_movilidad,
                    'porcentaje_extra': liquidacion.porcentaje_extra,
                    'porcentaje_promocion': liquidacion.porcentaje_promocion,
                    'total_a_pagar': liquidacion.total_a_pagar,
                }
                super_vals.append((0, 0, vals))
                # self.detalle_liquidacion_ids = [(0, 0, vals)]
            self.detalle_liquidacion_ids = super_vals
            self.monto_total = sum([liquidacion.total_a_pagar for liquidacion in liquidaciones])
        else:
            self.detalle_liquidacion_ids = None

    ##################################################
    # METODOS
    ##################################################
    def _generar_detalles_liquidacion_ids(self):
        """Toma los valores de la consulta en el formulario y devuelve una lista de valores para los
        """
        pass

    ##################################################
    # REPORT METHODS
    ##################################################
