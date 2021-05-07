# -*- coding: utf-8 -*-

# Odoo
from odoo import models, api


class LiquidacionEnLoteReport(models.AbstractModel):
    """Generación de reporte de liquidación en lote"""

    _name = 'report.ofreser.liquidacion_en_lote'

    #@api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('devoo_ofreser.liquidacion_en_lote')
        lote_args = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('devoo_ofreser.liquidacion_en_lote', lote_args)
