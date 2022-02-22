import time
import unittest
from app.common.server_utils import process_client_message
from app.common.variables import RESPONSE, ERROR, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME


class TestServerClass(unittest.TestCase):

    def setUp(self) -> None:
        self.bad_response = {RESPONSE: 400, ERROR: 'Bad request'}
        self.ok_response = {RESPONSE: 200}

    def test_process_right_client_message(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: time.time(), USER: {ACCOUNT_NAME: 'Guest'}}),
                         self.ok_response)

    def test_process_wrong_action_client_message(self):
        self.assertEqual(process_client_message({ACTION: '12aw', TIME: time.time(), USER: {ACCOUNT_NAME: 'Guest'}}),
                         self.bad_response)

    def test_process_no_action_client_message(self):
        self.assertEqual(process_client_message({TIME: time.time(), USER: {ACCOUNT_NAME: 'Guest'}}),
                         self.bad_response)

    def test_process_no_time_client_message(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}),
                         self.bad_response)

    def test_process_no_user_client_message(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: time.time()}),
                         self.bad_response)



