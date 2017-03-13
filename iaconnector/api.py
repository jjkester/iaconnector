import random
import string
import warnings

import logging
import requests

from iaconnector.exceptions import APIError


logger = logging.getLogger('iaconnector')


class APIConsumer(object):
    """
    API consumer for the Inter-Actief API.

    The methods performing API calls are documented to explain the call according to the official API documentation.
    Additionally, the exact JSON-RPC method name is included for reference.

    The API documentation can be found at https://github.com/Inter-Actief/api-docs.
    """
    base_url = 'https://api.ia.utwente.nl/app/lennart/'

    def __init__(self, access_token=None, base_url=None, connector=None, preview_mode=False):
        """
        :param access_token: (Optional) The access token to use with the API.
        :param base_url: (Optional) The URL on which the API resides. Defaults to the production Inter-Actief API.
        :param connector: (Optional) The `IAConnector` instance this consumer is used with.
        :param preview_mode: (Optional) Whether to use a sandboxed test environment.
        """
        self.access_token = access_token
        self.connector = connector
        self.preview_mode = preview_mode

        if base_url is not None:
            if base_url[-1:] != '/':
                base_url += '/'
            self.base_url = base_url

        logger.debug("API initialized at {url:s} with preview mode {preview:s}.".format(
            url=self.base_url,
            preview='yes' if self.preview_mode else 'no',
        ))

    @staticmethod
    def _get_exception(error_code):
        """
        Returns the appropriate exception class for the given error code.

        :param error_code: The error code for the exception.
        :return: The exception class.
        """
        errors = {}

        for cls in APIError.__subclasses__():
            if hasattr(cls, 'error_code') and cls.error_code is not None:
                errors[cls.error_code] = cls

        return errors.get(error_code, APIError)

    def _call(self, method, *params):
        """
        Performs a JSON-RPC call. Raises an APIError (or subclassed) exception in case of an error.

        The (JSON) result is decoded and returned as native Python objects.

        :param method: The API method to call.
        :param call_id: (Optional) An identifier for the API call. This is not used at this time.
        :param params: The parameters for the method call.
        :return: The result of the call as Python objects.
        """
        call_id = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))

        headers = {
            'User-Agent': 'IAConnector',
        }

        if self.access_token:
            headers['Authorization'] = 'Bearer %s' % self.access_token

        if self.preview_mode:
            headers['User-Agent'] += ' PREVIEWMODE'

        logger.debug("API request: {method:s}({params:s}).".format(
            method=method,
            params=','.join(map(str, params)),
        ))

        response = requests.post(
            url=self.base_url,
            json={
                'method': method,
                'params': params,
                'id': call_id,
            },
            headers=headers
        )

        response_json = response.json()

        logger.debug("API response: {json:s}".format(json=response_json))

        if 'error' in response_json and response_json['error'] is not None:
            error = response_json['error']

            if 'code' in error and 'message' in error:
                raise self._get_exception(error['code'])(error['message'])
            else:
                raise APIError(error.get('message'))
        try:
            result = response_json['result']
        except (TypeError, KeyError) as e:
            logger.error("Invalid response from server: %s" % str(e))
            raise APIError("Invalid response from server: %s" % str(e))

        return result

    # ----------------------
    # Begin of API endpoints
    # ----------------------

    # Authentication module

    def get_device_id(self):
        """
        Requests a new device id. It is recommended to call this method only once in your apps lifetime, just after its
        first start, and store the result for further use.

        JSON-RPC method: `getDeviceId`.

        :return: The assigned device id.
        """
        return self._call('getDeviceId')

    def get_auth_token(self, username, password, device_id):
        """
        Attempts to log in and returns the authentication token.

        This method is deprecated, please use OAuth and do not directly ask the user for his/her password.

        JSON-RPC method: `getAuthToken`.

        :param username: The username of the user.
        :param password: The password of the user.
        :param device_id: The device id of this app.
        :return: The authentication token for further use.
        """
        warnings.warn("API method 'get_auth_token' is deprecated, use OAuth instead.", DeprecationWarning, stacklevel=2)
        return self._call('getAuthToken', username, password, device_id)

    def check_auth_token(self):
        """
        Checks if an authentication token is (still) valid. It is recommended to do this after resuming your app, to see
        if the token was revoked.

        JSON-RPC method: `checkAuthToken`.

        :return: Whether the authentication token is valid.
        """
        return self._call('checkAuthToken')

    def revoke_auth_token(self):
        """
        Revokes an authentication token.

        JSON-RPC method: `revokeAuthToken`.

        :return: Whether the token was successfully revoked.
        """
        return self._call('revokeAuthToken')

    def get_person_details(self):
        """
        Retrieves details of the currently authenticated person.

        For a detailed description of the result, please consult the official API documentation.

        JSON-RPC method: `getPersonDetails`.

        :return: A dictionary containing the user's details.
        """
        return self._call('getPersonDetails')

    # Activity module

    def get_activity_stream(self, begin, end):
        """
        Retrieves a list of activities.

        The authentication token is used to check if the user is signed up for an activity.

        For a detailed description of the result, please consult the official API documentation.

        JSON-RPC method: `getActivityStream`.

        :param begin: The minimal end date (inclusive).
        :param end: The maximal begin date (exclusive).
        :return: An list of dictionaries containing the activity details.
        """
        return self._call('getActivityStream', begin, end)

    def get_activity_details(self, id):
        """
        Retrieves the details of an activity, including its signup options.

        The authentication token is used to check if the user is signed up for an activity.

        For a detailed description of the result, please consult the official API documentation.

        JSON-RPC method: `getActivityDetailed`.

        :param id: The id of the activity.
        :return: A dictionary containing the activity details.
        """
        return self._call('getActivityDetailed', id)

    def activity_signup(self, id, price, options):
        """
        Marks the user as an attendee to an activity.

        The calculated costs for the activity are used to check if the user was presented with the right price. The
        selected options may change the price of the activity.

        The options must be given as an list of dictionaries containing an id (of the option) and appropriate value.

        JSON-RPC method: `activitySignup`.

        :param id: The id of the activity.
        :param price: The calculated costs for the activity.
        :param options: The selected options for the activity.
        """
        self._call('activitySignup', id, price, options)

    def revoke_activity_signup(self, id):
        """
        Unmarks the current user as an attendee to an activity.

        JSON-RPC method: `activityRevokeSignup`.

        :param id: The id of the activity.
        """
        self._call('activityRevokeSignup', id)
