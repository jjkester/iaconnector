"""
Library for interacting with the Inter-Actief web site (https://www.inter-actief.utwente.nl).

This library provides OAuth (2) authentication and access to the API. Access to these resources is limited to members
of study association Inter-Actief.
"""
from iaconnector.api import APIConsumer
from iaconnector.oauth import OAuthConsumer


class IAConnector(object):
    """
    Wrapper class for interacting with Amelie, the Inter-Actief web site.

    OAuth and API functionality has to be initialized before it can be used using their respective init methods.
    """
    def __init__(self):
        self._oauth = None
        self._api = None

    def init_oauth(self, client_id, client_secret, scope, redirect_url, access_token=None,
                        renew_token=None, base_url=None):
        """
        Initializes the OAuth consumer. This is only possible if the consumer has not been initialized yet.

        :param client_id: The client id of your application
        :param client_secret: The client secret of your application
        :param scope: The scope your application requires
        :param redirect_url: The URL to redirect to after authenticating
        :param access_token: The optional access token if known
        :param renew_token: The optional renew token if known
        :param base_url: The optional URL where the OAuth implementation resides.
        """
        assert self._oauth is None
        self._oauth = OAuthConsumer(
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
            redirect_uri=redirect_url,
            access_token=access_token,
            renew_token=renew_token,
            base_url=base_url,
        )

    def init_api(self, base_url=None):
        """
        Initializes the API consumer. This is only possible if the consumer has not been initializes yet.

        :param base_url: The optional URL where the API implementation resides.
        """
        assert self._api is None
        self._api = APIConsumer(
            base_url=base_url,
        )

    @property
    def oauth(self):
        return self._oauth

    @property
    def api(self):
        return self._api
