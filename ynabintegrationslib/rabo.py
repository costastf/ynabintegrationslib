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

from requests import Session
from base64 import b64decode
from datetime import datetime
import csv

from .core import YnabTransaction


class RaboTransaction(YnabTransaction):
    """Models a Rabobank transaction"""

    @property
    def payee_name(self):
        return self._data.get('Naam tegenpartij')

    @property
    def memo(self):
        return self._data.get('Omschrijving-1')

    @property
    def date(self):
        date = datetime.strptime(self._data.get('Datum', '1999-01-01'), '%Y-%M-%d')
        return date.strftime('%Y-%d-%M')

    @property
    def amount(self):
        amount = self._data.get('Bedrag')
        return int(amount.translate({ord(char): '' for char in ',.'}))

    @property
    def iban(self):
        return self._data.get('IBAN/BBAN')

    @property
    def currency(self):
        return self._data.get('Munt')

    @property
    def bic_code(self):
        return self._data.get('BIC')

    @property
    def sequence_number(self):
        return self._data.get('Volgnr')

    @property
    def balance(self):
        balance = self._data.get('Saldo na trn')
        return int(balance.translate({ord(char): '' for char in ',.'}))

    @property
    def counter_party_account(self):
        return self._data.get('Tegenrekening IBAN/BBAN')

    @property
    def counter_party_name(self):
        return self._data.get('Naam tegenpartij')

    @property
    def final_party_name(self):
        return self._data.get('Naam uiteindelijke partij')

    @property
    def initiating_party(self):
        return self._data.get('Naam initiërende partij')

    @property
    def counter_party_bic(self):
        return self._data.get('BIC tegenpartij')

    @property
    def code(self):
        return self._data.get('Code')

    @property
    def batch_id(self):
        return self._data.get('Batch ID')

    @property
    def transaction_reference(self):
        return self._data.get('Transactiereferentie')

    @property
    def authorization_reference(self):
        return self._data.get('Machtigingskenmerk')

    @property
    def authorization_reference(self):
        return self._data.get('Machtigingskenmerk')

    @property
    def creditor_id(self):
        return self._data.get('Incassant ID')

    @property
    def payment_reference(self):
        return self._data.get('Betalingskenmerk')

    @property
    def memo_2(self):
        return self._data.get('Omschrijving-2')

    @property
    def memo_3(self):
        return self._data.get('Omschrijving-3')

    @property
    def return_reason(self):
        return self._data.get('Reden retour')

    @property
    def original_amount(self):
        return self._data.get('Oorspr bedrag')

    def original_currency(self):
        return self._data.get('Oorspr munt')

    def koers(self):
        return self._data.get('Koers')


class Service:

    def __init__(self, username=None, password=None, csv_file=None):
        self._session = self._authenticate(username, password) if username or password else None
        self._transactions = csv_file

    def _authenticate(self, username, password):
        # session = Session()
        # TODO implement authenticating
        # return None
        pass

    def _retrieve_transactions_from_api(self):
        # TODO implement retrieving csv from api
        # csv_file = b64decode(self._retrieve_transactions_csv())
        return self._transactions

    def _retrieve_transactions_from_file(self):
        with open(self._transactions, newline='', encoding='iso-8859-1') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
            transactions = [line for line in reader]
        return[RaboTransaction(data) for data in transactions]

    def get_transactions(self):
        contents = csv.reader(self._transactions, delimiter=',', quotechar='"')
        transactions = [line for line in contents]
        transactions.pop(0)  # getting rid of header line in index 0
        return [RaboTransaction(data) for data in transactions]

