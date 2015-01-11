#!/usr/bin/env python3

import json
import mimetypes
import os.path

import requests
from bs4 import BeautifulSoup as bs4


class TistoryError(Exception):

    """Base Exception thrown if there is a problem interacting with the
    Tistory API.

    Attributes:
        `message` returns the original error message returned by the API.
        `type`, i.e. 'access_token' is derived from trying to figure out
        what kind of error the one returned from the Tistory API is.
        `status_code` is the status code returned by the API.

    """

    def __init__(self, error_message, status_code):
        self.message = error_message
        self.type = self._error_handler(self.message)
        self.status_code = status_code

    def _error_handler(self, error_message):
        """ Attempts to figure out what kind of error the Tistory API threw
        by checking the error message against known errors.

        If the error message is not known, "unknown" will be returned instead.

        """

        errors = {'access_token 이 유효하지 않습니다.': 'access_token',
                  '블로그 정보가 없습니다.': 'does_not_exist',
                  '글이 존재하지 않 거나 권한이 없습니다.': 'does_not_exist_or_unauthorized',
                  '글이 존재하지 않거나, 범위가 유효하지 않습니다.': 'does_not_exist',
                  '필수 Parameter 또는 Request method 가 올바르지 않습니다.': 'incorrect_parameter_or_request_method',
                  '이미지만 업로드가 가능합니다.': 'not_a_image',
                  }

        for error in errors:
            if error in error_message:
                return errors[error]
        return 'unknown'

    def __str__(self):
        return 'Tistory API returned status code: {0}. Error message: \'{1}\' Error type: \'{2}\''.format(
            self.status_code, self.message, self.type)


class TistoryResponse(object):

    """Response from a Tistory request. Behaves like a dict or BeautifulSoup4
    object depending on whether JSON or XML was requested from the API.

    The TistoryResponse has the following interesting attributes:
        `request` gives you access to the requests object used for accessing
        the Tistory API.

        `headers` returns the HTTP headers returned from the Tistory API.

        `format` returns the name of the format the content was requested in.

        `uriparts` returns a tuple containing the endpoint the request was
        sent to, i.e. ('post', 'read').

    The attribute status_code returns the status code returned from the
    Tistory API and the raise_for_status() method throws an TistoryError exception
    if the status code is not 200.

    """

    request = None
    headers = None
    format = None
    uriparts = None

    @property
    def status_code(self):
        """Return the status code returned from the API as an integer."""

        if self.format == 'xml':
            status_code = self.status.text
        elif self.format == 'json':
            status_code = self['status']

        status_code = int(status_code)
        return status_code

    def raise_for_status(self):
        """
        Throws an TistoryError exception if the status code returned from the
        API is not 200.

        See the docstring in TistoryError for more details on the attributes.
        """

        if self.status_code != 200:
            if self.format == 'xml':
                error_message = self.error_message.text
            elif self.format == 'json':
                error_message = self['error_message']
            raise TistoryError(error_message, self.status_code)


class TistoryResponseSoup(bs4, TistoryResponse):
    pass


class TistoryResponseDict(dict, TistoryResponse):

    def __init__(self, text):
        data = json.loads(text)['tistory']
        super().__init__(data)


def _wrap_tistory_request(request, format):
    """Wrap the response from the Tistory API in either a dictionary or a
    BeautifulSoup4 object depending on the format.

    Returned along with the dict/bs4-object is the TistoryRequest object,
    HTTP headers, the format requested and the URI parts used when generating
    the URL.

    """

    if format == 'xml':
        response = TistoryResponseSoup(request.content, features="xml")
    elif format == 'json':
        response = TistoryResponseDict(request.text)

    response.request = request
    response.uriparts = request.uriparts
    response.format = format
    response.headers = request.headers

    return response


class TistoryClassCall(object):

    """A helper class intended for being used as a mapper to the Tistory
    RESTful API."""

    def __init__(
            self,
            callable_cls,
            access_token,
            uriparts=None,
            format='xml',
            file=False):
        self.callable_cls = callable_cls
        self.access_token = access_token
        if not uriparts:
            self.uriparts = ()
        else:
            self.uriparts = uriparts
        self.format = format
        self.file = False

    def __getattr__(self, k):
        # Return a initialized instance of the callable_class, with the
        # appended uripart, k
        return self.callable_cls(callable_cls=self.callable_cls,
                                 access_token=self.access_token,
                                 uriparts=self.uriparts + (k,),
                                 format=self.format,
                                 file=self.file)

    def __call__(self, file=None, **kwargs):
        # Create a params dictionary that TistoryRequest._get() will later
        # build on.
        params = {}
        for kw in kwargs:
            params[kw] = str(kwargs[kw])

        req = TistoryRequest(access_token=self.access_token,
                             uriparts=self.uriparts,
                             params=params,
                             format=self.format,
                             file=file)
        response_wrapper = _wrap_tistory_request(req, self.format)
        return response_wrapper


class TistoryRequest(object):
    API_BASEURL = 'https://www.tistory.com/apis/'

    request = None
    headers = None

    text = None
    content = None

    """The class responsible for doing the actual request to the Tistory
    API."""

    def __init__(self, access_token, uriparts, params, format, file=None):
        """"""
        self.access_token = access_token
        self.uriparts = uriparts

        # Join the uriparts (i.e. 'post' and 'read') and append the path to
        # the base url.
        self.url = self.API_BASEURL + '/'.join(self.uriparts)
        self.params = params
        self.format = format
        self.file = file

        # Do the request to the API.
        self._post()

    @property
    def payload(self):
        """"""
        payload = self.params
        # Add/overwrite the access token and selected format to/in the payload
        payload['access_token'] = self.access_token
        payload['output'] = self.format.lower()

        return payload

    def _post(self):

        # Do the request to the API
        if self.file:
            abspath = os.path.abspath(self.file)
            filename = os.path.basename(abspath)
            mimetype = mimetypes.guess_type(filename)

            with open(filename, 'rb') as f:
                data = {'uploadedfile': (filename, f, mimetype)}
                self.request = requests.post(self.url,
                                             files=data,
                                             data=self.payload)
        else:
            self.request = requests.post(self.url, data=self.payload)

        self.request.raise_for_status()

        self.headers = self.request.headers
        self.text = self.request.text
        self.content = self.request.content


class Tistory(TistoryClassCall):

    """"""

    def __init__(self, access_token=None, format='xml'):
        """"""

        self.access_token = access_token

        if not access_token:
            raise ValueError('Missing access_token.')

        if format not in ['xml', 'json']:
            raise ValueError(
                'Format needs to be either xml or json. Got: {}'.format(format))

        # uriparts have to be a empty tuple, TistoryClassCall will
        # append uri parts to it later as it is invoked, and then use it
        # to create the URL to the API.
        uriparts = ()

        TistoryClassCall.__init__(self,
                                  callable_cls=TistoryClassCall,
                                  access_token=self.access_token,
                                  format=format,
                                  uriparts=uriparts,
                                  file=False)

if __name__ == "__main__":
    pass
