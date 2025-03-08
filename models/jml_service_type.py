from odoo import models, fields, api

class RepairMaintenance(models.Model):
    _name = 'jml.service.type'
    _description = 'Service Type'


    name = fields.Char(string='Service Type', required=True)
    service_location = fields.Many2one('stock.location', string='Service Location', required=True)