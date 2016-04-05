# IAConnector

IAConnector is the Python implementation of an OAuth and API consumer for the Inter-_Actief_ web site.

The goal of IAConnector is to provide an easy-to-use interface to the official Inter-_Actief_ API. Part of this is the
included OAuth functionality. This allows applications to act on behalf of a user. Committees can use this functionality
to streamline activity signup processes, get user details or verify Inter-_Actief_ memberships.

IAConnector can be used in Django (or other Python) projects by committees of Study Association Inter-_Actief_.

## Documentation

### Installation

#### Requirements

IAConnector only supports **Python 3.2** and higher.

IAConnector requires the following external libraries, which are installed automatically when using the `setup.py` script:

- requests (2.9 or higher)
- requests-oauthlib (0.6 or higher)

#### From PyPI

Our goal is to make this library available on PyPI, however, this has not yet happened.

### Using IAConnector

IAConnector features a base class from which all functionality can be accessed. Below you will find a short example
of how to use IAConnector. The source code has been documented extensively, you can find more information there.

#### OAuth

```python
from iaconnector import IAConnector

ia = IAConnector()
ia.init_oauth(
    client_id='your-id',
    client_secret='your-secret',
    scope=['your-first-scope', 'your-second-scope'],
    redirect_url='http://your-site.net/oauth/return/',
)
redirect_to = ia.oauth.get_authorization_url()

# The user returned! The variable 'request_url' contains the URL the user was redirected to from the IA site

ia.oauth.fetch_access_token(request_url)
access_token = ia.oauth.get_access_token()
```

#### API

```python
from iaconnector import IAConnector
from iaconnector.exceptions import NotLoggedInError

ia = IAConnector()
ia.init_api()

# Check if token is correct, then get user details
if ia.api.check_token(access_token):
    print(ia.api.get_user_details(access_token))
else:
    print("No user details - token is not valid!")

# OR catch an exception
try:
    print(ia.api.get_user_details(access_token))
except NotLoggedInError:
    print("No user details - token is not valid!")
```

#### Combining OAuth and API

If both the OAuth and API parts are initialized, any token obtained using OAuth is automatically propagated to the API client.

```python
from iaconnector import IAConnector

ia = IAConnector()
ia.init_oauth(
    client_id='your-id',
    client_secret='your-secret',
    scope=['your-first-scope', 'your-second-scope'],
    redirect_url='http://your-site.net/oauth/return/',
)
ia.init_api()

redirect_to = ia.oauth.get_authorization_url()

# The user returned! The variable 'request_url' contains the URL the user was redirected to from the IA site

ia.oauth.fetch_access_token(request_url)
access_token = ia.oauth.get_access_token()

# Check if token is correct, then get user details
if ia.api.check_token(access_token):
    print(ia.api.get_user_details(access_token))
else:
    print("No user details - token is not valid!")
```

### API coverage

At the moment only the 'authentication module' and parts of the 'activity module' are implemented.
This should be enough to manage users and subscribe users to your activity.
More endpoints can be added on request, please open an issue to do so.
