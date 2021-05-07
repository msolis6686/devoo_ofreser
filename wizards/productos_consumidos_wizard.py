# -*- coding: utf-8 -*-

from odoo import api, fields, models


class OfreserProductoConsumidoWizard(models.TransientModel):
    _name = 'ofreser.producto_consumido_wizard'
    _description = 'Totalizador de consumo'

    desde = fields.Datetime('Desde')
    hasta = fields.Datetime('Hasta')
    operador_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Operador'
    )
    producto_id = fields.Many2one(
        comodel_name='product.template',
        string='Producto'
    )
    detalle_ids = fields.Many2many(
        comodel_name='ofreser.producto_consumido_detalle',
        relation='prod_consumido_detalle_rel',
        string='Detalle'
    )
    total = fields.Float(string='Total')
    total_unidad = fields.Many2one(
        comodel_name='product.uom',
        string='Unidad'
    )

    #@api.multi
    def action_imprimir(self):
        return self.env['report'].get_action(self, 'devoo_ofreser.producto_consumido')

    #@api.multi
    def calcular_consumos(self):
        params = []
        params.append(('fecha_servicio', '>=', self.desde)) if self.desde else None
        params.append(('fecha_servicio', '<=', self.hasta)) if self.hasta else None
        ordenes = self.env['ofreser.orden_de_trabajo'].search(params)
        if self.operador_id:
            ordenes = ordenes.filtered(lambda r: self.operador_id.id in [mo.user_id.id for mo in r.mano_de_obra_utilizada_ids])
        if self.producto_id:
            ordenes = ordenes.filtered(lambda r: self.producto_id.id in [pc.product_id.id for pc in r.productos_consumidos_ids])

        self.detalle_ids = None

        detalles = []
        for orden in ordenes:
            for prod_consumido in orden.productos_consumidos_ids:
                if self.producto_id:
                    if prod_consumido.product_id == self.producto_id:
                        item_vals = {
                            'orden_de_trabajo_id': orden.id,
                            'fecha': orden.fecha_servicio,
                            'cliente_id': orden.partner_id.id,
                            'tipo_de_trabajos': orden.tipos_de_trabajo_display,
                            'producto_id': prod_consumido.product_id.id,
                            'cantidad': prod_consumido.cantidad,
                            'uom_id': prod_consumido.uom_id.id
                        }
                        detalles.append((0, 0, item_vals))
                else:
                    item_vals = {
                        'orden_de_trabajo_id': orden.id,
                        'fecha': orden.fecha_servicio,
                        'cliente_id': orden.partner_id.id,
                        'tipo_de_trabajos': orden.tipos_de_trabajo_display,
                        'producto_id': prod_consumido.product_id.id,
                        'cantidad': prod_consumido.cantidad,
                        'uom_id': prod_consumido.uom_id.id
                    }
                    detalles.append((0, 0, item_vals))

        self.detalle_ids = detalles if detalles else None

        if self.producto_id:
            total = sum([detalle.cantidad for detalle in self.detalle_ids])

            if self.producto_id.uom_id.name == 'cm3':
                self.total = total * self.producto_id.uom_id.factor
                self.total_unidad = self.env.ref('product.product_uom_litre')
            else:
                self.total = total
                self.total_unidad = self.producto_id.uom_id.id
        else:
            self.total = 0
            self.total_unidad = None


class OfreserProductoConsumidoDetalle(models.TransientModel):
    _name = 'ofreser.producto_consumido_detalle'
    _description = 'Detalle de productos consumidos'

    orden_de_trabajo_id = fields.Many2one(
        comodel_name='ofreser.orden_de_trabajo',
        string='Orden de Trabajo'
    )
    fecha = fields.Datetime(string='Fecha')
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente'
    )
    tipo_de_trabajos = fields.Char(string='Tipo de Trabajo')
    producto_id = fields.Many2one(
        comodel_name='product.template',
        string='Producto'
    )
    cantidad = fields.Float(string='Cantidad')
    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='Unidad'
    )
