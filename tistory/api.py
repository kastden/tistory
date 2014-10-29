#!/usr/bin/env python3

import os
import json

import requests
from bs4 import BeautifulSoup as bs4

# TODO:

# - Add support for uploading via the post/attach endpoint
# http://www.tistory.com/guide/api/post.php#post-attach
# -- At the moment, post/attach seems rather broken, or is too difficult for me
# to implement support for.


class TistoryError(Exception):
    pass


class TistoryHTTPException(TistoryError):
    pass


class TistoryAPI(object):
    protocol = 'https://'
    host = 'www.tistory.com'
    path = '/apis/'
    api_url = protocol + host + path


class TistoryResponse(object):

    @property
    def status_code(self):
        '''
        Return the status code returned from the API as an integer.
        '''

        if self.format == 'xml':
            status_code = self.status.text
        elif self.format == 'json':
            status_code = self['status']

        status_code = int(status_code)
        return status_code

    def raise_for_status(self):
        ''' 
        Raises an TistoryError exception if the status code returned from the 
        API is not 200. 
        The exception will return the original error message, along with a 
        error type if the error message is known. Otherwise the error type 
        "unknown" is returned.
        '''

        if self.status_code != 200:
            if self.format == 'xml':
                error_message = self.error_message.text
                error = self._error_handler(error_message)
            elif self.format == 'json':
                error_message = self['error_message']
                error = self._error_handler(error_message)
            raise TistoryError(repr(error))

    def _error_handler(self, text):
        '''
        Parses the error message and checks if the error message is a known 
        one. Otherwise it returns "unknown"
        '''

        error = {}
        error['text'] = text
        if 'access_token 이 유효하지 않습니다.' in text:
            error['type'] = 'access_token'
        elif '블로그 정보가 없습니다.' in text:
            error['type'] = 'non_existing'
        elif '글이 존재하지 않 거나 권한이 없습니다.' in text:
            error['type'] = 'does_not_exist_or_unauthorized'
        elif '블로그 정보가 없습니다.' in text:
            error['type'] = 'does_not_exist'
        elif '글이 존재하지 않거나, 범위가 유효하지 않습니다.' in text:
            error['type'] = 'does_not_exist'
        else:
            error['type'] = 'unknown'
        return error


class TistoryResponseSoup(bs4, TistoryResponse):
    pass


class TistoryResponseDict(dict, TistoryResponse):
    pass


def wrap_tistory_request(request, format):
    if format == 'xml':
        response = TistoryResponseSoup(request.bytes, features="xml")
    elif format == 'json':
        data = json.loads(request.text)['tistory']
        response = TistoryResponseDict(data)

    response.format = format
    response.request = request
    response.headers = request.headers

    return response


class TistoryClassCall(TistoryAPI):

    ''' A helper class intended for being used as a mapper to the Tistory
    RESTful API. '''

    def __init__(
            self,
            callable_cls,
            access_token,
            uriparts=None,
            format='xml'):
        self.callable_cls = callable_cls
        self.access_token = access_token
        if not uriparts:
            self.uriparts = ()
        else:
            self.uriparts = uriparts
        self.format = format

    def __getattr__(self, k):
        # Return a initialized instance of the callable_class, with the
        # appended uripart, k
        return self.callable_cls(callable_cls=self.callable_cls,
                                 access_token=self.access_token,
                                 uriparts=self.uriparts + (k,),
                                 format=self.format)

    def __call__(self, **kwargs):
        # Create a params dictionary that TistoryRequest._get() will later
        # build on.
        params = {}
        for kw in kwargs:
            params[kw] = str(kwargs[kw])

        # Join the uriparts (i.e. 'post' + 'read') and create the URL.
        url = self.api_url + '/'.join(self.uriparts)

        req = TistoryRequest(access_token=self.access_token,
                             url=url,
                             params=params,
                             format=self.format)
        response_wrapper = wrap_tistory_request(req, self.format)
        return response_wrapper


class TistoryRequest(TistoryAPI):

    ''' The class responsible for doing the actual request to the Tistory API.
    '''

    def __init__(self, access_token, url, params, format):
        self.access_token = access_token
        self.url = url
        self.params = params
        self.format = format

        # Store the request and headers. The headers returned from
        # requests.response.headers will be a dict.
        self.req = None
        self.headers = None

        # self.text is the string content from requests.response.text
        # and self.bytes is the bytes content from
        # requests.response.content
        self.text = None
        self.bytes = None

        # Do the request to the API.
        self._get()

    @property
    def payload(self):
        payload = self.params
        # Add/overwrite the access token and selected format to/in the payload
        payload['access_token'] = self.access_token
        payload['output'] = self.format.lower()

        return payload

    def _get(self):

        # Do the request to the API
        self.req = requests.post(self.url, data=self.payload)
        # Store the headers, as they will be saved in the response wrapper
        self.headers = self.req.headers

        self.req.raise_for_status()

        # Save the text and bytes content as the response wrapper will read
        # from them
        self.text = self.req.text
        self.bytes = self.req.content


class Tistory(TistoryClassCall):

    def __init__(self, access_token=None, format='xml'):
        self.access_token = access_token

        if not access_token:
            raise ValueError('Missing access_token.')

        if format not in ['xml', 'json']:
            raise ValueError(
                'Format needs to be either xml or json. Got: {}'.format(format))

        # uriparts have to be a empty tuple, TistoryClassCall will
        # appends uri parts to it later as it is invoked, and then use it
        # to create the URL to the API.
        uriparts = ()

        TistoryClassCall.__init__(self,
                                  callable_cls=TistoryClassCall,
                                  access_token=self.access_token,
                                  format=format,
                                  uriparts=uriparts)

if __name__ == "__main__":
    pass
