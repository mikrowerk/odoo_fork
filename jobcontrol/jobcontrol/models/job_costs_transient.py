from datetime import datetime

from odoo import models, fields, api
from .job_utils import shorten_text


class JobCostsTransient(models.Model):
    """
    Costs container, which is related to a job
    """
    _name = 'jobcontrol.job_costs_transient'
    _description = 'Cost container related to jobs for invoicing'
    job_id = fields.Integer(required=True)
    job_name = fields.Char(string='Job Name')
    job_costs_line_ids = fields.One2many(comodel_name="jobcontrol.job_costs_line_transient",
                                         string="Job Cost Entry",
                                         inverse_name="job_costs_id", required=True)
    job_costs_line_add_ids = fields.One2many(comodel_name="jobcontrol.job_costs_line_transient",
                                             string="Job Cost Entry",
                                             inverse_name="job_costs_id",
                                             domain=[('add', '=', True)])
    invoice_id = fields.Integer(string="Invoice ID", required=True)
    invoice_line_id = fields.Integer(string="Invoice Line ID")

    @api.model
    def default_get(self, default_fields):
        res = super(JobCostsTransient, self).default_get(default_fields)
        account_move_record = None
        invoice_id = None
        invoice_line_id = None
        print(f"self._context={self._context}")
        _dict = {} | self._context
        model = _dict.get('active_model', "")
        if model == 'account.move':
            account_move_record = self.env['account.move'].browse(self._context.get('active_ids', []))
            invoice_id = account_move_record.id
        elif model == 'account.move.line':
            account_move_line_record = self.env['account.move.line'].browse(self._context.get('active_ids', []))
            invoice_line_id = account_move_line_record.id
            account_move_record = account_move_line_record.move_id
            invoice_id = account_move_record.id
        else:
            print(f"Job costs are not supported for this model: {self._context.get('active.model')}")
            return res
        if account_move_record:
            if account_move_record.job_id and account_move_record.job_id.id > 0:
                job_id = account_move_record.job_id.id
                job_name = account_move_record.job_id.name
                print(f"Found {account_move_record.name} related job for id {job_id}")
                job = self.env['jobcontrol.job'].browse(job_id)
                lines = []
                for rec in job.job_cost_line_to_invoice:
                    costs_line = self.env['jobcontrol.job_costs'].browse(rec.id)
                    if not costs_line.not_billable:
                        lines.append((0, 0, {
                            'product_id': costs_line.product_id.id,
                            'product_name': costs_line.product_id.name,
                            'product_uom_id': costs_line.product_uom.id,
                            'name': costs_line.name,
                            'cost_line_id': costs_line.id,
                            'product_uom_qty': costs_line.product_uom_qty,
                            'unit_price': costs_line.unit_price,
                            'total_price': costs_line.total_price,
                            'currency_id': costs_line.currency_id,
                            'company_id': costs_line.company_id,
                            'not_billable': costs_line.not_billable,
                            'invoice_line': costs_line.invoice_line
                        }))

                res.update({
                    'job_id': job_id,
                    'job_name': job_name,
                    'invoice_id': invoice_id,
                    'invoice_line_id': invoice_line_id,
                    'job_costs_line_ids': lines})
        else:
            print("no invoice available for adding JobCosts")
        return res

    def add_job_costs_lines(self):
        print(f"Adding job costs lines job: {self.job_id} to invoice: {self.invoice_id}"
              f" invoice_line_id: {self.invoice_line_id}")

        cost_ids = []
        for _jcl_id in self.job_costs_line_add_ids:
            _job_costs_tr_line = self.env['jobcontrol.job_costs_line_transient'].browse(_jcl_id.id)
            cost_ids.append(_job_costs_tr_line.cost_line_id)
            print(f"Add: {_job_costs_tr_line.add} job costs id: {_job_costs_tr_line.cost_line_id}")

        if len(cost_ids) > 0:
            cost_entries = self.env['jobcontrol.job_costs'].browse(cost_ids)
            if self.invoice_line_id > 0:
                invoice_line = self.env['account.move.line'].browse(self.invoice_line_id)
                price_sum = sum(cost_entries.mapped('total_price'))
                print(f"Add: job cost entries {cost_entries} to invoice line {self.invoice_line_id} "
                      f"with cost sum price: {price_sum} + "
                      f"{invoice_line.price_total} = {price_sum + invoice_line.price_total}")
                # update invoice_lines
                cost_entries.invoice_line = invoice_line.id
                # set calculated total price
                invoice_line.credit = price_sum
            else:
                print(f"Need to add invoice lines for job cost entries {cost_entries}")
        else:
            print("No job costs to add")


class JobCostLineTransient(models.TransientModel):
    """
    Costs, which are related to a job
    """
    _name = 'jobcontrol.job_costs_line_transient'
    _description = 'Costs related to jobs for invoicing'
    add = fields.Boolean(string='Add', default=False)
    job_costs_id = fields.Many2one(comodel_name="jobcontrol.job_costs_transient", string="Job Cost Container")
    cost_line_id = fields.Integer(string="Cost Line Id")
    name = fields.Char("Name")
    description = fields.Text("Description")
    display_name = fields.Char(compute="_display_name", string="Display")

    product_id = fields.Integer(string="Product ID")
    product_name = fields.Char(string="Product Name")
    product_uom_id = fields.Integer(string="Product UoM ID")
    product_uom_qty = fields.Float(
        string="Quantity",
        digits='Product Unit of Measure', default=1.0,
        store=True, readonly=False)
    product_uom_name = fields.Char(string="Product")
    unit_price = fields.Float(string="Unit Price", digits=(12, 4))
    total_price = fields.Monetary(string="Total Price")
    company_id = fields.Integer(string="Company")
    currency_id = fields.Integer(string="Currency")
    effective_date = fields.Date(string="Effective Date", default=datetime.now())
    invoiced = fields.Boolean(string="Invoiced")
    not_billable = fields.Boolean(string="Not Billable", default=False)
    invoice_line = fields.Integer(string="Invoice Line")

    def _display_name(self):
        for record in self:
            record.display_name = shorten_text(f"{record.name} {record.product_uom_qty} "
                                               f"{record.product_uom_name}")
