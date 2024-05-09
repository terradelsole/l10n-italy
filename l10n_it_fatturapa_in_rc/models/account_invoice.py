import math

from odoo import _, api, models
from odoo.tools import float_compare


class InvoiceLine(models.Model):
    _inherit = "account.move.line"

    @api.depends(
        "move_id",
        "move_id.move_type",
        "move_id.fiscal_position_id",
        "move_id.fiscal_position_id.rc_type_id",
        "tax_ids",
    )
    def _compute_rc_flag(self):
        if "fatturapa.attachment.in" in self.env.context.get("active_model", []):
            # this means we are importing an e-invoice,
            # so RC flag is already set, where needed
            return
        super()._compute_rc_flag()


class Invoice(models.Model):
    _inherit = "account.move"

    def e_inv_check_amount_tax(self):
        if any(self.invoice_line_ids.mapped("rc")) and self.e_invoice_amount_tax:
            error_message = ""
            amount_added_for_rc = self.get_tax_amount_added_for_rc()
            amount_tax = self.amount_tax - amount_added_for_rc
            if (
                float_compare(
                    amount_tax,
                    self.e_invoice_amount_tax,
                    precision_rounding=self.currency_id.rounding,
                )
                != 0
            ):
                error_message = _(
                    "Taxed amount ({bill_amount_tax}) "
                    "does not match with "
                    "e-bill taxed amount ({e_bill_amount_tax})"
                ).format(
                    bill_amount_tax=amount_tax or 0,
                    e_bill_amount_tax=self.e_invoice_amount_tax,
                )
            return error_message
        else:
            return super(Invoice, self).e_inv_check_amount_tax()

    def e_inv_check_amount_total(self):
        if any(self.invoice_line_ids.mapped("rc")) and self.e_invoice_amount_total:
            error_message = ""
            amount_added_for_rc = self.get_tax_amount_added_for_rc()
            rounding_value = 0.01
            if self.currency_id.rounding:
                rounding_value = self.currency_id.rounding
            rounding_digits = int(math.ceil(math.log10(1 / rounding_value)))
            rounding_factor = math.pow(10, rounding_digits)
            rounded_amount_total = (
                self.amount_total - amount_added_for_rc
            ) * rounding_factor
            int_amnt_total = math.trunc(rounded_amount_total)
            amount_total = int_amnt_total / rounding_factor
            if (
                float_compare(
                    amount_total,
                    self.e_invoice_amount_total,
                    precision_rounding=self.currency_id.rounding,
                )
                != 0
            ):
                error_message = _(
                    "Total amount ({bill_amount_total}) "
                    "does not match with "
                    "e-bill total amount ({e_bill_amount_total})"
                ).format(
                    bill_amount_total=amount_total or 0,
                    e_bill_amount_total=self.e_invoice_amount_total,
                )
            return error_message
        else:
            return super(Invoice, self).e_inv_check_amount_total()
