# -*- coding: utf-8 -*-
# from odoo import http


# class JmlCustomRepairMaintenance(http.Controller):
#     @http.route('/jml_custom_repair_maintenance/jml_custom_repair_maintenance', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jml_custom_repair_maintenance/jml_custom_repair_maintenance/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('jml_custom_repair_maintenance.listing', {
#             'root': '/jml_custom_repair_maintenance/jml_custom_repair_maintenance',
#             'objects': http.request.env['jml_custom_repair_maintenance.jml_custom_repair_maintenance'].search([]),
#         })

#     @http.route('/jml_custom_repair_maintenance/jml_custom_repair_maintenance/objects/<model("jml_custom_repair_maintenance.jml_custom_repair_maintenance"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jml_custom_repair_maintenance.object', {
#             'object': obj
#         })

