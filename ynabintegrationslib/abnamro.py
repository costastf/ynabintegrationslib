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
from base64 import b64decode

from selenium.common.exceptions import TimeoutException
from urllib3.util import parse_url

from .authenticator import AccountAthenticator

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


PAGE_TRANSITION_WAIT = 120
AUTHENTICATION_URL = 'https://www.abnamro.nl/portalserver/my-abnamro/my-overview/overview/index.html'


class AmroAccountAthenticator(AccountAthenticator):

    def get_authenticated_session(self):
        self._logger.info('Loading login page')
        self._driver.get(AUTHENTICATION_URL)
        self._logger.info('Accepting cookies')
        try:
            self._click_on("//*[text()='Save cookie-level']")
        except TimeoutException:
            self._logger.warning("Cookies window didn't pop up")
        self._logger.info('Logging in')
        element = self._driver.find_element_by_xpath("//*[(@label='Identification code')]")
        element.click()
        self._driver.find_element_by_name('accountNumber').send_keys(self.account_number)
        self._driver.find_element_by_name('cardNumber').send_keys(self.card_number)
        self._driver.find_element_by_name('inputElement').send_keys(self.pin_number)
        self._driver.find_element_by_id('login-submit').click()
        return self._get_session()


class Transaction:
    """Models a banking transaction"""

    def __init__(self, data):
        _ = data


class AbnAmro:
    """Models the service"""

    def __init__(self, account_number, card_number, pin_number, url='https://www.abnamro.nl'):
        self.account_number = account_number
        self.card_number = card_number
        self._base_url = url
        self._host = parse_url(url).host
        self._session = self._get_authenticated_session(account_number,
                                                        card_number,
                                                        pin_number)

    def _get_authenticated_session(self, account_number, card_number, pin_number):
        authenticator = AmroAccountAthenticator(account_number, card_number, pin_number, AUTHENTICATION_URL)
        session = authenticator.get_authenticated_session()
        authenticator.quit()
        session.headers.update({'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0)'
                                               'Gecko/20100101 Firefox/67.0')})
        return session

    def get_latest_transactions(self):
        return self._get_transactions(date_from=None,
                                      date_to=None,
                                      from_last_download_date=True)

    def get_transactions(self, date_from, date_to):
        return self._get_transactions(date_from, date_to)

    def _get_transactions(self, date_from, date_to, from_last_download_date=False):
        url = f'{self._base_url}/mutationreporting/generations/v1'
        headers = {'Content-Type': 'application/json;charset=utf-8',
                   'DNT': '1',
                   'Host': self._host,
                   'Referer': f'{self._base_url}/'
                              f'portalserver/mijn-abnamro/'
                              f'zelf-regelen/download-transacties/index.html',
                   'TE': 'Trailers'}
        if from_last_download_date:
            date_from, date_to = None, None
        payload = {'generations': {'accountNumbers': [self.account_number],
                                   'format': 'TXT',
                                   'fromLastDownloadDate': from_last_download_date,
                                   'fromDate': date_from,  # format 20-05-2019
                                   'toDate': date_to}}
        response = self._session.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return self._parse_transactions(response.json())

    def _parse_transactions(self, payload):
        encoded_text = payload.get('reports', [{}])[0].get('fileBytes', None)
        if encoded_text is None:
            raise ValueError(f'No "fileBytes" base64 encoded text'
                             f'found in payload: {payload}')
        decoded_text = b64decode(encoded_text)
        return [Transaction(data) for data in decoded_text.splitlines()]
