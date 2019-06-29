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


class Transaction:

    def __init__(self, data):
        self._data = data

    @property
    def iban(self):
        return self._data.get('IBAN/BBAN')

    @property
    def currency(self):
        return self._data.get('Munt')

    @property
    def date(self):
        date = datetime.strptime(self._data.get('Datum', '1999-01-01'), '%Y-%M-%d')
        return date.strftime('%Y-%d-%M')

    @property
    def amount(self):
        amount = self._data.get('Bedrag')
        return int(amount.translate({ord(char): '' for char in ',.'}))

    @property
    def payee_name(self):
        return self._data.get('Naam tegenpartij')

    @property
    def memo(self):
        return self._data.get('Omschrijving-1')

    def serialize(self):
        return {"date": self.date,
                "amount": self.amount,
                "payee_name": self.payee_name,
                "memo": self.memo}


class Service:

    def __init__(self, username, password):
        self._session = self._authenticate(username, password)
        self._transactions = None

    def _authenticate(self, username, password):
        # session = Session()
        # TODO implement authenticating
        # return None
        pass

    def _retrieve_transactions_csv(self):
        # TODO implement retireving csv from api
        # csv_file = b64decode(self._retrieve_transactions_csv())
        return self._transactions

    def get_transactions(self):
        contents = csv.reader(self._transactions, delimiter=',', quotechar='"')
        transactions = [line for line in contents]
        transactions.pop(0)  # getting rid of header line in index 0
        return [Transaction(data) for data in transactions]

