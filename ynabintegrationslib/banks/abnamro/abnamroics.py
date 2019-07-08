#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: abnamroics.py
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
Main code for abnamroics

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging
from datetime import date
from datetime import datetime

from requests import Session
from urllib3.util import parse_url

from ynabintegrationslib.lib.core import YnabTransaction

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
LOGGER_BASENAME = '''abnamroics'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class AuthenticationFailed(Exception):
    """The token provided is invalid or the authentication failed for some other reason."""


class Account:
    """Models a credit card account"""

    def __init__(self, data):
        self._data = data

    @property
    def number(self):
        return self._data.get('accountNumber')

    @property
    def product_id(self):
        return self._data.get('productId')

    @property
    def credit_limit(self):
        return self._data.get('creditLimit')

    @property
    def current_balance(self):
        return self._data.get('currentBalance')

    @property
    def available_credit(self):
        return self._data.get('creditLeftToUse')

    @property
    def authorized_balance(self):
        return self._data.get('authorizedBalance')

    @property
    def in_arrears(self):
        return self._data.get('inArrears')

    @property
    def arrears_status(self):
        return self._data.get('arrearsStatus')

    @property
    def in_overlimit(self):
        return self._data.get('inOverLimit')

    @property
    def loyalty_points(self):
        return self._data.get('loyaltyPoints')

    @property
    def loyalty_amount(self):
        return self._data.get('loyaltyAmount')

    @property
    def is_valid(self):
        return self._data.get('valid')

    @property
    def next_payment_date(self):
        return self._data.get('paymentDate')

    @property
    def last_available_payment_date(self):
        return self._data.get('lastDayOfStatementToBePaid')

    @property
    def amount_due(self):
        return self._data.get('amountDue')

    @property
    def due_date(self):
        return self._data.get('dueDate')

    @property
    def iban(self):
        return self._data.get('iban')

    @property
    def balance_curried_forward(self):
        return self._data.get('balanceCarriedForward')

    @property
    def payment_condition(self):
        return self._data.get('paymentCondition')

    @property
    def remaining_amount_due(self):
        return self._data.get('remainingAmountDue')

    @property
    def credit_agreement(self):
        return self._data.get('creditAgreement')

    @property
    def payment_state(self):
        return self._data.get('paymentState')

    @property
    def charge_percentage(self):
        return self._data.get('chargePercentage')

    @property
    def fixed_amount(self):
        return self._data.get('fixedAmount')

    @property
    def prepaid(self):
        return self._data.get('prepaid')

    @property
    def continuous_credit(self):
        return self._data.get('continuousCredit')

    @property
    def migrated(self):
        return self._data.get('migrated')

    @property
    def credit_agreement_conditional(self):
        return self._data.get('creditagreementConditional')

    @property
    def main_card_holder(self):
        return self._data.get('mainCardHolder')

    @property
    def main_card_holder(self):
        return self._data.get('mainCardHolder')

    @property
    def app_enrolled(self):
        return self._data.get('appEnrolled')

    @property
    def over_limit(self):
        return self._data.get('overLimit')


class Period:
    """Models the payment period"""

    def __init__(self, credit_card, data):
        self._credit_card = credit_card
        self._data = data
        self._transactions = None

    @property
    def period(self):
        return self._data.get('period')

    @property
    def start_date(self):
        return self._data.get('startDatePeriod')

    @property
    def end_date(self):
        return self._data.get('endDatePeriod')

    @property
    def current_period(self):
        return self._data.get('currentPeriod')

    @property
    def show_statement(self):
        return self._data.get('showStatement')

    @property
    def balance_brought_forward(self):
        return self._data.get('balanceBroughtForward')

    @property
    def balance_carried_forward(self):
        return self._data.get('balanceCarriedForward')

    @property
    def transactions(self):
        if self._transactions is None:
            url = f'{self._credit_card._base_url}/sec/nl/sec/transactions'
            params = {'accountNumber': self._credit_card.account_number,
                      'flushCache': True,
                      'fromPeriod': self.period,
                      'untilPeriod': self.period}
            response = self._credit_card._session.get(url, params=params)
            response.raise_for_status()
            self._transactions = [AbnAmroCreditCardTransaction(data)
                                  for data in response.json()]
        return self._transactions


class AbnAmroCreditCardTransaction(YnabTransaction):
    """Models a credit card transaction"""

    @property
    def country_code(self):
        return self._data.get('countryCode')

    @property
    def card_last_four_digits(self):
        return self._data.get('lastFourDigits')

    @property
    def transaction_date(self):
        return self._data.get('transactionDate')

    @property
    def description(self):
        return self._data.get('description')

    @property
    def billing_amount(self):
        return self._data.get('billingAmount')

    @property
    def billing_currency(self):
        return self._data.get('billingCurrency')

    @property
    def source_amount(self):
        return self._data.get('sourceAmount')

    @property
    def source_currency(self):
        return self._data.get('sourceCurrency')

    @property
    def merchant_category_description(self):
        return self._data.get('merchantCategoryCodeDescription')

    @property
    def type_of_transaction(self):
        return self._data.get('typeOfTransaction')

    @property
    def batch_number(self):
        return self._data.get('batchNr')

    @property
    def batch_sequence_number(self):
        return self._data.get('batchSequenceNr')

    @property
    def type_of_purchase(self):
        return self._data.get('typeOfPurchase')

    @property
    def processing_time(self):
        return self._data.get('processingTime')

    @property
    def indicator_extra_card(self):
        return self._data.get('indicatorExtraCard')

    @property
    def embossing_name(self):
        return self._data.get('embossingName')

    @property
    def direct_debit_state(self):
        return self._data.get('directDebitState')

    @property
    def is_mobile(self):
        return self._data.get('mobile')

    @property
    def loyalty_points(self):
        return self._data.get('loyaltyPoints')

    @property
    def charge_back_allowed(self):
        return self._data.get('chargeBackAllowed')

    @property
    def amount(self):
        return int(self.billing_amount * 100)

    @property
    def payee_name(self):
        return self.description

    @property
    def memo(self):
        return (f'Description: {self.description}\n'
                f'Buyer: {self.embossing_name}\n'
                f'Merchant Category: {self.merchant_category_description}\n'
                f'Amount: {self.billing_amount} {self.billing_currency}')

    @property
    def date(self):
        return self.transaction_date


class AbnAmroCreditCard:
    """Models a credit card account"""

    def __init__(self, username, password, url='https://www.icscards.nl'):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self._username = username
        self._password = password
        self._base_url = url
        self._host = parse_url(url).host
        self._session = self._get_authenticated_session()
        self._account_number = None
        self._periods = None
        self._account = None
        self._current_transactions = None

    def _get_authenticated_session(self):
        session = Session()
        headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0)'
                                  'Gecko/20100101 Firefox/67.0')}
        session.headers.update(headers)
        session.headers.update({'X-XSRF-TOKEN': self._get_xsrf_token(session,
                                                                     self._username,
                                                                     self._password)})
        self.original_get = session.get  # pylint: disable=attribute-defined-outside-init
        session.get = self._patched_get
        return session

    def _patched_get(self, *args, **kwargs):
        url = args[0]
        self._logger.debug('Using patched get request for url %s', url)
        response = self.original_get(*args, **kwargs)
        if not url.startswith(self._base_url):
            self._logger.debug('Url "%s" requested is not from credit card api, passing through', url)
            return response
        if 'USERNAME=unauthenticated' in response.url:
            self._logger.info('Expired session detected, trying to re authenticate!')
            self._session = self._get_authenticated_session()
            response = self.original_get(*args, **kwargs)
        return response

    def _get_xsrf_token(self, session, username, password):
        login_url = f'{self._base_url}/pub/nl/pub/login'
        self._logger.debug('Trying to authenticate to url "%s"', login_url)
        payload = {'loginType': 'PASSWORD',
                   'virtualPortal': 'ICS-ABNAMRO',
                   'username': username,
                   'password': password}
        response = session.post(login_url, json=payload)
        if not response.ok:
            raise AuthenticationFailed(response.text)
        return session.cookies.get('XSRF-TOKEN')

    @property
    def account_number(self):
        if not self._account_number:
            url = f'{self._base_url}/sec/nl/sec/allaccountsv2'
            self._logger.debug('Trying to get all accounts from url "%s"', url)
            response = self._session.get(url)
            response.raise_for_status()
            self._account_number = response.json()[0].get('accountNumber')
        return self._account_number

    @property
    def current_period_transactions(self):
        if self._current_transactions is None:
            current_month = date.today().strftime('%Y-%m')
            url = f'{self._base_url}/sec/nl/sec/transactions'
            params = {'accountNumber': self.account_number,
                      'flushCache': True,
                      'fromPeriod': current_month,
                      'untilPeriod': current_month}
            response = self._session.get(url, params=params)
            response.raise_for_status()
            self._current_transactions = [AbnAmroCreditCardTransaction(data)
                                          for data in response.json()]
        return self._current_transactions

    def reset(self):
        self._current_transactions = None

    @property
    def periods(self):
        if self._periods is None:
            url = f'{self._base_url}/sec/nl/sec/periods'
            params = {'accountNumber': self.account_number}
            response = self._session.get(url, params=params)
            response.raise_for_status()
            self._periods = [Period(self, data)
                             for data in response.json()]
        return self._periods

    @property
    def account(self):
        if self._account is None:
            url = f'{self._base_url}/sec/nl/sec/accountv5'
            params = {'accountNumber': self.account_number}
            response = self._session.get(url, params=params)
            response.raise_for_status()
            self._account = [Account(response.json())]
        return self._account

    def get_period(self, year, month):
        return next((period for period in self.periods
                     if period.period == f'{year}-{month.zfill(2)}'), None)

    def get_transactions_for_period(self, year, month):
        period_ = self.get_period(year, month)
        if not period_:
            return []
        return period_.transactions
