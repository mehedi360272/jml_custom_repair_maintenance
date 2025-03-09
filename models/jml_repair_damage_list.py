# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class RepairItem(models.Model):
    _name = 'jml.repair.damage.list'
    _description = 'Create Repair'


    product_id = fields.Many2one('product.template', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, store=True)

    uom = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id', readonly=True, store=True)

    damage_list_id = fields.Many2one('jml.repair.maintenance', string='Damage List')
    remarks = fields.Text(string='Remarks')
