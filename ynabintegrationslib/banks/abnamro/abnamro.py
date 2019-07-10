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
Main code for abnamro

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging
from datetime import date
from time import sleep

from selenium.common.exceptions import TimeoutException
from urllib3.util import parse_url

from ynabintegrationslib.lib.core import YnabTransaction, AccountAuthenticator, Account

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


class AbnAmroAccountAuthenticator(AccountAuthenticator):

    def authenticate(self,  # pylint: disable=arguments-differ
                     account_number,
                     card_number,
                     pin_number,
                     url='https://www.abnamro.nl/portalserver/my-abnamro/my-overview/overview/index.html'):
        self._logger.info('Loading login page')
        self._driver.get(url)
        self._logger.info('Accepting cookies')
        try:
            self._click_on("//*[text()='Save cookie-level']")
        except TimeoutException:
            self._logger.warning("Cookies window didn't pop up")
        self._logger.info('Logging in')
        element = self._driver.find_element_by_xpath("//*[(@label='Identification code')]")
        element.click()
        self._driver.find_element_by_name('accountNumber').send_keys(account_number)
        self._driver.find_element_by_name('cardNumber').send_keys(card_number)
        self._driver.find_element_by_name('inputElement').send_keys(pin_number)
        self._driver.find_element_by_id('login-submit').click()
        return True


class Contract:

    def __init__(self, data):
        self._data = data

    @property
    def number(self):
        return self._data.get('contract', {}).get('contractNumber')

    @property
    def account_number(self):
        return self._data.get('contract', {}).get('accountNumber')

    @property
    def product(self):
        return self._data.get('product')

    @property
    def customer(self):
        return self._data.get('customer')

    @property
    def parent_contract(self):
        return self._data.get('parentContract')


class AbnAmroAccountTransaction(YnabTransaction):  # pylint: disable=too-many-public-methods
    """Models a banking transaction"""

    @property
    def mutation_code(self):
        return self._data.get('mutationCode')

    @property
    def description(self):
        return ' '.join([line.strip() for line in self._data.get('descriptionLines', [])])

    @staticmethod
    def _timestamp_to_date(timestamp):
        return date.fromtimestamp(int(timestamp) / 1000)

    @property
    def transaction_date(self):
        return self._timestamp_to_date(self._data.get('transactionDate'))

    @property
    def value_date(self):
        return self._timestamp_to_date(self._data.get('valueDate'))

    @property
    def book_date(self):
        return self._timestamp_to_date(self._data.get('bookDate'))

    @property
    def balance_after_mutation(self):
        return self._data.get('balanceAfterMutation')

    @property
    def transaction_type(self):
        return self._data.get('debitCredit')

    @property
    def indicator_digital_invoice(self):
        return self._data.get('indicatorDigitalInvoice')

    @property
    def counter_account_number(self):
        return self._data.get('counterAccountNumber')

    @property
    def counter_account_type(self):
        return self._data.get('counterAccountType')

    @property
    def counter_account_name(self):
        return self._data.get('counterAccountName')

    @property
    def currency_iso_code(self):
        return self._data.get('currencyIsoCode')

    @property
    def source_inquiry_number(self):
        return self._data.get('sourceInquiryNumber')

    @property
    def account_number(self):
        return self._data.get('accountNumber')

    @property
    def account_number_type(self):
        return self._data.get('accountNumberType')

    @property
    def transaction_timestamp(self):
        return self._data.get('transactionTimestamp')

    @property
    def status_timestamp(self):
        return self._data.get('statusTimestamp')

    @property
    def amount(self):
        return int(float(self._data.get('amount')) * 100)

    @property
    def payee_name(self):
        return self.counter_account_name

    @property
    def memo(self):
        return self.description

    @property
    def date(self):
        return self.transaction_date.strftime('%Y-%m-%d')


class AbnAmroContract(Account):  # pylint: disable=too-many-instance-attributes
    """Models the service"""

    def __init__(self, account_number, card_number, pin_number, url='https://www.abnamro.nl'):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self.account_number = account_number
        self.card_number = card_number
        self.pin_number = pin_number
        self._base_url = url
        self._iban_number = None
        self._host = parse_url(url).host
        self._session = self._get_authenticated_session()

    @property
    def iban_number(self):
        if self._iban_number is None:
            contract = next((contract for contract in self.contracts
                             if contract.number == self.account_number), None)
            if not contract:
                raise ValueError
            self._iban_number = contract.account_number
        return  self._iban_number

    @property
    def contracts(self):
        url = f'{self._base_url}/contracts'
        params = {'productGroups': 'PAYMENT_ACCOUNTS'}
        headers = {'x-aab-serviceversion': 'v2'}
        response = self._session.get(url, params=params, headers=headers)
        response.raise_for_status()
        return [Contract(data) for data in response.json().get('contractList', [])]

    def _get_authenticated_session(self):
        authenticator = AbnAmroAccountAuthenticator()
        authenticator.authenticate(self.account_number, self.card_number, self.pin_number)
        sleep(2)  # give time to the headless browser to execute all the code to get all the cookies
        session = authenticator.get_authenticated_session()
        session.headers.update({'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0)'
                                               'Gecko/20100101 Firefox/67.0')})
        authenticator.quit()
        self.original_get = session.get  # pylint: disable=attribute-defined-outside-init
        session.get = self._patched_get
        return session

    def _patched_get(self, *args, **kwargs):
        url = args[0]
        self._logger.debug('Using patched get request for url %s', url)
        response = self.original_get(*args, **kwargs)
        if not url.startswith(self._base_url):
            self._logger.debug('Url "%s" requested is not from abn amro account api, passing through', url)
            return response
        if response.status_code == 401:
            self._logger.info('Expired session detected, trying to re authenticate!')
            self._session = self._get_authenticated_session()
            response = self.original_get(*args, **kwargs)
        return response

    def get_latest_transactions(self):
        url = f'{self._base_url}/mutations/{self.iban_number}'
        headers = {'x-aab-serviceversion': 'v3'}
        response = self._session.get(url, headers=headers)
        response.raise_for_status()
        return [AbnAmroAccountTransaction(data.get('mutation'))
                for data in response.json().get('mutationsList', {}).get('mutations', [])]

    def _get_transactions(self, params=None):
        url = f'{self._base_url}/mutations/{self.iban_number}'
        headers = {'x-aab-serviceversion': 'v3'}
        response = self._session.get(url, headers=headers, params=params)
        response.raise_for_status()
        mutations_list = response.json().get('mutationsList', {})
        last_mutation_key = mutations_list.get('lastMutationKey', None)
        transactions = [AbnAmroAccountTransaction(data.get('mutation'))
                        for data in mutations_list.get('mutations')]
        return transactions, last_mutation_key

    @property
    def transactions(self):
        transactions, last_mutation_key = self._get_transactions()
        for transaction in transactions:
            yield transaction
        while last_mutation_key:
            params = {'lastMutationKey': last_mutation_key}
            transactions, last_mutation_key = self._get_transactions(params=params)
            for transaction in transactions:
                yield transaction

    def get_current_transactions(self):
        return self.get_latest_transactions()
