# Tistory

A Python 3 library for interacting with the Tistory RESTful API.  

[Tistory API documentation](http://www.tistory.com/guide/api/index)
[Manage applications](http://www.tistory.com/guide/api/manage/list)

### Dependencies

[Requests](http://docs.python-requests.org/en/latest/), [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/) and [lxml](http://lxml.de/).

	pip install -r requirements.txt

### Obtaining an access_token
There is a TistoryOAuth2 helper included for authorizing a app on behalf of the user and then requesting an access_token.

```python  
from tistory import TistoryOAuth2
config = {
    "client": {
        "client_id": "something_something_client_id",
        "client_secret": "client_something_secret",
        "callback": "http://mycallback:42777"
    },
    "cookies": {
        "TSSESSION": "valid_tsession_cookie"
    }}
auth = TistoryOAuth2(config)
auth.start(verbose=True)
auth.write('access_token.json')
```

### Example API usage
```python  
from pprint import pprint

from tistory import Tistory

access_token = 'abc123def'
my_username = 'my_tistory_username'
t = Tistory(access_token=access_token, format='xml')

# List the posts on a blog:
posts = t.post.list(targetUrl='toodur2', page=1, count=30)
pprint(posts)

# Get a post on a blog and print the HTML content:
post = t.post.read(targetUrl='iu0602', postId=273)
html = post.item.content.string
print(html)

# Upload a image:
upload = t.post.attach(targetUrl=my_username, file='image.jpg')
image_url = upload.url.string
print(image_url)
```

### Notes
The Tistory API returns a mix of escaped and unescaped HTML on the /read/post/ endpont if format is set to JSON.
To get correct output, use XML instead.

If format is set to JSON, the /post/list endpoint only returns a list if there is more than one entry found, otherwise it will just return the entry dictionary for that one post.

For a Node.js alternative, check out [Em-Man/node-tistoryAPI](https://github.com/Em-Man/node-tistoryAPI)