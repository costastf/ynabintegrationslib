#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: core.py
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
Main code for core.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import abc
import logging

from ynabintegrationslib.ynabintegrationslibexceptions import InvalidAccount, InvalidBudget
from abnamrolib.lib.core import Comparable

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
LOGGER_BASENAME = '''core'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class YnabAccount(Comparable):
    """Models a YNAB account."""

    def __init__(self, bank_account, ynab_service, budget_name, ynab_account_name):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self.bank_account = bank_account
        self.ynab = ynab_service
        self._budget, self._ynab_account = self._get_budget_and_account(budget_name, ynab_account_name)

    def _get_budget_and_account(self, budget_name, account_name):
        budget = self.ynab.get_budget_by_name(budget_name)
        if not budget:
            raise InvalidBudget(budget_name)
        account = budget.get_account_by_name(account_name)
        if not account:
            raise InvalidAccount(account_name)
        return budget, account

    @property
    def budget(self):
        """Budget."""
        return self._budget

    @property
    def ynab_account(self):
        """Ynab account."""
        return self._ynab_account

    def __hash__(self):
        return hash(self.bank_account)

    @abc.abstractmethod
    def transactions(self):
        """Transactions."""
        pass

    @abc.abstractmethod
    def get_latest_transactions(self):
        """Retrieves latest transactions from account."""
        pass


class YnabTransaction(Comparable):
    """Models the interface for ynab transaction."""

    def __init__(self, transaction, account):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self._transaction = transaction
        self.account = account

    def __hash__(self):
        return hash(self._transaction)

    @abc.abstractmethod
    def amount(self):
        """Amount."""
        pass

    @abc.abstractmethod
    def payee_name(self):
        """Payee Name."""
        pass

    @abc.abstractmethod
    def memo(self):
        """Memo."""
        pass

    @abc.abstractmethod
    def date(self):
        """Date."""
        pass

    @staticmethod
    def _clean_up(string):
        return " ".join(string.split())

    @property
    def payload(self):
        """Payload."""
        return {'account_id': self.account.id,
                'amount': self.amount,
                'payee_name': self.payee_name,
                'memo': self.memo,
                'date': self.date}
