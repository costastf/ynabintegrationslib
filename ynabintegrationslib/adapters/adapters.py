
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

    def __init__(self, transaction):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self._transaction = transaction

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
        pass

    @abc.abstractmethod
    def payee_name(self):
        pass

    @abc.abstractmethod
    def memo(self):
        pass

    @abc.abstractmethod
    def date(self):
        pass

    @staticmethod
    def _clean_up(string):
        return " ".join(string.split())

    @property
    def payload(self):
        return {'amount': self.amount,
                'payee_name': self.payee_name,
                'memo': self.memo,
                'date': self.date}


class AbnAmroAccountTransaction(YnabTransaction):

    @property
    def amount(self):
        return int(float(self._transaction.amount) * 100)

    @property
    def payee_name(self):
        return self._clean_up(self._transaction.counter_account_name)

    @property
    def memo(self):
        return self._transaction.description

    @property
    def date(self):
        return self._transaction.transaction_date.strftime('%Y-%m-%d')


class AbnAmroCreditCardTransaction(YnabTransaction):

    @property
    def amount(self):
        return int(self._transaction.billing_amount * 100)

    @property
    def payee_name(self):
        return self._clean_up(self._transaction.description)

    @property
    def memo(self):
        return (f'Description: {self._transaction.description}\n'
                f'Buyer: {self._transaction.embossing_name}\n'
                f'Merchant Category: {self._transaction.merchant_category_description}\n'
                f'Amount: {self._transaction.billing_amount} {self._transaction.billing_currency}')

    @property
    def date(self):
        return self._transaction.transaction_date


class YnabAccount(abc.ABC):

    def __init__(self, account, budget_name, account_name):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self._account = account
        self._budget_name = budget_name
        self._account_name = account_name

    def __hash__(self):
        return hash(self._account)

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
        pass

    @abc.abstractmethod
    def get_latest_transactions(self):
        pass


class AbnAmroAccount(YnabAccount):

    @property
    def transactions(self):
        return self._account.transactions

    def get_latest_transactions(self):
        return self._account.get_latest_transactions()


class AbnAmroCreditCardAccount(YnabAccount):

    @property
    def transactions(self):
        return self._account.transactions

    def get_latest_transactions(self):
        return self._account.get_current_period_transactions()
