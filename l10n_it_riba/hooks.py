# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def pre_absorb_old_module(cr):
    if openupgrade.is_module_installed(cr, "l10n_it_ricevute_bancarie"):
        openupgrade.update_module_names(
            cr,
            [
                ("l10n_it_ricevute_bancarie", "l10n_it_riba"),
            ],
            merge_modules=True,
        )
