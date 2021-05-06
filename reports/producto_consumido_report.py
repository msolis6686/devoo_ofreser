# -*- coding: utf-8 -*-

# Odoo
from odoo import models, api


class ProductoconsumidoReport(models.AbstractModel):
    """Generación de reporte de productos Consumidos"""

    _name = 'report.ofreser.liquidacion_en_lote'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('devoo_ofreser.producto_consumido')
        lote_args = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('devoo_ofreser.liquidacion_en_lote', lote_args)
