# Tistory

A Python 3 library for interacting with the Tistory RESTful API.  

[Tistory API documentation](http://www.tistory.com/guide/api/index)  
[Manage applications](http://www.tistory.com/guide/api/manage/list)

### Dependencies

[Requests](http://docs.python-requests.org/en/latest/), [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/) and [lxml](http://lxml.de/).

	pip install -r requirements.txt

### Obtaining an access_token
There is a TistoryOAuth2 helper included for authorizing a app on behalf of the user and then requesting an access_token.

	>>> from tistory import TistoryOAuth2
    >>> config = {
    >>>     "client": {
    >>>         "client_id": "something_something_client_id",
    >>>         "client_secret": "client_something_secret",
    >>>         "callback": "http://mycallback:42777"
    >>>     },
    >>>     "cookies": {
    >>>         "TSSESSION": "valid_tsession_cookie"
    >>>     }}
    >>> at = TistoryOAuth2(config)
    >>> at.start(verbose=True)
    >>> at.write('access_token.json')

### Example API usage

	>>> from pprint import pprint
	>>> from tistory import Tistory
	>>> access_token = 'abc123def'
	>>> t = Tistory(access_token=access_token, format='xml')
#
	>>> # List the entries on a blog:
	>>> response = t.post.list(targetUrl='toodur2', page=1, count=50)
	>>> pprint(response.soup)
#	
	>>> # Print the HTML content of a post:
	>>> post = t.post.read(targetUrl='iu0602', postId=273)
	>>> print(post.item.content.string)

### Notes
The Tistory API returns a mix of escaped and unescaped HTML on the /read/post/ endpont if format is set to JSON.  
To get correct output, use XML instead.

### Todo
- Support file uploading