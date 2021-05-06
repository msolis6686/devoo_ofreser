# -*-coding: utf-8 -*-

# Odoo
from odoo import fields, models


class OfreserCertificadosWizard(models.TransientModel):
    """ Crea Certificados desde un número hasta otro número """
    _name = 'ofreser.certificados_wizard'
    _description = 'Creacion Certificados Wizard'

    desde = fields.Integer(string='Desde')
    hasta = fields.Integer(string='Hasta')

    certificados_no_usados = fields.Text(string='Certificados no Utilizados')

    def crear_certificados(self):
        """Crea un certificado por cada número en el rango introducido"""
        rango = range(self.desde, self.hasta + 1)

        # Buscar los numeros de certificados ya creados dentro del rango
        certificados_creados = self.env['ofreser.certificado'].search([('numero', 'in', rango)])
        numeros_certificados_creados = [cert.numero for cert in certificados_creados]
        # Crear los certificados con los numeros no utilizados en el rango
        for num in rango:
            if num not in numeros_certificados_creados:
                self.env['ofreser.certificado'].create({'numero': num})
