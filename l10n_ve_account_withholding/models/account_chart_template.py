###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################
from odoo import models
import logging
_logger = logging.getLogger(__name__)


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def _create_bank_journals(self, company, acc_template_ref):
        """
        Bank - Cash journals are created with this method
        Inherit this function in order to add checks to cash and bank
        journals. This is because usually will be installed before chart loaded
        and they will be disable by default
        """

        bank_journals = super(
            AccountChartTemplate, self)._create_bank_journals(
            company, acc_template_ref)

        # each chart of account / localization should send this key if
        # they want withholding journal to be created
        if company._localization_use_withholdings():
            # creamos diario para retenciones
            inbound_withholding = self.env.ref(
                'account_withholding.account_payment_method_in_withholding')
            outbound_withholding = self.env.ref(
                'account_withholding.account_payment_method_out_withholding')
            journal = self.env['account.journal'].create({
                'name': 'Retenciones',
                'type': 'cash',
                'company_id': company.id,
                'inbound_payment_method_ids': [
                    (4, inbound_withholding.id, None)],
                'outbound_payment_method_ids': [
                    (4, outbound_withholding.id, None)],
            })
            bank_journals += journal

            # we dont want this journal to have accounts and we can not inherit
            # to avoid creation, so we delete it
            to_unlink = journal.default_credit_account_id
            journal.default_credit_account_id = False
            journal.default_debit_account_id = False
            to_unlink.with_context(force_unlink=True).unlink()

        return bank_journals
    