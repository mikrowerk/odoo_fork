# Models for location module
from odoo import models, fields


class EventLocation(models.Model):
    _name = 'jobcontrol.eventmanagement.location'
    _description = 'Location for Events'
    partner_id = fields.Many2one(comodel_name='res.partner', string='Address')
    name = fields.Char(string="Location Name", related="partner_id.complete_name", store="True")
    location_zip = fields.Char(string="Zip Code", related="partner_id.zip", store="True")
    location_city = fields.Char(string="City", related="partner_id.city", store="True")
    contact_address = fields.Char(string="Contact Address", related="partner_id.contact_address", store="True")
    location_country = fields.Char(string="Country", related="partner_id.country_code", store="True")
    location_description = fields.Text(string="Location Description")
    pax_max = fields.Integer(string="PAX Max")
    rooms = fields.One2many(comodel_name='jobcontrol.eventmanagement.room', inverse_name="location_id", string="Rooms",
                            help='Event Rooms of the location')


class EventRoom(models.Model):
    _name = 'jobcontrol.eventmanagement.room'
    _description = 'EventLocation Room'
    name = fields.Char(string='Room Name')
    description = fields.Text(string='Description')
    capacity_max = fields.Integer(string='Maximum Capacity')
    qm = fields.Integer(string='Square meters')
    location_id = fields.Many2one(comodel_name='jobcontrol.eventmanagement.location', string='Location')
    location_name = fields.Char(string="Location Name", related="location_id.name", store="True")
    room_configurations = fields.One2many(comodel_name='jobcontrol.eventmanagement.room_configuration',
                                          string='Room Configurations', inverse_name="event_room_id",
                                          help='Room Setup Variants')


class EventRoomConfiguration(models.Model):
    _name = 'jobcontrol.eventmanagement.room_configuration'
    _description = 'Describes a Room Setup in the context of person capacity'
    name = fields.Char(string='Room Setup Name')
    description = fields.Text(string='Description')
    capacity = fields.Integer(string='Capacity')
    event_room_id = fields.Many2one(comodel_name='jobcontrol.eventmanagement.room', string='EventLocation', )
