#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: ynab.py
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
Main code for ynab

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging
from requests import Session
from datetime import datetime

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
LOGGER_BASENAME = '''ynab'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class Ynab:

    def __init__(self, token, url='https://api.youneedabudget.com'):
        logger_name = f'{LOGGER_BASENAME}.{self.__class__.__name__}'
        self._logger = logging.getLogger(logger_name)
        self._api_version = 'v1'
        self._base_url = url
        self.api_url = f'{self._base_url}/{self._api_version}'
        self._session = self._get_authenticated_session(token)
        self._budgets = self.budgets
        self._default_budget = self.default_budget

    def _get_authenticated_session(self, token):
        budget_url = f'{self.api_url}/budgets'
        session = Session()
        headers = {'Authorization': f'Bearer {token}'}
        session.headers.update(headers)
        response = session.get(budget_url)
        response.raise_for_status()
        return session

    @property
    def budgets(self):
        budget_url = f'{self.api_url}/budgets'
        response = self._session.get(budget_url)
        response.raise_for_status()
        return [Budget(self, budget) for budget in response.json().get('data').get('budgets')]

    def get_budget_by_name(self, budget_name):
        return next((budget for budget in self._budgets if budget.name.lower() == budget_name.lower()), None)

    def get_accounts_for_budget(self, budget_name):
        budget = self.get_budget_by_name(budget_name)
        return budget.accounts

    def upload_transactions(self, transactions, budget_id, account_id):
        transaction_url = f'{self.api_url}/budgets/{budget_id}/transactions'
        payload = {"transactions": [transaction.payload for transaction in list(transactions)]}
        response = self._session.post(transaction_url, json=payload)
        response.raise_for_status()
        return response


class Budget:

    def __init__(self, ynab, data):
        self._data = data
        self._ynab = ynab

    @property
    def accounts(self):
        account_url = f'{self._ynab.api_url}/budgets/{self.id}/accounts'
        response = self._ynab._session.get(account_url)
        response.raise_for_status()
        return [Account(account) for account in response.json().get('data', {}).get('accounts', [])]

    @property
    def currency_format(self):
        return self._data.get('currency_format')

    @property
    def date_format(self):
        return self._data.get('date_format')

    @property
    def first_month(self):
        return self._data.get('first_month')

    @property
    def id(self):
        return self._data.get('id')

    @property
    def last_modified_on(self):
        return self._data.get('last_modified_on')

    @property
    def last_month(self):
        return self._data.get('last_month')

    @property
    def name(self):
        return self._data.get('name')

    def get_account_by_name(self, name):
        return next((account for account in self.accounts if account.name.lower() == name.lower()), None)


class Account:

    def __init__(self, data):
        self._data = data

    @property
    def balance(self):
        return self._data.get('balance')

    @property
    def cleared_balance(self):
        return self._data.get('cleared_balance')

    @property
    def closed(self):
        return self._data.get('closed')

    @property
    def deleted(self):
        return self._data.get('deleted')

    @property
    def id(self):
        return self._data.get('id')

    @property
    def name(self):
        return self._data.get('name')

    @property
    def note(self):
        return self._data.get('note')

    @property
    def on_budget(self):
        return self._data.get('on_budget')

    @property
    def transfer_payee_id(self):
        return self._data.get('transfer_payee_id')

    @property
    def type(self):
        return self._data.get('type')
