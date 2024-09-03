from datetime import datetime

from odoo import models, fields, api
from .job_utils import shorten_text


class JobCosts(models.Model):
    """
    Costs, which are related to a job
    """
    _name = 'jobcontrol.job_costs'
    _description = 'Costs related to jobs'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Name", required=True)
    description = fields.Text("Description", required=False)
    display_name = fields.Char(compute="_display_name", string="Display")
    job_id = fields.Many2one('jobcontrol.job', string="Job")
    event_id = fields.Many2one('jobcontrol.eventmanagement.event', string="Event")
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', index='btree_not_null',
        domain="[('sale_ok', '=', True)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', depends=['product_id'])
    product_uom_qty = fields.Float(
        string="Quantity",
        digits='Product Unit of Measure', default=1.0,
        store=True, readonly=False, required=True)
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        compute='_compute_product_uom',
        store=True, readonly=False, precompute=True, ondelete='restrict',
        domain="[('category_id', '=', product_uom_category_id)]")
    unit_price = fields.Float(string="Unit Price", required=True, digits=(12, 4))
    total_price = fields.Monetary(string="Total Price", compute='_compute_total_price', inverse="_compute_unit_price",
                                  store=True)
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    effective_date = fields.Date(string="Effective Date", default=datetime.now())
    invoiced = fields.Boolean(string="Invoiced", compute="_compute_invoiced", store=True)
    not_billable = fields.Boolean(string="Not Billable", store=True, default=False)
    invoice_line = fields.Many2one(comodel_name="account.move.line", string="Invoice Line",
                                   domain="[('move_type', '=', 'out_invoice')]")

    def _compute_product_uom(self):
        for line in self:
            if not line.product_uom or (line.product_id.uom_id.id != line.product_uom.id):
                line.product_uom = line.product_id.uom_id

    @api.depends('invoice_line')
    def _compute_invoiced(self):

        if self.invoice_line and len(self.invoice_line.ids) > 0:
            self.invoiced = True
            print(f"calculate invoiced = True")
        else:
            self.invoiced = False
            print(f"calculate invoiced = False")

    @api.depends('product_id', 'product_uom_qty', 'unit_price')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.unit_price * line.product_uom_qty
            print(f"_compute_total_price: unit_price={line.unit_price} >> total_price={line.total_price}")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            line.unit_price = line.product_id.lst_price
            print(f"_onchange_product_id:{line.product_id.name} >> line.unit_price={line.unit_price}")

    @api.onchange('total_price')
    def _compute_unit_price(self):
        for line in self:
            line.unit_price = line.total_price / line.product_uom_qty
            print(f"_compute_unit_price: total_price={line.total_price} >> unit_price={line.unit_price}")

    def _display_name(self):
        for record in self:
            record.display_name = shorten_text(f"{record.name} {record.product_uom_qty} "
                                               f"{record.product_uom.name}")
