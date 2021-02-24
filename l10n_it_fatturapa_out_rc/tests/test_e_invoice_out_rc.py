# -*- coding: utf-8 -*-
from openerp.addons.l10n_it_reverse_charge.tests.rc_common import ReverseChargeCommon
from openerp.addons.l10n_it_fatturapa_out.tests.fatturapa_common import FatturaPACommon
from openerp.exceptions import Warning as UserError


class TestReverseCharge(ReverseChargeCommon, FatturaPACommon):

    def setUp(self):
        super(TestReverseCharge, self).setUp()
        self.company = self.rc_type_ieu.company_id
        self.company.vat = "IT10538570960"  # 06363391001 gives 00399 error
        self.company.fatturapa_art73 = False
        self.rc_type_ieu.partner_type = "other"
        self.rc_type_ieu.partner_id = self.company.partner_id.id
        self.rc_type_ieu.fiscal_document_type_id = self.env.ref(
            "l10n_it_fiscal_document_type.15").id
        self.rc_type_eeu.partner_id = self.company.partner_id.id
        self.rc_type_eeu.fiscal_document_type_id = self.env.ref(
            "l10n_it_fiscal_document_type.15").id
        self.tax_22vi.kind_id = self.env.ref("l10n_it_account_tax_kind.n6").id
        self.supplier_intraEU.customer = True
        self.customer_invoice_account = self.env['account.account'].search(
            [('user_type', '=', self.env.ref(
                'account.data_account_type_receivable').id)], limit=1).id
        self.supplier_invoice_account = self.env['account.account'].search(
            [('user_type', '=', self.env.ref(
                'account.data_account_type_payable').id)], limit=1).id
        self.sale_invoice_line_account = self.env['account.account'].search(
            [('user_type', '=', self.env.ref(
                'account.data_account_type_income').id)], limit=1).id
        self.purchase_invoice_line_account = self.env['account.account'].search(
            [('user_type', '=', self.env.ref(
                'account.data_account_type_expense').id)], limit=1).id

    def set_sequence_journal_selfinvoice(self, invoice_number, year):
        inv_seq = self.journal_selfinvoice.sequence_id
        inv_seq.prefix = inv_seq.prefix % {'year': year}
        inv_seq.number_next_actual = invoice_number

    def set_sequence_journal_selfinvoice_extra(self, invoice_number, year):
        inv_seq = self.journal_selfinvoice_extra.sequence_id
        inv_seq.prefix = inv_seq.prefix % {'year': year}
        inv_seq.number_next_actual = invoice_number

    def set_bill_sequence(self, invoice_number, year):
        seq_pool = self.env['ir.sequence']
        inv_seq = seq_pool.search([
            ('name', '=', 'Account Default Expenses Journal'),
        ])[0]
        inv_seq.prefix = inv_seq.prefix % {'year': year}
        inv_seq.number_next_actual = invoice_number

    def test_intra_EU(self):
        self.set_sequence_journal_selfinvoice(15, '2019')
        self.set_bill_sequence(25, '2019')
        self.supplier_intraEU.property_payment_term_id = self.term_15_30.id
        invoice = self.invoice_model.create({
            'partner_id': self.supplier_intraEU.id,
            'account_id': self.invoice_account,
            'journal_id': self.purchases_journal.id,
            'type': 'in_invoice',
            'date_invoice': '2019-01-15',
            'reference': 'EU-SUPPLIER-REF'
        })
        res = invoice.onchange_partner_id(invoice.type, invoice.partner_id.id)
        invoice.fiscal_position = res['value']['fiscal_position']

        invoice_line_vals = {
            'name': 'Invoice for sample product',
            'account_id': self.invoice_line_account,
            'invoice_id': invoice.id,
            'product_id': self.sample_product.id,
            'price_unit': 100,
            'invoice_line_tax_id': [(4, self.tax_22ai.id, 0)]}
        invoice_line = self.invoice_line_model.create(invoice_line_vals)
        invoice_line.onchange_invoice_line_tax_id()
        self.env['account.invoice.tax'].compute(invoice)
        invoice.signal_workflow('invoice_open')

        self.assertEqual(
            invoice.rc_self_invoice_id.fiscal_document_type_id.code, "TD17")
        with self.assertRaises(UserError):
            # Impossible to set IdFiscaleIVA
            self.run_wizard(invoice.rc_self_invoice_id.id)
        self.supplier_intraEU.vat = "BE0477472701"
        with self.assertRaises(UserError):
            # Street is not set
            self.run_wizard(invoice.rc_self_invoice_id.id)
        self.supplier_intraEU.street = "Street"
        self.supplier_intraEU.zip = "12345"
        self.supplier_intraEU.city = "city"
        self.supplier_intraEU.country_id = self.env.ref("base.be")
        res = self.run_wizard(invoice.rc_self_invoice_id.id)
        attachment = self.attach_model.browse(res['res_id'])
        self.set_e_invoice_file_id(attachment, 'IT10538570960_00002.xml')
        xml_content = attachment.datas.decode('base64')
        self.check_content(
            xml_content, 'IT10538570960_00002.xml', "l10n_it_fatturapa_out_rc")

    def test_intra_EU_customer(self):
        self.set_sequence_journal_selfinvoice(15, '2020')
        self.set_bill_sequence(25, '2020')
        self.supplier_intraEU.property_payment_term_id = self.term_15_30.id
        invoice = self.invoice_model.create({
            'partner_id': self.supplier_intraEU.id,
            'account_id': self.customer_invoice_account,
            'type': 'out_invoice',
            'date_invoice': '2020-12-01',
            'reference': 'EU-CUSTOMER-REF'
        })

        invoice_line_vals = {
            'name': 'Invoice for sample product',
            'account_id': self.sale_invoice_line_account,
            'invoice_id': invoice.id,
            'product_id': self.sample_product.id,
            'price_unit': 100,
            'invoice_line_tax_id': [(4, self.tax_22vi.id, 0)]}
        invoice_line = self.invoice_line_model.create(invoice_line_vals)
        invoice_line.onchange_invoice_line_tax_id()
        self.env['account.invoice.tax'].compute(invoice)
        invoice.signal_workflow('invoice_open')
        self.assertFalse(invoice.rc_self_invoice_id)

    def test_intra_EU_draft(self):
        self.set_sequence_journal_selfinvoice(15, '2020')
        self.set_bill_sequence(25, '2020')
        self.supplier_intraEU.property_payment_term_id = self.term_15_30.id
        invoice = self.invoice_model.create({
            'partner_id': self.supplier_intraEU.id,
            'account_id': self.invoice_account,
            'journal_id': self.purchases_journal.id,
            'type': 'in_invoice',
            'date_invoice': '2020-12-01',
            'reference': 'EU-SUPPLIER-REF'
        })
        res = invoice.onchange_partner_id(invoice.type, invoice.partner_id.id)
        invoice.fiscal_position = res['value']['fiscal_position']

        invoice_line_vals = {
            'name': 'Invoice for sample product',
            'account_id': self.invoice_line_account,
            'invoice_id': invoice.id,
            'product_id': self.sample_product.id,
            'price_unit': 100,
            'invoice_line_tax_id': [(4, self.tax_22ai.id, 0)]}
        invoice_line = self.invoice_line_model.create(invoice_line_vals)
        invoice_line.onchange_invoice_line_tax_id()
        self.env['account.invoice.tax'].compute(invoice)
        invoice.signal_workflow('invoice_open')
        self.assertIsNot(bool(invoice.rc_self_invoice_id), False)
        self.assertEqual(invoice.rc_self_invoice_id.state, 'paid')
        invoice.journal_id.update_posted = True
        invoice.signal_workflow('invoice_cancel')
        self.assertEqual(invoice.rc_self_invoice_id.state, 'cancel')
        with self.assertRaises(UserError):
            invoice.rc_self_invoice_id.action_cancel_draft()

    def test_intra_EU_supplier_refund(self):
        self.set_sequence_journal_selfinvoice(16, '2020')
        self.set_bill_sequence(26, '2020')
        self.supplier_intraEU.property_payment_term_id = self.term_15_30.id
        invoice = self.invoice_model.create({
            'partner_id': self.supplier_intraEU.id,
            'account_id': self.supplier_invoice_account,
            'journal_id': self.purchases_journal.id,
            'type': 'in_refund',
            'date_invoice': '2020-12-01',
            'reference': 'EU-SUPPLIER-REF',
        })
        res = invoice.onchange_partner_id(invoice.type, invoice.partner_id.id)
        invoice.fiscal_position = res['value']['fiscal_position']
        self.assertEqual(
            invoice.fiscal_document_type_id.code, "TD04")
        invoice_line_vals = {
            'name': 'Invoice for sample product',
            'account_id': self.purchase_invoice_line_account,
            'invoice_id': invoice.id,
            'product_id': self.sample_product.id,
            'price_unit': 100,
            'invoice_line_tax_id': [(4, self.tax_22ai.id, 0)]}
        invoice_line = self.invoice_line_model.create(invoice_line_vals)
        invoice_line.onchange_invoice_line_tax_id()
        self.env['account.invoice.tax'].compute(invoice)
        invoice.signal_workflow('invoice_open')
        self.assertEqual(
            invoice.rc_self_invoice_id.fiscal_document_type_id.code, "TD17")
        with self.assertRaises(UserError):
            # Impossible to set IdFiscaleIVA
            self.run_wizard(invoice.rc_self_invoice_id.id)
        self.supplier_intraEU.vat = "BE0477472701"
        with self.assertRaises(UserError):
            # Street is not set
            self.run_wizard(invoice.rc_self_invoice_id.id)
        self.supplier_intraEU.street = "Street"
        self.supplier_intraEU.zip = "12345"
        self.supplier_intraEU.city = "city"
        self.supplier_intraEU.country_id = self.env.ref("base.be")
        res = self.run_wizard(invoice.rc_self_invoice_id.id)
        attachment = self.attach_model.browse(res['res_id'])
        self.set_e_invoice_file_id(attachment, 'IT10538570960_00003.xml')
        xml_content = attachment.datas.decode('base64')

        self.check_content(
            xml_content, 'IT10538570960_00003.xml', "l10n_it_fatturapa_out_rc")

    def test_extra_EU(self):
        self.set_sequence_journal_selfinvoice_extra(1, '2020')
        self.set_bill_sequence(27, '2020')
        self.supplier_extraEU.property_payment_term_id = self.term_15_30.id
        self.rc_type_eeu.with_supplier_self_invoice = False
        invoice = self.invoice_model.create({
            'partner_id': self.supplier_extraEU.id,
            'account_id': self.invoice_account,
            'journal_id': self.purchases_journal.id,
            'type': 'in_invoice',
            'date_invoice': '2020-12-01',
            'reference': 'EXEU-SUPPLIER-REF'
        })
        res = invoice.onchange_partner_id(invoice.type, invoice.partner_id.id)
        invoice.fiscal_position = res['value']['fiscal_position']

        invoice_line_vals = {
            'name': 'Invoice for sample product',
            'account_id': self.invoice_line_account,
            'invoice_id': invoice.id,
            'product_id': self.sample_product.id,
            'price_unit': 100,
            'invoice_line_tax_id': [(4, self.tax_22ae.id, 0)]}
        invoice_line = self.invoice_line_model.create(invoice_line_vals)
        invoice_line.onchange_invoice_line_tax_id()
        self.env['account.invoice.tax'].compute(invoice)
        invoice.signal_workflow('invoice_open')
        self.assertEqual(
            invoice.rc_self_invoice_id.fiscal_document_type_id.code, "TD17")
        with self.assertRaises(UserError):
            # Impossible to set IdFiscaleIVA
            self.run_wizard(invoice.rc_self_invoice_id.id)
        self.supplier_extraEU.vat = "US484762844"
        with self.assertRaises(UserError):
            # Street is not set
            self.run_wizard(invoice.rc_self_invoice_id.id)
        self.supplier_extraEU.street = "Street"
        self.supplier_extraEU.zip = "12345"
        self.supplier_extraEU.city = "city"
        self.supplier_extraEU.country_id = self.env.ref("base.us")
        res = self.run_wizard(invoice.rc_self_invoice_id.id)
        attachment = self.attach_model.browse(res['res_id'])
        self.set_e_invoice_file_id(attachment, 'IT10538570960_00004.xml')
        xml_content = attachment.datas.decode('base64')
        self.check_content(
            xml_content, 'IT10538570960_00004.xml', "l10n_it_fatturapa_out_rc")
