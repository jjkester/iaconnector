import random
import string

import requests

from iaconnector.exceptions import APIError


class APIConsumer(object):
    """
    API consumer for the Inter-Actief API.
    """
    base_url = 'https://api.ia.utwente.nl/app/lennart/'

    def __init__(self, access_token=None, base_url=None, connector=None):
        """
        :param base_url: The URL on which the API resides. Defaults to the production Inter-Actief API
        """
        self.access_token = access_token
        self.connector = connector

        if base_url is not None:
            if base_url[-1:] != '/':
                base_url += '/'
            self.base_url = base_url

    @staticmethod
    def _get_exception(error_code):
        """
        Returns the appropriate exception class for the given error code.
        :param error_code: The error code for the exception
        :return: The exception class
        """
        errors = {}

        for cls in APIError.__subclasses__():
            if hasattr(cls, 'error_code') and cls.error_code is not None:
                errors[cls.error_code] = cls

        return errors.get(error_code, APIError)

    def _call(self, method, *params):
        """
        Performs a JSON-RPC call. Raises an APIError (or subclassed) exception in case of an error.

        :param method: The method to call
        :param call_id: An optional id. This is not used at this time
        :param params: The parameters for the method
        :return: The result of the call
        """
        call_id = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))

        headers = {}

        if self.access_token:
            headers['Authorization'] = 'Bearer %s' % self.access_token

        response = requests.post(
            url=self.base_url,
            json={
                'method': method,
                'params': params,
                'id': call_id,
            },
            headers=headers
        )

        if 'error' in response and response['error'] is not None:
            error = response['error']

            if 'code' in error and 'message' in error:
                raise self._get_exception(error['code'])(error['message'])
            else:
                raise APIError(error.get('message'))
        try:
            result = response.json()['result']
        except (TypeError, KeyError) as e:
            raise APIError("Invalid response from server: %s" % str(e))

        return result

    # Begin of API endpoints

    # Authentication module

    def get_device_id(self):
        """
        Requests a new device id. It is recommended to call this method only once in your apps lifetime, just after its
        first start, and store the result for further use.

        :return: The assigned device id
        """
        return self._call('getDeviceId')

    def get_auth_token(self, username, password, device_id):
        """
        Attempts to log in and returns the authentication token.

        This method is deprecated, please use OAuth and do not directly ask the user for his/her password.

        :param username: The username of the user
        :param password: The password of the user
        :param device_id: The device id of this app
        :return: The authentication token for further use
        """
        return self._call('getAuthToken', username, password, device_id)

    def check_auth_token(self, token):
        """
        Checks if an authentication token is (still) valid. It is recommended to do this after resuming your app, to see
        if the token was revoked.

        :param token: The obtained authentication token
        :return: Whether the authentication token is valid
        """
        return self._call('checkAuthToken', token)

    def revoke_auth_token(self, token):
        """
        Revokes an authentication token.

        :param token: The obtained authentication token to revoke
        :return: Whether the token was successfully revoked
        """
        return self._call('revokeAuthToken', token)

    def get_person_details(self, token):
        """
        Retrieves details of the currently authenticated person.

        :param token: The obtained authentication token for the user
        :return: A dictionary containing the user's details
        """
        return self._call('getPersonDetails', token)

    # Activity module

    def get_activity_stream(self, begin, end, token=None):
        """
        Retrieves a list of activities.

        The authentication token is used to check if the user is signed up for an activity.

        :param begin: The minimal end date (inclusive)
        :param end: The maximal begin date (exclusive)
        :param token: The optional authentication token
        :return: An array of dictionaries containing the activity details
        """
        return self._call('getActivityStream', begin, end, token)

    def get_activity_details(self, id, token=None):
        """
        Retrieves the details of an activity, including its signup options

        The authentication token is used to check if the user is signed up for an activity.

        :param id: The id of the activity
        :param token: The optional authentication token
        :return: A dictionary containing the activity details
        """
        return self._call('getActivityDetailed', id, token)

    def activity_signup(self, id, price, options, token):
        """
        Marks the user as an attendee to an activity.

        The calculated costs for the activity are used to check if the user was presented with the right price. The
        selected options may change the price of the activity.

        The options must be given as an array of dictionaries containing an id (of the option) and appropriate value.

        :param id: The id of the activity
        :param price: The calculated costs for the activity
        :param options: The selected options for the activity
        :param token: The authentication token of the user to sign up
        """
        return self._call('activitySignup', id, price, options, token)

    def revoke_activity_signup(self, id, token):
        """
        Unmarks the current user as an attendee to an activity.

        :param id: The id of the activity
        :param token: The authentication token of the user to sign out
        """
        return self._call('activityRevokeSignup', id, token)
