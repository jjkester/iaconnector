import unittest

from iaconnector import exceptions, OAuthConsumer
from iaconnector import APIConsumer


class APITest(unittest.TestCase):
    """
    Test case for the API functionality.

    This unit test does not interact with the API itself, therefore, an acceptance test is needed.
    """
    def setUp(self):
        self.api = APIConsumer()

    def test_init(self):
        """Tests the behaviour of the constructor."""
        self.assertEqual(APIConsumer().base_url, APIConsumer.base_url)
        self.assertEqual(APIConsumer(base_url='https://test.example/api').base_url, 'https://test.example/api/')

    def test_exceptions(self):
        """Tests whether the correct exceptions are selected."""
        self.assertEqual(self.api._get_exception(None), exceptions.APIError)
        self.assertEqual(self.api._get_exception(666), exceptions.APIError)
        self.assertEqual(self.api._get_exception(-32700), exceptions.APIError)
        self.assertEqual(self.api._get_exception(403), exceptions.NotLoggedInError)
        self.assertEqual(self.api._get_exception(406), exceptions.UnknownDeviceError)
        self.assertEqual(self.api._get_exception(412), exceptions.SignupError)
        self.assertEqual(self.api._get_exception(500), exceptions.OtherError)


class OAuthTest(unittest.TestCase):
    """
    Test case for the OAuth functionality.

    This unit test does not interact with the OAuth server itself, therefore, an acceptance test is needed.
    """
    config = {
        'client_id': 'test',
        'client_secret': 'vault',
        'redirect_uri': 'https://example.test/oauth',
        'scope': ['ice_creams', 'waffles'],
        'access_token': 'access_granted',
        'renew_token': 'renew_possible',
    }

    def setUp(self):
        self.oauth = OAuthConsumer(**self.config)

    def test_init(self):
        """Tests the behaviour of the constructor."""
        self.assertEqual(self.oauth.client_id, self.config['client_id'])
        self.assertEqual(self.oauth.client_secret, self.config['client_secret'])
        self.assertEqual(self.oauth.redirect_uri, self.config['redirect_uri'])
        self.assertEqual(self.oauth.scope, self.config['scope'])
        self.assertEqual(self.oauth.access_token, self.config['access_token'])
        self.assertEqual(self.oauth.renew_token, self.config['renew_token'])

        oauth = OAuthConsumer(base_url='https://test.example/oauth', **self.config)
        self.assertEqual(oauth.base_url, 'https://test.example/oauth/')
        self.assertEqual(OAuthConsumer(**self.config).base_url, OAuthConsumer.base_url)

    def test_get_session(self):
        """Tests the _get_session method."""
        self.assertIsNone(self.oauth._session)

        session = self.oauth._get_session()

        self.assertIsNotNone(session)
        self.assertEquals(self.oauth._get_session(), session)

    def test_get_url(self):
        """Tests the _get_url method."""
        base_url = self.oauth.base_url

        self.assertEqual(self.oauth._get_url('authorization'), base_url + 'authorize/')
        self.assertEqual(self.oauth._get_url('token'), base_url + 'token/')
