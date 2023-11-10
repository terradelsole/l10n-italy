#  Copyright 2023 Simone Rubino - AionTech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

NEW_MODULE_NAME = "l10n_it_riba"


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr,
        NEW_MODULE_NAME,
        "migrations/16.0.1.0.0/data/noupdate.xml",
    )
    # remove riba.distinta[.line].state refs
    distinta_line_state_refs = env["ir.model.data"].search(
        [
            ("module", "=", "l10n_it_riba"),
            ("name", "like", "selection__riba_distinta_line__state__%"),
        ]
    )
    distinta_line_state_refs.unlink()
    # remove riba.distinta.state refs
    distinta_line_refs = env["ir.model.data"].search(
        [
            ("module", "=", "l10n_it_riba"),
            ("name", "like", "selection__riba_distinta__state%%"),
        ]
    )
    distinta_line_refs.unlink()
