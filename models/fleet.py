# -*- coding: utf:8 -*-
from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    _name = 'fleet.vehicle'

    conductor_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Conductor'
    )
