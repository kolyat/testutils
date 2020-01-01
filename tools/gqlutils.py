# Copyright (c) 2017-2020 Kirill 'Kolyat' Kiselnikov
# This file is the part of testutils, released under modified MIT license
# See the file LICENSE included in this distribution

import logging
import json
import requests


class GqlClient:
    """
    Simple client for interaction with GraphQL API.
    It can be used as mixin with unittest.TestCase and locust.TaskSet classes
    """
    client = requests.Session()
    cookie = None
    headers = {'content-type': 'application/json'}

    def login(self, url, **kwargs):
        """Log into system

        :param url: login url
        :param kwargs:
            -- username
            -- password

        :return: response
        """
        logging.info('Log in to {}'.format(url))
        logging.info('User: {}'.format(kwargs.get('username')))
        _data = dict()
        if kwargs.get('username'):
            _data.update({'username': kwargs['username']})
        if kwargs.get('password'):
            _data.update({'password': kwargs['password']})
        response = self.client.post(url, data=_data)
        logging.info('{}: {}'.format(response.status_code, response.text))
        self.cookie = '_yum_l={}'.format(response.cookies.get('_yum_l'))
        logging.info('Got cookie: {}'.format(self.cookie))
        self.headers.update({'Cookie': self.cookie})
        return response

    def logout(self, url):
        """Log out from system

        :param url: logout url

        :return: response
        """
        logging.info('Log out from {}'.format(url))
        response = self.client.get(url, headers=self.headers)
        logging.info('{}: {}'.format(response.status_code, response.text))
        return response

    def cleanup(self):
        """Close session and delete cookie info
        """
        self.client.close()
        self.cookie = None
        try:
            self.headers.pop('Cookie')
        except KeyError:
            pass

    def query(self, url, query, variables):
        """Execute GraphQL query

        :param url: url to GraphQL interface
        :param query: query str
        :param variables: dict with additional query variables

        :return: response
        """
        logging.info('GraphQL query to {}'.format(url))
        logging.info(query)
        logging.info('Variables: {}'.format(variables))
        response = self.client.post(
            url,
            headers=self.headers,
            data=json.dumps({'query': query, 'variables': variables})
        )
        logging.info('{}: {}'.format(response.status_code, response.text))
        return response
