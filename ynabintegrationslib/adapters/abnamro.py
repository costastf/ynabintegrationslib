#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: abnamro.py
#
# Copyright 2019 Costas Tyfoxylos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for abnamro.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging

from abnamrolib import AccountContract as AbnAmroAccountContract
from abnamrolib import CreditCardContract as AbnAmroCreditCardContract

from ynabintegrationslib.lib.core import YnabAccount, YnabTransaction

assert AbnAmroAccountContract
assert AbnAmroCreditCardContract

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''24-06-2019'''
__copyright__ = '''Copyright 2019, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = '''abnamro'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class AbnAmroAccount(YnabAccount):
    """Models an Abn Amro account."""

    @property
    def _comparable_attributes(self):
        return ['ynab_account_name',
                'bank_account_number']

    @property
    def ynab_account_name(self):
        """Ynab account name."""
        return self.ynab_account.name

    @property
    def bank_account_number(self):
        """Bank account number."""
        return self.bank_account.account_number

    @property
    def transactions(self):
        """Transactions."""
        for transaction in self.bank_account.transactions:
            yield AbnAmroAccountTransaction(transaction, self._ynab_account)

    def get_latest_transactions(self):
        """Retrieves latest transactions."""
        for transaction in self.bank_account.get_latest_transactions():
            yield AbnAmroAccountTransaction(transaction, self._ynab_account)

    def get_transactions_for_date(self, date):
        """Retrieves transactions for date."""
        for transaction in self.bank_account.get_transactions_for_date(date):
            yield AbnAmroAccountTransaction(transaction, self._ynab_account)

    def get_transactions_for_date_range(self, date_from, date_to):
        """Retrieves transactions for date."""
        for transaction in self.bank_account.get_transactions_for_date_range(date_from, date_to):
            yield AbnAmroAccountTransaction(transaction, self._ynab_account)

    def get_transactions_since_date(self, date):
        """Retrieves transactions for date."""
        for transaction in self.bank_account.transactions_since_date(date):
            yield AbnAmroAccountTransaction(transaction, self._ynab_account)


class AbnAmroCreditCard(YnabAccount):
    """Models an Abn Amro credit card account."""

    @property
    def _comparable_attributes(self):
        return ['ynab_account_name',
                'bank_account_number']

    @property
    def ynab_account_name(self):
        """Ynab account name."""
        return self.ynab_account.name

    @property
    def bank_account_number(self):
        """Bank account number."""
        return self.bank_account.number

    @property
    def transactions(self):
        """Transactions."""
        for transaction in self.bank_account.transactions:
            yield AbnAmroCreditCardTransaction(transaction, self._ynab_account)

    def get_latest_transactions(self):
        """Retrieves latest transactions."""
        for transaction in self.bank_account.get_current_period_transactions():
            yield AbnAmroCreditCardTransaction(transaction, self._ynab_account)


class AbnAmroAccountTransaction(YnabTransaction):
    """Models an Abn Amro account transaction."""

    @property
    def amount(self):
        """Amount."""
        return int(float(self._transaction.amount) * 1000) if self._transaction.amount else None

    @property
    def payee_name(self):
        """Payee Name."""
        return self._clean_up(self._transaction.counter_account_name)

    @property
    def memo(self):
        """Memo of maximum 200 characters."""
        return self._transaction.description[:200]

    @property
    def date(self):
        """Date."""
        return self._transaction.transaction_date.strftime('%Y-%m-%d')


class AbnAmroCreditCardTransaction(YnabTransaction):
    """Models an Abn Amro credit card transaction."""

    @property
    def amount(self):
        """Amount."""
        amount = int(self._transaction.billing_amount * 1000)
        return abs(amount) if self._transaction.type_of_transaction == 'P' else amount * -1

    @property
    def payee_name(self):
        """Payee Name."""
        return self._clean_up(self._transaction.description)

    @property
    def memo(self):
        """Memo."""
        return (f'Description: {self._transaction.description}\n'
                f'Buyer: {self._transaction.embossing_name}\n'
                f'Merchant Category: {self._transaction.merchant_category_description}\n'
                f'Amount: {self._transaction.billing_amount} {self._transaction.billing_currency}')[:200]

    @property
    def date(self):
        """Date."""
        return self._transaction.transaction_date

    @property
    def is_reserved(self):
        """Is reserved."""
        return self._transaction.type_of_transaction == 'A'
