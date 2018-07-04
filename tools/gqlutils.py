import re
import json
import requests


class GqlClient:
    """
    Simple client for interaction with GraphQL API.
    It can be used together with unittest.TestCase and locust.TaskSet classes
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
        _data = dict()
        if kwargs.get('username'):
            _data.update({'username': kwargs['username']})
        if kwargs.get('password'):
            _data.update({'password': kwargs['password']})
        response = self.client.post(url, data=_data)
        self.cookie = '_yum_l={}'.format(response.cookies.get('_yum_l'))
        self.headers.update({'Cookie': self.cookie})
        return response

    def logout(self, url):
        """Log out from system

        :param url: logout url

        :return: response
        """
        return self.client.get(url, headers=self.headers)

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
        return self.client.post(
            url,
            headers=self.headers,
            data=json.dumps({
                'query': query,
                'variables': variables,
                'operationName': re.match('[a-z]+ ([a-zA-Z_]+)[ (]',
                                          query).group(1)
            })
        )
