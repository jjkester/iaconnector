from requests_oauthlib import OAuth2Session


class OAuthConsumer(object):
    """
    OAuth consumer for the Inter-Actief OAuth endpoint.

    For each session (user) a new instance needs to be created.
    """
    base_url = 'https://www.inter-actief.utwente.nl/o/'
    url_endpoints = {
        'authorization': 'authorize/',
        'token': 'token/',
        'refresh': 'token/',
    }

    def __init__(self, client_id, client_secret, redirect_uri, scope, access_token=None, renew_token=None, base_url=None):
        """
        Creates a new OAuth consumer.

        :param client_id: The registered client id for the application.
        :param client_secret: The registered client secret for the application.
        :param redirect_uri: The URI to which the server redirects. This URI must be registered with the application.
        :param scope: The permission scope to request.
        :param access_token: The current access token, if known.
        :param base_url: The base URL for the OAuth implementation. This is by default the (production) Inter-Actief
        web site (`https://www.inter-actief.utwente.nl/o/`).
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.access_token = access_token
        self.renew_token = renew_token

        if base_url is not None:
            if base_url[-1:] != '/':
                base_url += '/'
            self.base_url = base_url

        self._session = None

    def _get_session(self):
        """
        Returns the OAuth session object and creates a new one if necessary.

        :return: The OAuth session object
        """
        if self._session is None:
            self._session = OAuth2Session(
                client_id=self.client_id,
                scope=self.scope,
                redirect_uri=self.redirect_uri,
            )
        return self._session

    def _get_url(self, endpoint):
        """
        Builds an OAuth URL for the given OAuth endpoint.

        :param endpoint: The name of the OAuth endpoint
        :return: The external URL to the OAuth endpoint
        """
        return ''.join([
            self.base_url,
            self.url_endpoints[endpoint]
        ])

    def get_authorization_url(self):
        """
        Returns the authorization URL to which the user can be redirected to log in at Inter-Actief.

        :return: The authorization URL
        """
        return self._get_session().authorization_url(self._get_url('authorization'))

    def fetch_access_token(self, authorization_response):
        """
        Retrieves an access token for the authorized user.

        Afterwards the access token and renew token can be read using their respective methods.

        :param authorization_response: The full URL to which the Inter-Actief site redirected the user after
        authorizing.
        """
        response = self._get_session().fetch_token(
            token_url=self._get_url('token'),
            authorization_response=authorization_response,
        )
        self.access_token = response['access_token']
        self.renew_token = response['renew_token']

    def renew_access_token(self):
        """
        Retrieves a new access token for the authorized user. This can be used when a token has expired.

        Afterwards the access token and renew token can be read using their respective methods.
        """
        response = self._get_session().refresh_token(
            self._get_url('refresh'),
            refresh_token=self.renew_token,
        )
        self.access_token = response['access_token']
        self.renew_token = response['renew_token']

    def get_access_token(self):
        """
        Returns the access token for the current session. Throws an exception if there is no access token present.
        :return: The access token
        """
        if self.access_token is None:
            raise ValueError("There is no access token present. Request a token using fetch_access_token.")
        return self.access_token

    def get_renew_token(self):
        """
        Returns the renew token for the current session. Throws an exception if there is no renew token present.
        :return: The renew token
        """
        if self.renew_token is None:
            raise ValueError("There is no renew token present. Request a token using fetch_renew_token.")
        return self.renew_token
