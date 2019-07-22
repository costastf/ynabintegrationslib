#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: configuration.py
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
Main code for configuration.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

CONFIGURATION = {'ynab_token': 'TOKEN',
                 'transaction_queue_size': 1000,
                 'upload_frequency': 45,
                 'accounts': [{'bank': 'AbnAmro',
                               'type': 'account',
                               'credentials': {'account_number': 'NUMBER',
                                               'card_number': 'NUMBER',
                                               'pin_number': 'NUMBER'},
                               'budget_name': 'BUDGET_NAME',
                               'account_name': 'ACCOUNT_NAME'},
                              {'bank': 'AbnAmro',
                               'type': 'credit_card',
                               'credentials': {'username': 'USERNAME',
                                               'password': 'PASSWORD'},
                               'budget_name': 'BUDGET_NAME',
                               'account_name': 'ACCOUNT_NAME'}
                              ]}
