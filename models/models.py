# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class jml_custom_repair_maintenance(models.Model):
#     _name = 'jml_custom_repair_maintenance.jml_custom_repair_maintenance'
#     _description = 'jml_custom_repair_maintenance.jml_custom_repair_maintenance'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

