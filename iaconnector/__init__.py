"""
Library for interacting with the Inter-Actief web site (https://www.inter-actief.utwente.nl).

This library provides OAuth (2) authentication and access to the API. Access to these resources is limited to members
of study association Inter-Actief.
"""
import logging

from iaconnector.api import APIConsumer
from iaconnector.oauth import OAuthConsumer
from iaconnector.exceptions import APIError, NotLoggedInError, SignupError, UnknownDeviceError, OtherError


logger = logging.getLogger('iaconnector')


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

        :param client_id: The client id of your application.
        :param client_secret: The client secret of your application.
        :param scope: The scope your application requires.
        :param redirect_url: The URL to redirect to after authenticating.
        :param access_token: (Optional) The access token, if known.
        :param renew_token: (Optional) The renew token, if known.
        :param base_url: (Optional) The base URL of the OAuth implementation. Overrides the default production URL.
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
            connector=self,
        )

    def init_api(self, base_url=None):
        """
        Initializes the API consumer. This is only possible if the consumer has not been initializes yet.

        :param base_url: (Optional) The URL of the API implementation. Overrides the default production URL.
        """
        assert self._api is None
        self._api = APIConsumer(
            base_url=base_url,
            connector=self,
        )

    def propagate_tokens(self, access_token=None, renew_token=None, source=None):
        """
        Propagates the access token to the IAConnector elements.

        This method functions as a bridge to automatically inform the API of a token obtained using OAuth. Therefore, it
        should not be necessary to call this method yourself. Do not use this method to resume a previous OAuth and/or
        API session - the preferred way to do this is by calling the `init_oauth` and `init_api` methods on a new
        instance.

        If no access token or renew token is given the previous value is not changed. It is therefore not possible to
        unset access tokens or renew tokens using this method.

        :param access_token: The access token to propagate.
        :param renew_token: The renew token to propagate.
        :param source: The source object which initiated the propagation.
        """
        # Set for API
        if not isinstance(source, APIConsumer) and self._api is not None:
            if access_token is not None:
                self._api.access_token = access_token
                logger.debug("Access token propagated to API.")

        # Set for OAuth
        if not isinstance(source, OAuthConsumer) and self._oauth is not None:
            if access_token is not None:
                self._oauth.access_token = access_token
                logger.debug("Access token propagated to OAuth.")
            if renew_token is not None:
                self._oauth.renew_token = renew_token
                logger.debug("Renew token propagated to OAuth.")

    @property
    def oauth(self):
        return self._oauth

    @property
    def api(self):
        return self._api
