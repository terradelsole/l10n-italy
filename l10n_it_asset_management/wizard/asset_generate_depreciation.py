# Author(s): Silvio Gregorini (silviogregorini@openforce.it)
# Copyright 2019 Openforce Srls Unipersonale (www.openforce.it)
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.fields import Command
from odoo.tools import format_date


class WizardAssetsGenerateDepreciations(models.TransientModel):
    _name = "wizard.asset.generate.depreciation"
    _description = "Generate Asset Depreciations"

    @api.model
    def get_default_company_id(self):
        return self.env.company

    @api.model
    def get_default_date_dep(self):
        fiscal_year = self.env["account.fiscal.year"].get_fiscal_year_by_date(
            fields.Date.today(), company=self.env.company, miss_raise=False
        )
        if fiscal_year:
            return fiscal_year.date_to
        return fields.Date.today()

    @api.model
    def get_default_type_ids(self):
        return [Command.set(self.env["asset.depreciation.type"].search([]).ids)]

    asset_ids = fields.Many2many(
        "asset.asset",
        string="Assets",
    )

    category_ids = fields.Many2many(
        "asset.category",
        string="Categories",
    )

    company_id = fields.Many2one(
        "res.company",
        default=get_default_company_id,
        string="Company",
    )

    date_dep = fields.Date(
        default=get_default_date_dep,
        required=True,
        string="Depreciation Date",
    )

    type_ids = fields.Many2many(
        "asset.depreciation.type",
        default=get_default_type_ids,
        required=True,
        string="Depreciation Types",
    )

    period = fields.Selection(
        selection=[
            ("year", "Year"),
            ("month", "Month"),
        ],
        default="year",
        required=True,
    )
    missing_fiscal_year_warning = fields.Text(
        compute="_compute_missing_fiscal_year_warning",
        help="Message to warn the user that some fiscal years are missing.",
    )

    @api.depends(
        "date_dep",
        "asset_ids.purchase_date",
    )
    def _compute_missing_fiscal_year_warning(self):
        _get_passed_years = self.env["account.fiscal.year"]._get_passed_years
        for generate_depreciation in self:
            depreciation_date = generate_depreciation.date_dep
            for asset in generate_depreciation.asset_ids:
                asset_date = asset.purchase_date
                passed_years = depreciation_date.year - asset_date.year + 1
                passed_fiscal_years = _get_passed_years(asset_date, depreciation_date)
                if passed_years != passed_fiscal_years:
                    missing_fiscal_year_warning = _(
                        "Some years between %(asset_date)s and %(depreciation_date)s "
                        "have no configured fiscal year "
                        "and will not be counted for depreciation.\n"
                        "Please configure every fiscal year "
                        "that has to be counted for depreciation.",
                        asset_date=format_date(generate_depreciation.env, asset_date),
                        depreciation_date=format_date(
                            generate_depreciation.env, depreciation_date
                        ),
                    )
                    break
            else:
                missing_fiscal_year_warning = False
            generate_depreciation.missing_fiscal_year_warning = (
                missing_fiscal_year_warning
            )

    def do_generate(self):
        """
        Launches the generation of new depreciation lines for the retrieved
        assets.
        Reloads the current window if necessary.
        """
        self.ensure_one()
        # Add depreciation date in context just in case
        deps = self.env["asset.depreciation"]
        all_deps = self.with_context(dep_date=self.date_dep).get_depreciations()
        for dep in all_deps:
            if (
                not dep.last_depreciation_date
                or dep.last_depreciation_date < self.date_dep
            ):
                deps |= dep
        if deps:
            dep_lines = deps.generate_depreciation_lines(
                self.date_dep, period=self.period
            )
            deps.post_generate_depreciation_lines(dep_lines)
        if self._context.get("reload_window"):
            return {"type": "ir.actions.client", "tag": "reload"}

    def get_depreciations(self):
        self.ensure_one()
        domain = self.get_depreciations_domain()
        return self.env["asset.depreciation"].search(domain)

    def get_depreciations_domain(self):
        domain = [
            ("amount_residual", ">", 0),
            ("date_start", "!=", False),
            ("date_start", "<", self.date_dep),
            ("type_id", "in", self.type_ids.ids),
        ]
        if self.asset_ids:
            domain += [("asset_id", "in", self.asset_ids.ids)]
        if self.category_ids:
            domain += [("asset_id.category_id", "in", self.category_ids.ids)]
        if self.company_id:
            domain += [("company_id", "=", self.company_id.id)]
        return domain
