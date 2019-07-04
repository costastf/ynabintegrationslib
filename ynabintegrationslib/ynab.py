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
from .configuration import YNAB_BUDGET_URL

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
        self._base_url = url
        self._session = self._get_authenticated_session(token)
        self._budgets = None

    def _get_authenticated_session(self, token):
        budget_url = f'{self._base_url}/v1/budgets'
        session = Session()
        headers = {'Authorization': 'Bearer {}'.format(token)}
        session.headers.update(headers)
        response = session.get(budget_url)
        response.raise_for_status()
        return session

    @property
    def budgets(self):
        budget_url = f'{self._base_url}/v1/budgets'
        response = self._session.get(budget_url)
        response.raise_for_status()
        self._budgets = response.json().get('data').get('budgets')
        return self._budgets

    def accounts(self, budget_id):
        account_url = f'{self._base_url}/v1/budgets/{budget_id}/accounts'
        response = self._session.get(account_url)
        response.raise_for_status()
        print(response.json())
        return response.json().get('data').get('accounts')

    def upload_transaction(self, transaction):
        # implement uploading of a single transaction
        pass

    def upload_transactions_bulk(self, transactions):
        # implement uploading of multiple transactions
        pass
