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
import importlib

from ynabinterfaceslib import Comparable

from ynabintegrationslib.ynabintegrationslibexceptions import InvalidAccount, InvalidBudget

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


class YnabContract:  # pylint: disable=too-few-public-methods
    """Models a ynab contract."""

    def __init__(self, name, bank, contract_type, credentials):
        self.name = name
        self.bank = bank
        self.type = contract_type
        self.contract = self._get_contract(bank, contract_type, credentials)

    @staticmethod
    def _get_contract(bank, type_, credentials):
        contract_object = getattr(importlib.import_module('ynabintegrationslib.adapters'),
                                  f'{bank}{type_}Contract')
        return contract_object(**credentials)


class YnabAccount(Comparable):
    """Models a YNAB account."""

    def __init__(self, bank_account, ynab_service, budget_name, ynab_account_name):
        super().__init__(bank_account._data)
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self.bank_account = bank_account
        self.ynab = ynab_service
        self._budget, self._ynab_account = self._get_budget_and_account(budget_name, ynab_account_name)

    @property
    def _comparable_attributes(self):
        return ['budget',
                'ynab_account']

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

    @abc.abstractmethod
    def transactions(self):
        """Transactions."""

    @abc.abstractmethod
    def get_latest_transactions(self):
        """Retrieves latest transactions from account."""


class YnabTransaction(Comparable):
    """Models the interface for ynab transaction."""

    def __init__(self, transaction, account):
        super().__init__(transaction._data)
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self._transaction = transaction
        self.account = account

    @property
    def _comparable_attributes(self):
        return ['account_id',
                'amount',
                'memo',
                'date']

    @property
    def account_id(self):
        """Account ID."""
        return self.account.id

    @abc.abstractmethod
    def amount(self):
        """Amount."""

    @abc.abstractmethod
    def payee_name(self):
        """Payee Name."""

    @abc.abstractmethod
    def memo(self):
        """Memo."""

    @abc.abstractmethod
    def date(self):
        """Date."""

    @staticmethod
    def _clean_up(string):
        return " ".join(string.split()) if string else ''

    @property
    def payload(self):
        """Payload."""
        return {'account_id': self.account.id,
                'amount': self.amount,
                'payee_name': self.payee_name,
                'memo': self.memo,
                'date': self.date}


class YnabServerTransaction(YnabTransaction):
    """Models an ynab uploaded transaction."""

    @property
    def amount(self):
        """Amount."""
        return self._transaction.amount

    @property
    def payee_name(self):
        """Payee Name."""
        return self._transaction.payee_name

    @property
    def memo(self):
        """Memo of maximum 200 characters."""
        return self._transaction.memo

    @property
    def date(self):
        """Date."""
        return self._transaction.date
