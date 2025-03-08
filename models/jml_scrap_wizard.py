# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class RepairScrapWizard(models.TransientModel):
    _name = 'repair.scrap.wizard'
    _description = 'Select Scrap Location'

    scrap_location_id = fields.Many2one(
        'stock.location',
        string='Scrap Location',
        required=True
    )


    def action_confirm_scrap(self):
        """Move the machine to scrap when confirmed."""
        active_id = self.env.context.get('active_id')
        repair_record = self.env['jml.repair.maintenance'].browse(active_id)

        if repair_record:
            repair_record.write({
                'status': 'scrap',
                'scrap_location': self.scrap_location_id.id  # Set Scrap Location
            })



