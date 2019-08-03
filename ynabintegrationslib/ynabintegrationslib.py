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

import importlib
import logging
from collections import deque

from ynablib import Ynab

from .lib import YnabContract

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''26-06-2019'''
__copyright__ = '''Copyright 2019, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos", "Gareth Hawker"]
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
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self._accounts = []
        self._contracts = []
        self._ynab = Ynab(ynab_token)
        self._transactions = deque(maxlen=TRANSACTIONS_QUEUE_SIZE)

    @property
    def accounts(self):
        """Accounts."""
        return self._accounts

    @property
    def contracts(self):
        """Contracts."""
        return self._contracts

    def get_contract_by_name(self, name):
        """Retrieves a contract by name.

        Args:
            name: The name of the contract to retrieve

        Returns:
            contract (Contract): A contract if a match is found else None

        """
        return next((contract for contract in self.contracts
                     if contract.name.lower() == name.lower()), None)

    def register_contract(self, name, bank, contract_type, credentials):
        """Registers an account in the service.

        Args:
            name: The friendly name to identify the account by
            bank: The bank of the account
            contract_type: The type of the contract
            credentials: A dictionary with the required credentials to initialize the contract

        Returns:
            bool (bool) : True on success, False otherwise

        """
        try:
            self._contracts.append(YnabContract(name, bank, contract_type, credentials))
            return True
        except Exception:  # pylint: disable=broad-except
            self._logger.exception('Problem registering contract')
            return False

    def register_account(self, contract_name, budget_name, ynab_account_name, account_id=None):
        """Registers an account in the service.

        Args:
            contract_name: The friendly name of the contract the account is part of
            budget_name: The name of the budget in YNAB the account is connected with
            ynab_account_name: The name of the account in YNAB that the account is associated with
            account_id: The id of the account to be identified by

        Returns:
            bool (bool) : True on success, False otherwise

        """
        ynab_contract = self.get_contract_by_name(contract_name)
        if not ynab_contract:
            self._logger.error('Could not get contract by name "%s"', contract_name)
            return False
        try:
            account_wrapper = getattr(importlib.import_module('ynabintegrationslib.adapters'),
                                      f'{ynab_contract.bank}{ynab_contract.type}')
            account = ynab_contract.contract.get_account(account_id)
            self._accounts.append(account_wrapper(account,
                                                  self._ynab,
                                                  budget_name,
                                                  ynab_account_name))
            return True
        except Exception:  # pylint: disable=broad-except
            self._logger.exception('Problem registering account')
            return False

    def get_latest_transactions(self):
        """Retrieves the latest transactions from all accounts.

        Returns:
            transactions (Transaction): A list of transactions to upload to YNAB.

        """
        first_run = False
        if not self._transactions:
            first_run = True
        transactions = []
        for account in self.accounts:
            self._logger.debug('Getting transactions for account "%s"', account.ynab_account.name)
            for transaction in account.get_latest_transactions():
                if transaction not in self._transactions:
                    transactions.append(transaction)
        self._logger.debug('Caching %s transactions', len(transactions))
        self._transactions.extend(transactions)
        if first_run:
            self._logger.info('First run detected, discarding transactions until now')
            return []
        return transactions

    def upload_latest_transactions(self):
        """Uploads latest transactions to YNAB."""
        self.upload_transactions(self.get_latest_transactions())

    def upload_transactions(self, transactions):
        """Uploads the provided transaction objects to YNAB.

        Args:
            transactions (list|Transaction): A list of transaction objects or a single transaction object

        Returns:
            boolean (bool): True on success, False otherwise

        """
        if not transactions:
            self._logger.debug('No transactions to upload')
            return True
        if not isinstance(transactions, (list, tuple, set)):
            transactions = [transactions]
        budgets = {}
        self._logger.debug('Batching transactions per budget id.')
        for transaction in transactions:
            budgets.setdefault(transaction.account.budget.id, []).append(transaction.payload)
        self._logger.debug('Uploading all transactions')
        return all([self._ynab.upload_transactions(budget_id, payloads)
                    for budget_id, payloads in budgets.items()])
