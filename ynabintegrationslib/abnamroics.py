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

from requests import Session
from urllib3.util import parse_url

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


class Account:
    """Models a credit card account"""

    def __init__(self, data):
        self._data = data

    @property
    def number(self):
        return self._data.get('accountNumber')

    @property
    def poduct_id(self):
        return self._data.get('productId')

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
    def last_vailable_payment_date(self):
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

    def __init__(self, data):
        self._data = data

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


class Transaction:
    """Models a credit card transaction"""

    def __init__(self, data):
        self._data = data

    def country_code(self):
        return self._data.get('countryCode')

    def card_last_four_digits(self):
        return self._data.get('lastFourDigits')

    def transaction_date(self):
        return self._data.get('transactionDate')

    def description(self):
        return self._data.get('description')

    def billing_amount(self):
        return self._data.get('billingAmount')

    def billing_currency(self):
        return self._data.get('billingCurrency')

    def source_amount(self):
        return self._data.get('sourceAmount')

    def source_currency(self):
        return self._data.get('sourceCurrency')

    def merchant_category_description(self):
        return self._data.get('merchantCategoryCodeDescription')

    def type_of_transaction(self):
        return self._data.get('typeOfTransaction')

    def batch_number(self):
        return self._data.get('batchNr')

    def batch_sequence_number(self):
        return self._data.get('batchSequenceNr')

    def type_of_purchase(self):
        return self._data.get('typeOfPurchase')

    def processing_time(self):
        return self._data.get('processingTime')

    def indicator_extra_card(self):
        return self._data.get('indicatorExtraCard')

    def embossing_name(self):
        return self._data.get('embossingName')

    def direct_debit_state(self):
        return self._data.get('directDebitState')

    def is_mobile(self):
        return self._data.get('mobile')

    def loyalty_points(self):
        return self._data.get('loyaltyPoints')

    def charge_back_allowed(self):
        return self._data.get('chargeBackAllowed')


class CreditCard:
    """Models a credit card account"""

    def __init__(self, username, password, url='https://www.icscards.nl'):
        self._base_url = url
        self._host = parse_url(url).host
        self._session = self._get_authenticated_session(username, password)
        self._periods = None
        self._current_transactions = None
        self._account_number = None
        self._xsrf_token = None

    def _get_authenticated_session(self, username, password):
        session = Session()
        headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0)'
                                  'Gecko/20100101 Firefox/67.0'),
                   'X-XSRF-TOKEN': self._xsrf_token}
        session.headers.update(headers)
        # TODO implement session authentication
        return session

    def get_current_period_transactions(self):
        if self._current_transactions is None:
            current_month = date.today().strftime('%Y-%m')
            url = f'{self._base_url}/sec/nl/sec/transactions'
            headers = {'Accept': 'application/json, text/plain, */*',
                       'DNT': 1,
                       'Host': self._host,
                       'Referer': f'{self._base_url}/abnamrogb/mijn/overview'}
            params = {'accountNumber': self._account_number,
                      'flushCache': True,
                      'fromPeriod': current_month,
                      'untilPeriod': current_month}
            response = self._session.get(url, params=params, headers=headers)
            response.raise_for_status()
            self._current_transactions = [Transaction(data)
                                          for data in response.json()]
        return self._current_transactions
