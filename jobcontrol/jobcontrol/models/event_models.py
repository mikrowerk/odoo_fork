# -*- coding: utf-8 -*-

from odoo import models, fields
from .job_models import JobPurchase


class Event(models.Model):
    _name = 'jobcontrol.eventmanagement.event'
    _description = 'Model for an Event'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    description = fields.Text()
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')

    job_id = fields.Many2one('jobcontrol.job', string="Job")
    job_name = fields.Char(related='job_id.display_name', string="Job Name")

    responsible_customer_id = fields.Many2one('res.partner', string="Responsible Customer")
    responsible_customer_name = fields.Char(string="Responsible Customer Name",
                                            related="responsible_customer_id.complete_name", store="True")
    responsible_agency_id = fields.Many2one('res.partner', string="Responsible Agency")
    responsible_agency_name = fields.Char(string="Responsible Agency Name",
                                          related="responsible_agency_id.complete_name", store="True")
    session_lines = fields.One2many(comodel_name="jobcontrol.eventmanagement.session", inverse_name="event_id",
                                    string="Session Lines")


class EventSession(models.Model):
    _name = 'jobcontrol.eventmanagement.session'
    _description = 'Model for an Event Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Session Name')
    description = fields.Text()
    start_date = fields.Datetime()
    end_date = fields.Datetime()

    event_id = fields.Many2one('jobcontrol.eventmanagement.event', string="Event")
    event_name = fields.Char(related="event_id.name", string="Event", store="True")
    speakers = fields.Many2many('res.partner', string="Speaker")
    pax = fields.Integer(string="Participants")
    event_room_id = fields.Many2one('jobcontrol.eventmanagement.room', string="Room")
    event_room_name = fields.Char(string="Room Name", related="event_room_id.name", store="True")
    event_room_config_id = fields.Many2one('jobcontrol.eventmanagement.room_configuration',
                                           string="Room Configuration",
                                           domain="[('event_room_id', '=', event_room_id)]")
    event_room_config = fields.Char(string="Room Configuration", related="event_room_config_id.name")
    event_room_capacity = fields.Integer(string="Room Capacity", related='event_room_config_id.capacity')
    event_setup_items = fields.One2many(comodel_name="jobcontrol.eventmanagement.room_setup_item",
                                        inverse_name="event_session_id", )
    catering_order_line = fields.One2many(
        comodel_name='purchase.order',
        inverse_name='session_id',
        string='Purchase Order'
    )


class EventRoomSetupItem(models.Model):
    _name = 'jobcontrol.eventmanagement.room_setup_item'
    _description = 'Model for an Event Room Setup Item'
    name = fields.Char(string='Item Name')
    description = fields.Text(string='Item Description')
    comment = fields.Text(string='Comment')
    quantity = fields.Float(string='Quantity', default=1.0)
    externally_supplied = fields.Boolean(string='Externally supplied', default=False)
    event_session_id = fields.Many2one('jobcontrol.eventmanagement.session', string="Environment Session")
    event_session_name = fields.Char(related="event_session_id.name", string="Event Session", store="True",
                                     readonly=True)
    event_name = fields.Char(related="event_session_id.event_id.name", string="Event Name", store="True",
                             readonly=True)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', index='btree_not_null',
        domain="[('sale_ok', '=', True)]")

