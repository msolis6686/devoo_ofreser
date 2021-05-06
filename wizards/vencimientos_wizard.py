# -*-coding: utf-8 -*-

# Utilities
import pytz

# Odoo
from odoo import api, fields, models


class OfreserVencimientosWizard(models.TransientModel):
    """ Obtener datos para impresión de reporte de vencimientos """
    _name = 'ofreser.vencimientos_wizard'
    _description = 'Vencimientos Wizard'

    fecha_desde = fields.Date(string='Desde')
    fecha_hasta = fields.Date(string='Hasta')

    promotor_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Promotor'
    )

    orden_de_trabajo_ids = fields.Many2many(
        comodel_name='ofreser.ordenes_venicmiento'
    )

    @api.onchange('fecha_desde', 'fecha_hasta', 'promotor_id')
    def _onchange_fechas(self):
        """Al cambiar cualquiera de las dos fechas actualiza la lista de ordenes de trabajo
        con vencimiento entre esas fechas
        """
        params = []
        local = pytz.timezone(self.env.user._context.get('tz'))
        if self.fecha_desde:
            desde_dt_naive = fields.Datetime.from_string(self.fecha_desde)
            desde_dt = local.localize(desde_dt_naive, is_dst=None)
            desde_dt_utc = desde_dt.astimezone(pytz.utc)
            fecha_desde_utc = fields.Datetime.to_string(desde_dt_utc)
            params.append(('fecha_vencimiento', '>=', fecha_desde_utc))
        if self.fecha_hasta:
            hasta_dt_naive = fields.Datetime.from_string(self.fecha_hasta)
            hasta_dt_naive = hasta_dt_naive.replace(hour=23, minute=59, second=59, microsecond=0)
            hasta_dt = local.localize(hasta_dt_naive, is_dst=None)
            hasta_dt_utc = hasta_dt.astimezone(pytz.utc)
            fecha_hasta_utc = fields.Datetime.to_string(hasta_dt_utc)
            params.append(('fecha_vencimiento', '<=', fecha_hasta_utc))

        if params:
            ordenes = self.env['ofreser.orden_de_trabajo'].search(params).sorted(key=lambda r: r.fecha_vencimiento)
            if self.promotor_id:
                ordenes = ordenes.filtered(lambda r: self.promotor_id.id == r.partner_id.promotor_id.id)

            ordenes_vencimiento = []
            for orden in ordenes:
                vals = {
                    'orden_id': orden.id,
                    'promotor_id': orden.partner_id.promotor_id.id,
                    'numero_comprobante': orden.numero_comprobante.zfill(8),
                    'fecha_servicio': orden.fecha_servicio,
                    'fecha_vencimiento': orden.fecha_vencimiento,
                    'cliente_id': orden.partner_id.id,
                    'domicilio': orden.domicilio,
                    'telefono': orden.telefono,
                    'movil': orden.partner_id.mobile,
                    'email': orden.partner_id.email,
                    'precio': orden.precio,
                }
                ordenes_vencimiento.append((0, 0, vals))
            self.orden_de_trabajo_ids = ordenes_vencimiento

    @api.multi
    def action_imprimir(self):
        return self.env['report'].get_action(self, 'devoo_ofreser.vencimientos_print')
        pass


class OfreserOrdenesVencimiento(models.TransientModel):
    _name = 'ofreser.ordenes_venicmiento'
    _description = 'Ordenes de venicmientos'

    orden_id = fields.Many2one(
        comodel_name='ofreser.orden_de_trabajo',
        string='Orden'
    )
    promotor_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Promotor'
    )
    numero_comprobante = fields.Char(string='N° Comprobante')
    fecha_servicio = fields.Datetime(string='Fecha Servicio')
    fecha_vencimiento = fields.Datetime(string='Fecha Vencimiento')
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente'
    )
    domicilio = fields.Char(string='Domicilio')
    telefono = fields.Char(string='Telefono')
    movil = fields.Char(string='Móvil')
    email = fields.Char(string='Email')
    precio = fields.Float(string='Precio')
