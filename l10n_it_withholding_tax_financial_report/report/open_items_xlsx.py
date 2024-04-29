from odoo import _, models


class OpenItemsXslx(models.AbstractModel):
    _inherit = "report.a_f_r.report_open_items_xlsx"

    def _get_report_columns(self, report):
        res = super()._get_report_columns(report)
        net_pay_index = 9
        residual_net_pay_index = 10
        if report.foreign_currency:
            net_pay_index = 12
            residual_net_pay_index = 13
        net_to_pay = {
            net_pay_index: {
                "header": _("Net to pay"),
                "field": "amount_net_pay",
                "type": "amount",
                "width": 14,
            },
            residual_net_pay_index: {
                "header": _("Residual net to pay"),
                "field": "amount_net_pay_residual",
                "field_final_balance": "amount_net_pay_residual",
                "type": "amount",
                "width": 14,
            },
        }
        res.update(net_to_pay)
        return res

    def write_ending_balance_from_dict(
        self,
        my_object,
        type_object,
        total_amount,
        report_data,
        account_id=False,
        partner_id=False,
    ):
        if type_object == "partner":
            my_object["amount_net_pay_residual"] = total_amount[account_id][partner_id][
                "amount_net_pay_residual"
            ]
        elif type_object == "account":
            my_object["amount_net_pay_residual"] = total_amount[account_id][
                "amount_net_pay_residual"
            ]
        return super().write_ending_balance_from_dict(
            my_object,
            type_object,
            total_amount,
            report_data,
            account_id=account_id,
            partner_id=partner_id,
        )
