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
from .adapters import YnabAccount

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

    def __init__(self):
        self._accounts = []
        self._transactions = deque(maxlen=TRANSACTIONS_QUEUE_SIZE)

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
