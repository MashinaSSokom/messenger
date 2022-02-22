import sys
import time
import unittest

from app.common.client_utils import create_presence, process_response
from app.common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR


class TestClientUtilsClass(unittest.TestCase):
    def setUp(self) -> None:
        self.presence = {
            ACTION: PRESENCE,
            TIME: 1,
            USER: {ACCOUNT_NAME: 'Guest'}
        }

    def test_create_presence(self):
        test_presence = create_presence(account_name='Guest')
        test_presence[TIME] = 1
        self.assertEqual(self.presence, test_presence)

    def test_process_right_response(self):
        self.assertEqual(process_response({RESPONSE: 200}), '200: OK')

    def test_process_bad_response(self):
        self.assertEqual(process_response({RESPONSE: 400, ERROR: 'Bad request'}), f'400: Bad request')

    def test_process_invalid_response(self):
        self.assertRaises(ValueError, process_response, {ERROR: 'Bad request'})
