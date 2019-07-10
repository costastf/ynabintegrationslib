#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: core.py
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
Main code for core

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import abc
import logging

from requests import Session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

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
LOGGER_BASENAME = '''core'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


PAGE_TRANSITION_WAIT = 120


class AccountAuthenticator(abc.ABC):

    def __init__(self):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self._driver = self._initialize_chrome()

    def _initialize_chrome(self):
        self._logger.info('Initializing chrome in headless mode')
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('window-size=1920,1080')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                                  chrome_options=chrome_options)
        driver.implicitly_wait(PAGE_TRANSITION_WAIT)
        return driver

    def _click_on(self, xpath):
        self._logger.info('Waiting for %s', xpath)
        WebDriverWait(self._driver,
                      PAGE_TRANSITION_WAIT).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        self._logger.info('Clicking %s', xpath)
        self._driver.find_element_by_xpath(xpath).click()

    @abc.abstractmethod
    def authenticate(self, *args, **kwargs):
        pass

    def get_authenticated_session(self):
        self._logger.info('Log in successful, getting session cookies.')
        session = Session()
        self._logger.info('Transferring cookies to a requests session.')
        for cookie in self._driver.get_cookies():
            for invalid in ['httpOnly', 'expiry']:
                try:
                    del cookie[invalid]
                except KeyError:
                    pass
            session.cookies.set(**cookie)
        self.quit()
        return session

    def quit(self):
        self._logger.info('Closing chrome')
        self._driver.quit()


class YnabTransaction(abc.ABC):

    def __init__(self, data):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self._data = data

    @abc.abstractmethod
    def amount(self):
        pass

    @abc.abstractmethod
    def payee_name(self):
        pass

    @abc.abstractmethod
    def memo(self):
        pass

    @abc.abstractmethod
    def date(self):
        pass

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, YnabTransaction):
            return hash(frozenset(self._data.items())) == hash(frozenset(other._data.items()))  # pylint: disable=protected-access
        return NotImplemented

    def __ne__(self, other):
        """Override the default Unequal behavior"""
        if isinstance(other, YnabTransaction):
            return hash(frozenset(self._data.items())) != hash(frozenset(other._data.items()))  # pylint: disable=protected-access
        return NotImplemented

    @property
    def to_ynab(self):
        return {'amount': self.amount,
                'payee_name': self.payee_name,
                'memo': self.memo,
                'date': self.date}


class Account(abc.ABC):

    @abc.abstractmethod
    def transactions(self):
        pass

    @abc.abstractmethod
    def get_current_transactions(self):
        pass
