# -*- coding: utf-8 -*-
# from odoo import http


# class Jobcontrol(http.Controller):
#     @http.route('/jobcontrol/jobcontrol', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jobcontrol/jobcontrol/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('jobcontrol.listing', {
#             'root': '/jobcontrol/jobcontrol',
#             'objects': http.request.env['jobcontrol.jobcontrol'].search([]),
#         })

#     @http.route('/jobcontrol/jobcontrol/objects/<model("jobcontrol.jobcontrol"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jobcontrol.object', {
#             'object': obj
#         })

