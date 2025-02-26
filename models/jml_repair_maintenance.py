from odoo import models, fields, api

class RepairMaintenance(models.Model):
    _name = 'jml.repair.maintenance'
    _description = 'Repair and Maintenance'

    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('sent_for_repair', 'Sent for Repair'),
        ('received_and_repaired', 'Received and Repaired'),
        ('scrap', 'Scrap'),
    ], default='draft', string='Status')

    repair_date = fields.Datetime(string='Repair Date')

    # first group
    name = fields.Char(string='Problem')
    details = fields.Text(string='Repair Details')
    machine_id = fields.Many2one('product.product', string='Machine', required=True)
    model = fields.Char(string='Model')
    service_type = fields.Many2one('jml.service.type', string='Service Type')
    brand = fields.Char(string='Brand')
    location_from = fields.Many2one('stock.location', string='Machine Location',
                                       default=lambda self: self.machine_id.stock_location_id if self.machine_id else False)
    partner_id = fields.Many2one('res.partner' , string="Vendor")
    location_to = fields.Many2one('stock.location', string='Vendor Location', domain=[('usage', '=', 'internal')])

    # Second Group
    request_by = fields.Many2one('res.users', string='Request By', default=lambda self: self.env.user, readonly=True)
    department = fields.Char(
        string='Department',
        default=lambda self: self.env.user.department_id.name or 'Not Assigned',
        readonly=True
    )

    def action_submit(self):
        self.write({'status': 'submitted'})

    def action_approve(self):
        self.write({'status': 'approved'})

    def action_sent_for_repair(self):
        self.write({'status': 'sent_for_repair'})

    def action_received_and_repaired(self):
        self.write({'status': 'received_and_repaired'})

    def action_scrap(self):
        self.write({'status': 'scrap'})

    def action_view_picking(self):
        self.ensure_one()
        picking_records = self.env['stock.picking'].search([
            ('origin', '=', self.name),  # Match the indent request name with the picking origin
            ('picking_type_id.code', '=', 'internal')  # Ensure it's an internal transfer
        ])

    internal_transfer_count = fields.Integer(
        string='Internal Transfer Count',
        compute='_compute_internal_transfer_count'
    )
    picking_id = fields.Many2one('stock.picking', string='Picking', readonly=True)

    @api.depends('picking_id')
    def _compute_internal_transfer_count(self):
        for record in self:
            record.internal_transfer_count = self.env['stock.picking'].search_count([
                ('origin', '=', record.name),
                ('picking_type_id.code', '=', 'internal')
            ])
