#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: adapters.py
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
Main code for adapters

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import abc
import logging

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
LOGGER_BASENAME = '''adapters'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class YnabTransaction(abc.ABC):
    """Models the interface for ynab transaction"""

    def __init__(self, transaction, account):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self._transaction = transaction
        self._account = account

    def __hash__(self):
        return hash(self._transaction)

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if not isinstance(other, self.__class__):
            raise ValueError('Not a YnabTransaction object')
        return hash(self) == hash(other)

    def __ne__(self, other):
        """Override the default Unequal behavior"""
        if not isinstance(other, self.__class__):
            raise ValueError('Not a YnabTransaction object')
        return hash(self) != hash(other)

    @abc.abstractmethod
    def amount(self):
        """Amount"""
        pass

    @abc.abstractmethod
    def payee_name(self):
        """Payee Name"""
        pass

    @abc.abstractmethod
    def memo(self):
        """Memo"""
        pass

    @abc.abstractmethod
    def date(self):
        """Date"""
        pass

    @staticmethod
    def _clean_up(string):
        return " ".join(string.split())

    @property
    def payload(self):
        """Payload"""
        return {'account_id': self._account.id,
                'amount': self.amount,
                'payee_name': self.payee_name,
                'memo': self.memo,
                'date': self.date}


class AbnAmroAccountTransaction(YnabTransaction):
    """Models an Abn Amro account transaction"""

    @property
    def amount(self):
        """Amount"""
        return int(float(self._transaction.amount) * 10)

    @property
    def payee_name(self):
        """Payee Name"""
        return self._clean_up(self._transaction.counter_account_name)

    @property
    def memo(self):
        """Memo of maximum 200 characters"""
        return self._transaction.description[:200]

    @property
    def date(self):
        """Date"""
        return self._transaction.transaction_date.strftime('%Y-%m-%d')


class AbnAmroCreditCardTransaction(YnabTransaction):
    """Models an Abn Amro credit card transaction"""

    @property
    def amount(self):
        """Amount"""
        return int(self._transaction.billing_amount * 1000)

    @property
    def payee_name(self):
        """Payee Name"""
        return self._clean_up(self._transaction.description)

    @property
    def memo(self):
        """Memo"""
        return (f'Description: {self._transaction.description}\n'
                f'Buyer: {self._transaction.embossing_name}\n'
                f'Merchant Category: {self._transaction.merchant_category_description}\n'
                f'Amount: {self._transaction.billing_amount} {self._transaction.billing_currency}')

    @property
    def date(self):
        """Date"""
        return self._transaction.transaction_date


class YnabAccount(abc.ABC):
    """Models a YNAB account"""

    def __init__(self, account, ynab_service, budget_name, account_name):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self.bank_account = account
        self.ynab = ynab_service
        self._budget = self.ynab.get_budget_by_name(budget_name)
        self._ynab_account = self.budget.get_account_by_name(account_name)

    @property
    def budget(self):
        """Budget"""
        return self._budget

    @property
    def ynab_account(self):
        """Ynab account"""
        return self._ynab_account

    def __hash__(self):
        return hash(self.bank_account)

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if not isinstance(other, self.__class__):
            raise ValueError('Not a Account object')
        return hash(self) == hash(other)

    def __ne__(self, other):
        """Override the default Unequal behavior"""
        if not isinstance(other, self.__class__):
            raise ValueError('Not a Account object')
        return hash(self) != hash(other)

    @abc.abstractmethod
    def transactions(self):
        """Transactions"""
        pass

    @abc.abstractmethod
    def get_latest_transactions(self):
        """Retrieves latest transactions from account"""
        pass


class AbnAmroAccount(YnabAccount):
    """Models an Abn Amro account"""

    @property
    def transactions(self):
        """Transactions"""
        for transaction in self.bank_account.transactions:
            yield AbnAmroAccountTransaction(transaction, self._ynab_account)

    def get_latest_transactions(self):
        """Retrieves latest transactions"""
        for transaction in self.bank_account.get_latest_transactions():
            yield AbnAmroAccountTransaction(transaction, self._ynab_account)


class AbnAmroCreditCardAccount(YnabAccount):
    """Models an Abn Amro credit card account"""

    @property
    def transactions(self):
        """Transactions"""
        for transaction in self.bank_account.transactions:
            yield AbnAmroCreditCardTransaction(transaction, self._ynab_account)

    def get_latest_transactions(self):
        """Retrieves latest transactions"""
        for transaction in self.bank_account.get_current_period_transactions():
            yield AbnAmroCreditCardTransaction(transaction, self._ynab_account)
