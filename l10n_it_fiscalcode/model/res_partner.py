# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


def _check_person_fiscal_code(fiscal_code):
    """`fiscal_code` is the Fiscal Code of a Person."""
    return len(fiscal_code) == 16


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def check_fiscalcode(self):
        for partner in self:
            fiscal_code = partner.fiscalcode
            if not fiscal_code:
                # Because it is not mandatory
                continue
            elif partner.company_type == 'person':
                # Person case
                if partner.company_name:
                    # In E-commerce, if there is company_name,
                    # the user might insert VAT in fiscalcode field.
                    # Perform the same check as Company case
                    continue
                if not _check_person_fiscal_code(fiscal_code):
                    # Check fiscalcode of a person
                    return False
        return True

    fiscalcode = fields.Char(
        'Fiscal Code', size=16, help="Italian Fiscal Code")

    _constraints = [
        (check_fiscalcode,
         "The fiscal code doesn't seem to be correct.", ["fiscalcode"])
    ]

    @api.onchange('fiscalcode')
    def _fiscalcode_changed(self):
        if self.fiscalcode:
            self.fiscalcode = self.fiscalcode.upper()
