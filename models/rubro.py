# -*- coding: utf-8 -*-
from odoo import models, fields, api


class OfreserRubro(models.Model):
    _name = 'ofreser.rubro'
    _description = 'Ofreser - Rubro'

    name = fields.Char('Nombre')
