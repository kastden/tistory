#!/usr/bin/env python3

import json
import os
import re
from pprint import pprint

import requests

class TistoryOAuth2(object):

    ''' A class for authenticating against the Tistory OAuth2 endpont on behalf of
    both the user and the application. This is a two-step process.
    First, the script authorizes the application on behalf of the user, and a
    callback URL with a authorization code is returned.
    The authorization code is then used to generate an access token for the
    user that will later be used for accessing the Tistory API.

    Tistory OAuth documentation:
    http://www.tistory.com/guide/api/oauth
    '''

    baseurl = 'https://www.tistory.com/oauth/'

    def __init__(self, config):

        if config:
            self.config = config

        # TODO: Check if the following keys actually exist in the configuration
        # file.
        self.client_id = self.config['client']['client_id']
        self.client_secret = self.config['client']['client_secret']
        self.callback = self.config['client']['callback']

        # We need a valid TSESSION cookie when we do the authorization step.
        self.cookies = self.config['cookies']

        # The property self.access_token reads from self._access_token
        self._access_token = None

    @property
    def access_token(self):
        ''' Returns the generated access_token, or if not yet generated, run
        the method that communicates with the API and generates one.
        '''

        if not self._access_token:
            self.start()
        return self._access_token

    def start(self, verbose=False):
        ''' Start the two-step process of authorizing the app on behalf of the
        user and generating an access token. '''

        # The authorization step returns an code in the callback that
        # is used for generating an access token in the next step.
        code = self._authorize()

        # Deliver the code from the authorization process and return the access
        # token
        self._access_token = self._get_access_token(code)

        if verbose:
            print('The generated access token is: {}'.format(self._access_token))

        return self._access_token

    def _authorize(self):
        ''' Authorize the app on the behalf of the user and return the code
        needed to generate an access token in the next step.'''

        # URL: https://www.tistory.com/oauth/authorize
        url = '{}authorize'.format(self.baseurl)
        params = {'client_id': self.client_id,
                  'redirect_uri': self.callback,
                  'response_type': 'code'}

        text = self._get_text(url, params, cookies=True)

        # Find the code in the returned HTML by searching for the callback
        # URL and code with a regex.
        code_match = r'{host}\?code=(.*)\''.format(
            host=re.escape(self.callback))
        code = re.search(code_match, text)
        code = code.groups(1)[0]

        return code

    def _get_access_token(self, code):
        ''' Do a new request, and this time deliver the code from the
        authorization step.
        If everything is OK, this will finally return the access token '''

        # URL: https://www.tistory.com/oauth/access_token
        url = '{}access_token'.format(self.baseurl)
        params = {'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'redirect_uri': self.callback,
                  'code': code,
                  'grant_type': 'authorization_code'}

        text = self._get_text(url, params)

        # Split the returned string and return the access token.
        access_token = text.split('access_token=')[-1]
        access_token = access_token.lstrip().rstrip()

        return access_token

    def _get_text(self, url, params, cookies=False):
        # Cookies is only needed for the first request.
        # There is no need to send it the second time, even if it probably
        # doesn't make a difference.
        if cookies:
            cookies = self.cookies

        r = requests.get(url, cookies=cookies, params=params)
        r.raise_for_status()
        return r.text

    def write(self, fname='tistory_access_token.json'):
        ''' Write the generated access_token to a JSON file.
        If no fname is specified, write the access_token to a file named
        tistory_access_token.json in the current working directory.'''

        access_token_dict = {'access_token': self._access_token}
        access_token_json = json.dumps(access_token_dict)

        with open(fname, 'w') as file:
            file.write(access_token_json)

if __name__ == "__main__":
    pass