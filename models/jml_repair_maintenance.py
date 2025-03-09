# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.tools.float_utils import float_compare, float_round
from odoo.exceptions import UserError


class RepairMaintenance(models.Model):
    _name = 'jml.repair.maintenance'
    _description = 'Repair and Maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('sent_for_repair', 'Sent for Repair'),
        ('received_and_repaired', 'Received and Repaired'),
        ('scrap', 'Scrap'),
    ], default='draft', string='Status', tracking=True)

    repair_date = fields.Date(string='Repair Date', default=fields.Date.today())
    name = fields.Char(strign='Repair No:', required=True, index=True, copy=False, default="NEW")

    # first group
    problem_name = fields.Char(string='Problem', required=True)
    details = fields.Text(string='Repair Details')

    service_type = fields.Many2one('jml.service.type', string='Service Type')

    location_from = fields.Many2one('stock.location', string='Machine Location')
    partner_id = fields.Many2one('res.partner', string="Vendor")
    location_to = fields.Many2one('stock.location', string='Vendor Location')


    scrap_location = fields.Many2one('stock.location', string='Scrap Location', readonly=True)

    # Second Group
    request_by = fields.Many2one('res.users', string='Request By', default=lambda self: self.env.user, readonly=True)
    department = fields.Char(
        string='Department',
        default=lambda self: self.env.user.department_id.name or 'Not Assigned',
        readonly=True
    )

    repair_item_ids = fields.One2many('jml.repair.item', 'repair_id', string='Repair Items')

    damage_list_ids = fields.One2many('jml.repair.damage.list', 'damage_list_id', string='Damage List')

    def action_submit(self):
        self.write({'status': 'submitted'})

    def action_approve(self):
        self.write({'status': 'approved'})

    def action_sent_for_repair(self):
        """When clicking 'Sent for Repair', create a delivery order."""
        self.write({'status': 'sent_for_repair'})

        if not self.repair_item_ids:
            raise UserError(_("No repair items found to create a delivery order."))

        if not self.location_from or not self.location_to:
            raise UserError(_("Please select both 'Machine Location' and 'Vendor Location' before sending for repair."))

        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),  # Outgoing shipment (Delivery Order)
            ('warehouse_id.company_id', '=', self.env.company.id)
        ], limit=1)

        if not picking_type:
            raise UserError(_("No outgoing stock picking type found for this company."))

        picking_vals = {
            'partner_id': self.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': self.location_from.id,
            'location_dest_id': self.location_to.id,
            'origin': self.name,
            'move_ids_without_package': [(0, 0, {
                'product_id': item.product_id.id,
                'name': item.product_id.name,
                'product_uom_qty': item.quantity,
                'product_uom': item.product_id.uom_id.id,
                'location_id': self.location_from.id,
                'location_dest_id': self.location_to.id,
            }) for item in self.repair_item_ids]
        }

        picking = self.env['stock.picking'].create(picking_vals)
        self.picking_id = picking.id  # Store the delivery order reference

        return {
            "name": _("Delivery Order"),
            "res_model": "stock.picking",
            "view_mode": "form",
            "res_id": picking.id,
            "target": "current",
        }

    def action_received_and_repaired(self):
        """When clicking 'Received and Repaired', create a received picking."""
        self.write({'status': 'received_and_repaired'})

        if not self.repair_item_ids:
            raise UserError(_("No repair items found to create a receiving order."))

        if not self.location_from or not self.location_to:
            raise UserError(
                _("Please select both 'Machine Location' and 'Vendor Location' before receiving the items."))

        # Find the picking type for incoming (receiving)
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),  # Incoming shipment (Receipt)
            ('warehouse_id.company_id', '=', self.env.company.id)
        ], limit=1)

        if not picking_type:
            raise UserError(_("No incoming stock picking type found for this company."))

        picking_vals = {
            'partner_id': self.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': self.location_to.id,  # Set the location where items are received
            'location_dest_id': self.location_from.id,  # Set the destination location for the received items
            'origin': self.name,  # The origin is the repair maintenance record name
            'move_ids_without_package': [(0, 0, {
                'product_id': item.product_id.id,
                'name': item.product_id.name,
                'product_uom_qty': item.quantity,
                'product_uom': item.product_id.uom_id.id,
                'location_id': self.location_to.id,
                'location_dest_id': self.location_from.id,
            }) for item in self.repair_item_ids]
        }

        picking = self.env['stock.picking'].create(picking_vals)
        self.picking_id = picking.id  # Store the received picking reference

        return {
            "name": _("Received Picking"),
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "view_mode": "form",
            "res_id": picking.id,
            "target": "current",
        }

    def action_scrap(self):
        """Open popup wizard for scrap selection."""
        return {
            'name': 'Select Scrap Location',
            'type': 'ir.actions.act_window',
            'res_model': 'repair.scrap.wizard',
            'view_mode': 'form',
            'target': 'new',  # Open as popup
            'context': {'default_repair_id': self.id},
        }

    def action_create_bill(self):
        """Create a vendor bill when the button is clicked."""
        if not self.partner_id:
            raise UserError(_("Please select a vendor before creating a bill."))

        if not self.damage_list_ids:
            raise UserError(_("No damage items found to create a bill."))

        bill_vals = {
            "ref": self.name,
            "partner_id": self.partner_id.id,
            "move_type": "in_invoice",  # Vendor Bill
            "invoice_line_ids": [
                (0, 0, {
                    "product_id": item.product_id.id,
                    "quantity": item.quantity,
                    "price_unit": item.product_id.list_price,
                }) for item in self.damage_list_ids
            ],
        }

        bill = self.env["account.move"].create(bill_vals)

        return {
            "name": _("Vendor Bill"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": bill.id,
            "target": "current",
        }

    # for smart button for delivery
    picking_id = fields.Many2one('stock.picking', string='Delivery Order', readonly=True)
    internal_transfer_count = fields.Integer(
        string='Internal Transfer Count',
        compute='_compute_internal_transfer_count'
    )

    @api.depends('picking_id')
    def _compute_internal_transfer_count(self):
        for record in self:
            record.internal_transfer_count = self.env['stock.picking'].search_count([
                ('origin', '=', record.name),
                ('picking_type_id.code', '=', 'outgoing')
            ])

    def action_view_picking(self):
        """Open related delivery orders."""
        self.ensure_one()
        picking_records = self.env['stock.picking'].search([('origin', '=', self.name)])

        if not picking_records:
            raise UserError(_("No delivery order found for this repair request."))

        return {
            'name': _('Delivery Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('origin', '=', self.name), ('picking_type_id.code', '=', 'outgoing')],
            'target': 'current',
        }

    # Smart Button fields for Received Order
    received_picking_id = fields.Many2one('stock.picking', string='Received Order', readonly=True)
    received_transfer_count = fields.Integer(
        string='Received',
        compute='_compute_received_transfer_count'
    )

    @api.depends('received_picking_id')
    def _compute_received_transfer_count(self):
        for record in self:
            record.received_transfer_count = self.env['stock.picking'].search_count([
                ('origin', '=', record.name),
                ('picking_type_id.code', '=', 'incoming')  # Incoming stock transfer
            ])

    def action_view_received_picking(self):
        """Open related received orders."""
        self.ensure_one()
        picking_records = self.env['stock.picking'].search([('origin', '=', self.name)])

        if not picking_records:
            raise UserError(_("No received order found for this repair request."))

        return {
            'name': _('Received Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('origin', '=', self.name), ('picking_type_id.code', '=', 'incoming')],
            'target': 'current',
        }

    # sequence number
    @api.model
    def create(self, vals):
        if vals.get('name', _('NEW')) == "NEW":
            vals['name'] = self.env['ir.sequence'].next_by_code('jml.repair.maintenance') or "NEW"
        result = super(RepairMaintenance, self).create(vals)
        logging.info("Created repair sequence number: %s", result.name)
        return result


class RepairItem(models.Model):
    _name = 'jml.repair.item'
    _description = 'Create Repair'

    brand = fields.Char(string='Brand')
    model = fields.Char(string='Model')
    product_id = fields.Many2one('product.template', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, store=True)

    uom = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id', readonly=True, store=True)
    repair_id = fields.Many2one('jml.repair.maintenance', string='Create Repair')
    remarks = fields.Text(string='Remarks')
    location_from = fields.Many2one('stock.location', string='Location From', related='repair_id.location_from',
                                    readonly=True)
    location_to = fields.Many2one('stock.location', string='Location To', related='repair_id.location_to',
                                  readonly=True)

    current_stock = fields.Float(string='Current Stock', compute='_compute_current_stock', store=True)

    @api.depends('product_id', 'location_from')
    def _compute_current_stock(self):
        for record in self:
            if record.product_id and record.location_from:
                stock_quant = self.env['stock.quant'].search([
                    ('product_id', '=', record.product_id.id),
                    ('location_id', '=', record.location_from.id)
                ], limit=1)
                record.current_stock = stock_quant.quantity if stock_quant else 0
            else:
                record.current_stock = 0
