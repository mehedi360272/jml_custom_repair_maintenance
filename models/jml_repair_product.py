from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_machine = fields.Boolean(string="Is Machine", help="Indicates if the product is a machine")
    is_parts = fields.Boolean(string="Is Parts", help="Indicates if the product is a part of a machine")
