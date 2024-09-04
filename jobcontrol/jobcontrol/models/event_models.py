# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Event(models.Model):
    _name = 'jobcontrol.eventmanagement.event'
    _description = 'Model for an Event'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "start_date ASC"

    name = fields.Char(string='Event Name', required=True)
    description = fields.Text()
    comment = fields.Text(string='Comment')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    signage = fields.Char(string='Signage')

    job_id = fields.Many2one('jobcontrol.job', string="Job")
    job_name = fields.Char(related='job_id.display_name', string="Job Name")

    responsible_customer_id = fields.Many2one('res.partner', string="Responsible Customer")
    responsible_customer_name = fields.Char(string="Responsible Customer Name",
                                            related="responsible_customer_id.complete_name", store="True")
    responsible_agency_id = fields.Many2one('res.partner', string="Responsible Agency")
    responsible_agency_name = fields.Char(
        string="Responsible Agency Name",
        related="responsible_agency_id.complete_name", store="True")
    location_id = fields.Many2one('jobcontrol.eventmanagement.location', string="Location")
    session_lines = fields.One2many(
        comodel_name="jobcontrol.eventmanagement.session", inverse_name="event_id",
        string="Session Lines")
    purchase_order_lines = fields.One2many(
        comodel_name='purchase.order',
        inverse_name='event_id',
        string='Purchase Orders'
    )
    sales_order_lines = fields.One2many(
        comodel_name='sale.order',
        inverse_name='event_id',
        string='Sales Orders'
    )
    stock_move_lines = fields.One2many(
        comodel_name='stock.picking',
        inverse_name='event_id',
        string='Stock Picking')
    setup_items = fields.One2many(
        comodel_name="jobcontrol.eventmanagement.room_setup_item",
        inverse_name="event_id", )


class EventSession(models.Model):
    _name = 'jobcontrol.eventmanagement.session'
    _description = 'Model for an Event Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "event_name ASC, start_date ASC"

    name = fields.Char(string='Session Name', required=True)
    description = fields.Text()
    comment = fields.Text(string='Comment')
    start_date = fields.Datetime()
    end_date = fields.Datetime()

    event_id = fields.Many2one('jobcontrol.eventmanagement.event', string="Event")
    event_name = fields.Char(related="event_id.name", string="Event", store="True")
    location_id = fields.Many2one('jobcontrol.eventmanagement.location', string="Location", readonly=True,
                                  compute='_compute_location_id', store=True)
    speakers = fields.Many2many('res.partner', string="Speaker")
    pax = fields.Integer(string="Participants")
    event_room_id = fields.Many2one('jobcontrol.eventmanagement.room', string="Room",
                                    domain="[('location_id', '=', location_id)]")
    event_room_name = fields.Char(string="Room Name", related="event_room_id.name", store="True")
    event_room_config_id = fields.Many2one('jobcontrol.eventmanagement.room_configuration',
                                           string="Room Configuration",
                                           domain="[('event_room_id', '=', event_room_id)]")
    event_room_config = fields.Char(string="Room Configuration", related="event_room_config_id.name")
    event_room_capacity = fields.Integer(string="Room Capacity", related='event_room_config_id.capacity')
    session_setup_items = fields.One2many(comodel_name="jobcontrol.eventmanagement.room_setup_item",
                                          inverse_name="session_id", )
    session_order_lines = fields.One2many(
        comodel_name='purchase.order',
        inverse_name='session_id',
        string='Purchase Orders'
    )

    @api.depends('event_id')
    def _compute_location_id(self):
        if self.event_id:
            self.location_id = self.event_id.location_id


class EventRoomSetupItem(models.Model):
    _name = 'jobcontrol.eventmanagement.room_setup_item'
    _description = 'Model for an Event Room Setup Item'
    _order = "session_name ASC, subject ASC, name ASC"
    name = fields.Char(string='Item Name', required=True)
    subject = fields.Char(string='Subject', required=True)
    description = fields.Text(string='Item Description')
    comment = fields.Text(string='Comment')
    quantity = fields.Float(string='Quantity', default=1.0)
    externally_supplied = fields.Boolean(string='Externally supplied', default=False)
    session_id = fields.Many2one('jobcontrol.eventmanagement.session', string="Event Session")
    session_name = fields.Char(related="session_id.name", string="Session Name", store="True",
                               readonly=True)
    event_id = fields.Many2one('jobcontrol.eventmanagement.event', string="Event")
    event_name = fields.Char(compute="_set_event")

    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', index='btree_not_null')

    @api.onchange("session_id")
    @api.depends("session_id")
    def _set_event(self):
        for record in self:
            if record.session_id:
                record.event_id = record.session_id.event_id.id
                record.event_name = record.session_id.event_id.name
            elif record.event_id:
                record.event_name = record.event_id.name
