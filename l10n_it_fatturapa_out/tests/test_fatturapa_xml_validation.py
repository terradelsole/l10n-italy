# -*- coding: utf-8 -*-
# Copyright 2014 Davide Corio
# Copyright 2015-2016 Lorenzo Battistini - Agile Business Group
# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2019 Sergio Corato
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .fatturapa_common import FatturaPACommon


class TestFatturaPAXMLValidation(FatturaPACommon):

    def setUp(self):
        super(TestFatturaPAXMLValidation, self).setUp()
        obj_acc_fiscalyear = self.env['account.fiscalyear']
        self.fiscalyear = obj_acc_fiscalyear.create(
            vals={
                'name': '2016',
                'code': '2016',
                'date_start': '2016-01-01',
                'date_stop': '2016-12-31',
            }
        )
        self.fiscalyear1 = obj_acc_fiscalyear.create(
            vals={
                'name': '2018',
                'code': '2018',
                'date_start': '2018-01-01',
                'date_stop': '2018-12-31',
            }
        )
        period_obj = self.env['account.period']
        self.period = period_obj.create({
            'name': "Period 01/2016",
            'code': '01/2016',
            'date_start': '2016-01-01',
            'date_stop': '2016-01-31',
            'special': False,
            'fiscalyear_id': self.fiscalyear.id,
        })
        self.period1 = period_obj.create({
            'name': "Period 06/2016",
            'code': '06/2016',
            'date_start': '2016-06-01',
            'date_stop': '2016-06-30',
            'special': False,
            'fiscalyear_id': self.fiscalyear.id,
        })
        self.period2 = period_obj.create({
            'name': "Period 01/2018",
            'code': '01/2018',
            'date_start': '2018-01-01',
            'date_stop': '2018-01-31',
            'special': False,
            'fiscalyear_id': self.fiscalyear1.id,
        })
        self.period3 = period_obj.create({
            'name': "Period 02/2018",
            'code': '02/2018',
            'date_start': '2018-02-01',
            'date_stop': '2018-02-28',
            'special': False,
            'fiscalyear_id': self.fiscalyear1.id,
        })

    def test_1_xml_export(self):
        self.set_sequences(1, 13, '2016')
        invoice = self.invoice_model.create({
            'date_invoice': '2016-01-07',
            'partner_id': self.res_partner_fatturapa_0.id,
            'journal_id': self.sales_journal.id,
            'account_id': self.a_recv.id,
            'payment_term': self.account_payment_term.id,
            'user_id': self.user_demo.id,
            'type': 'out_invoice',
            'currency_id': self.EUR.id,
            'invoice_line': [
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_product_10.id,
                    'name': 'Mouse\nOptical',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 10,
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22.id})]
                }),
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_order_01.id,
                    'name': 'Zed+ Antivirus',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 4,
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22.id})]
                })],
        })
        invoice.signal_workflow('invoice_open')
        res = self.run_wizard(invoice.id)

        self.assertTrue(res)
        attachment = self.attach_model.browse(res['res_id'])
        self.assertEqual(attachment.datas_fname, 'IT06363391001_00001.xml')

        # XML doc to be validated
        xml_content = attachment.datas.decode('base64')
        self.check_content(xml_content, 'IT06363391001_00001.xml')

    def test_2_xml_export(self):
        self.set_sequences(2, 14, '2016')
        invoice = self.invoice_model.create({
            'date_invoice': '2016-06-15',
            'partner_id': self.res_partner_fatturapa_0.id,
            'journal_id': self.sales_journal.id,
            'account_id': self.a_recv.id,
            'payment_term': self.account_payment_term.id,
            'user_id': self.user_demo.id,
            'type': 'out_invoice',
            'currency_id': self.EUR.id,
            'comment': 'prima riga\nseconda riga',
            'invoice_line': [
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_product_10.id,
                    'name': 'Mouse, Optical',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 10,
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22.id})]
                }),
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_order_01.id,
                    'name': 'Zed+ Antivirus',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 4,
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22.id})]
                })],
            'related_documents': [(0, 0, {
                'type': 'order',
                'name': 'PO123',
                'cig': '123',
                'cup': '456',
            })],
        })
        invoice.signal_workflow('invoice_open')
        res = self.run_wizard(invoice.id)
        attachment = self.attach_model.browse(res['res_id'])

        xml_content = attachment.datas.decode('base64')
        self.check_content(xml_content, 'IT06363391001_00002.xml')

    def test_3_xml_export(self):
        self.set_sequences(3, 15, '2016')
        invoice = self.invoice_model.create({
            'date_invoice': '2016-06-15',
            'partner_id': self.res_partner_fatturapa_0.id,
            'journal_id': self.sales_journal.id,
            'account_id': self.a_recv.id,
            'payment_term': self.account_payment_term.id,
            'user_id': self.user_demo.id,
            'type': 'out_invoice',
            'currency_id': self.EUR.id,
            'comment': 'prima riga\nseconda riga',
            'invoice_line': [
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_product_10.id,
                    'name': 'Mouse, Optical',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 10,
                    'admin_ref': 'D122353',
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22.id})]
                }),
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_order_01.id,
                    'name': 'Zed+ Antivirus',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 4,
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22.id})]
                })],
            'related_documents': [(0, 0, {
                'type': 'order',
                'name': 'PO123',
                'cig': '123',
                'cup': '456',
            })],
        })
        invoice.signal_workflow('invoice_open')
        self.AttachFileToInvoice(invoice.id, 'test1.pdf')
        self.AttachFileToInvoice(invoice.id, 'test2.pdf')
        res = self.run_wizard(invoice.id)
        attachment = self.attach_model.browse(res['res_id'])
        xml_content = attachment.datas.decode('base64')

        self.check_content(xml_content, 'IT06363391001_00003.xml')

    def test_4_xml_export(self):
        self.set_sequences(4, 16, '2016')
        invoice = self.invoice_model.create({
            'date_invoice': '2016-06-15',
            'partner_id': self.res_partner_fatturapa_0.id,
            'journal_id': self.sales_journal.id,
            'account_id': self.a_recv.id,
            'payment_term': self.account_payment_term.id,
            'user_id': self.user_demo.id,
            'type': 'out_invoice',
            'currency_id': self.EUR.id,
            'fiscal_position': self.fiscal_position_sp.id,
            'invoice_line': [
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_product_10.id,
                    'name': 'Mouse, Optical',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 10,
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22_SP.id})]
                }),
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_order_01.id,
                    'name': 'Zed+ Antivirus',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 4,
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22_SP.id})]
                })],
        })
        invoice.signal_workflow('invoice_open')
        res = self.run_wizard(invoice.id)
        attachment = self.attach_model.browse(res['res_id'])
        xml_content = attachment.datas.decode('base64')
        self.check_content(xml_content, 'IT06363391001_00004.xml')

    def test_5_xml_export(self):
        self.env.user.company_id.fatturapa_sender_partner = (
            self.intermediario.id)
        self.set_sequences(5, 17, '2016')
        invoice = self.invoice_model.create({
            'date_invoice': '2016-06-15',
            'partner_id': self.res_partner_fatturapa_0.id,
            'journal_id': self.sales_journal.id,
            'account_id': self.a_recv.id,
            'payment_term': self.account_payment_term.id,
            'user_id': self.user_demo.id,
            'type': 'out_invoice',
            'currency_id': self.EUR.id,
            'invoice_line': [
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_product_10.id,
                    'name': 'Mouse, Optical',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 10,
                    'discount': 10,
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22.id})]
                }),
            ],
        })
        invoice.signal_workflow('invoice_open')
        res = self.run_wizard(invoice.id)
        attachment = self.attach_model.browse(res['res_id'])
        xml_content = attachment.datas.decode('base64')
        self.assertEqual(attachment.datas_fname, 'IT03297040366_00005.xml')
        self.check_content(xml_content, 'IT03297040366_00005.xml')

    def test_6_xml_export(self):
        self.product_product_10.default_code = 'ODOOCODE'
        self.product_order_01.ean13 = '0000073513537'
        self.set_sequences(6, 13, '2018')
        invoice = self.invoice_model.create({
            'date_invoice': '2018-01-07',
            'partner_id': self.res_partner_fatturapa_2.id,
            'journal_id': self.sales_journal.id,
            'account_id': self.a_recv.id,
            'payment_term': self.account_payment_term.id,
            'user_id': self.user_demo.id,
            'type': 'out_invoice',
            'currency_id': self.EUR.id,
            'invoice_line': [
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_product_10.id,
                    'name': 'Mouse Optical',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 10,
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22.id})]
                }),
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_order_01.id,
                    'name': 'Zed+ Antivirus',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 4,
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22.id})]
                })],
        })
        invoice.signal_workflow('invoice_open')
        res = self.run_wizard(invoice.id)
        attachment = self.attach_model.browse(res['res_id'])
        self.assertEqual(attachment.datas_fname, 'IT06363391001_00006.xml')

        xml_content = attachment.datas.decode('base64')
        self.check_content(xml_content, 'IT06363391001_00006.xml')

    def test_7_xml_export(self):
        self.product_product_10.default_code = False
        self.product_order_01.ean13 = False
        self.company.partner_id.vat = 'CHE-114.993.395 IVA'
        self.company.partner_id.name = 'Azienda estera'
        self.company.partner_id.city = 'Lugano'
        self.company.partner_id.state_id = False
        self.company.partner_id.country_id = self.env.ref('base.ch').id
        self.company.fatturapa_tax_representative = self.intermediario.id
        self.company.fatturapa_stabile_organizzazione = (
            self.stabile_organizzazione.id)
        self.set_sequences(7, 14, '2018')
        invoice = self.invoice_model.create({
            'date_invoice': '2018-01-07',
            'partner_id': self.res_partner_fatturapa_2.id,
            'journal_id': self.sales_journal.id,
            'account_id': self.a_recv.id,
            'payment_term': self.account_payment_term.id,
            'user_id': self.user_demo.id,
            'type': 'out_invoice',
            'currency_id': self.EUR.id,
            'invoice_line': [
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_product_10.id,
                    'name': 'Mouse Optical',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 10,
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22.id})]
                }),
            ],
        })
        invoice.signal_workflow('invoice_open')
        res = self.run_wizard(invoice.id)
        attachment = self.attach_model.browse(res['res_id'])
        self.assertEqual(
            attachment.datas_fname, 'CHE114993395IVA_00007.xml')

        xml_content = attachment.datas.decode('base64')
        self.check_content(xml_content, 'CHE114993395IVA_00007.xml')

    def test_8_xml_export(self):
        self.tax_22.price_include = True
        self.set_sequences(8, 15, '2018')
        invoice = self.invoice_model.create({
            'date_invoice': '2018-01-07',
            'partner_id': self.res_partner_fatturapa_2.id,
            'journal_id': self.sales_journal.id,
            'account_id': self.a_recv.id,
            'payment_term': self.account_payment_term.id,
            'user_id': self.user_demo.id,
            'type': 'out_invoice',
            'currency_id': self.EUR.id,
            'comment': "firsrt line\n\nsecond line",
            'invoice_line': [
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_product_10.id,
                    'name': 'Mouse Optical',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 10,
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22.id})]
                }),
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_order_01.id,
                    'name': 'Zed+ Antivirus',
                    'quantity': 1,
                    'uos_id': self.product_uom_unit.id,
                    'price_unit': 4,
                    'invoice_line_tax_id': [(6, 0, {
                        self.tax_22.id})]
                })],
        })
        invoice.signal_workflow('invoice_open')
        res = self.run_wizard(invoice.id)
        attachment = self.attach_model.browse(res['res_id'])
        self.assertEqual(attachment.datas_fname, 'IT06363391001_00008.xml')

        xml_content = attachment.datas.decode('base64')
        self.check_content(xml_content, 'IT06363391001_00008.xml')

    def test_9_xml_export(self):
        self.tax_22.price_include = True
        self.set_sequences(9, 18, '2018-01-07')
        partner = self.res_partner_fatturapa_4
        partner.onchange_country_id_e_inv()
        partner.write(partner._convert_to_write(partner._cache))
        self.assertEqual(partner.codice_destinatario, 'XXXXXXX')
        invoice = self.invoice_model.create({
            'date_invoice': '2018-01-07',
            'partner_id': partner.id,
            'journal_id': self.sales_journal.id,
            'account_id': self.a_recv.id,
            'payment_term_id': self.account_payment_term.id,
            'user_id': self.user_demo.id,
            'type': 'out_invoice',
            'currency_id': self.AED.id,
            'invoice_line_ids': [
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_product_10.id,
                    'name': 'Mouse Optical',
                    'quantity': 1,
                    'uom_id': self.product_uom_unit.id,
                    'price_unit': 10,
                    'invoice_line_tax_ids': [(6, 0, {
                        self.tax_22.id})]
                }),
                (0, 0, {
                    'account_id': self.a_sale.id,
                    'product_id': self.product_order_01.id,
                    'name': 'Zed+ Antivirus',
                    'quantity': 1,
                    'uom_id': self.product_uom_unit.id,
                    'price_unit': 4,
                    'invoice_line_tax_ids': [(6, 0, {
                        self.tax_22.id})]
                })],
        })
        invoice.action_invoice_open()
        res = self.run_wizard(invoice.id)
        attachment = self.attach_model.browse(res['res_id'])
        self.assertEqual(attachment.datas_fname, 'IT06363391001_00009.xml')

        xml_content = attachment.datas.decode('base64')
        self.check_content(xml_content, 'IT06363391001_00009.xml')
