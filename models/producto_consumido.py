# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OfreserProductoConsumido(models.Model):
    _name = 'ofreser.producto_consumido'
    _description = 'Ofreser - Producto Consumido'

    product_id = fields.Many2one(
        comodel_name='product.template',
        string='Producto')
    orden_de_trabajo_id = fields.Many2one(
        comodel_name='ofreser.orden_de_trabajo',
        string='Orden de trabajo')
    cantidad = fields.Float('cantidad')
    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='Unidad'
    )

    ##################################################
    # ONCHANGES
    ##################################################
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id

    ##################################################
    # ORM OVERRIDES
    ##################################################
    @api.model
    def create(self, vals):
        # Añade la uom al registro porque en la vista es read only
        res = super(OfreserProductoConsumido, self).create(vals)
        res.uom_id = res.product_id.uom_id
        return res

    #@api.multi
    def write(self, vals):
        # Añade la uom al registro porque en la vista es read only
        if vals.get('product_id'):
            vals['uom_id'] = self.env['product.template'].browse(vals['product_id']).uom_id.id
        res = super(OfreserProductoConsumido, self).write(vals)
        return res
