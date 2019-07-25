#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: ynabintegrationslib.py
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
Main code for ynabintegrationslib.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging

from collections import deque
from .adapters import (YnabAccount,
                       AbnAmroAccount,
                       AbnAmroCreditCardAccount)
from abnamrolib import (Contract,
                        CreditCard)
from ynabintegrationslib import Ynab

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''26-06-2019'''
__copyright__ = '''Copyright 2019, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = '''ynabintegrationslib'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())

TRANSACTIONS_QUEUE_SIZE = 100


class Service:
    """Models a service to retrieve transactions and upload them to YNAB."""

    def __init__(self, ynab_token):
        self._accounts = []
        self._ynab = Ynab(ynab_token)
        self._transactions = deque(maxlen=TRANSACTIONS_QUEUE_SIZE)
        self._abn_contract = None

    def _register_abn_contract(self, account_number, card_number, pin_number):
        if self._abn_contract:
            print('contract already registered')
        else:
            self._abn_contract = Contract(account_number, card_number, pin_number)

    def register_abn_account(self,
                             iban,
                             budget_name,
                             account_name,
                             account_number=None,
                             card_number=None,
                             pin_number=None):
        if all([account_number, card_number, pin_number]):
            self._register_abn_contract(account_number, card_number, pin_number)
        try:
            abn_account = self._abn_contract.get_account_by_iban(iban)
            ynab_account = AbnAmroAccount(abn_account, self._ynab, budget_name, account_name)
            self.register_account(ynab_account)
        except AttributeError:
            print('please supply account credentials along with mapping details')

    def register_credit_card(self, user_name, password, budget_name, account_name):
        credit_card = CreditCard(user_name, password)
        ynab_account = AbnAmroCreditCardAccount(credit_card, self._ynab, budget_name, account_name)
        self.register_account(ynab_account)

    def register_account(self, account):
        """Registers an account on the service.

        Args:
            account (Account): The bank account to register.

        Returns:
            boolean (bool): True on success, False otherwise.

        """
        if not isinstance(account, YnabAccount):
            raise ValueError('Object not of type YnabAccount')
        if account not in self._accounts:
            self._accounts.append(account)
            print('registered')

    def get_latest_transactions(self):
        """Retrieves the latest transactions from all accounts.

        Returns:
            transactions (Transaction): A list of transactions to upload to YNAB.

        """
        transactions = []
        for account in self._accounts:
            for transaction in account.get_latest_transactions():
                if transaction not in self._transactions:
                    self._transactions.append(transaction)
                    transactions.append(transaction)
        return transactions

    def upload_latest_transactions(self):
        self._ynab.upload_transactions(self.get_latest_transactions())
