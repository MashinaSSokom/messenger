import json
import sys
import unittest
from ..common.utils import create_argv_parser, get_message, send_message
from ..common.variables import ENCODING, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR


class TestSocket:
    def __init__(self, test_message):
        self.test_message = test_message
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        json_message = json.dumps(self.test_message)
        self.encoded_message = json_message.encode(ENCODING)
        self.received_message = message_to_send

    def recv(self, max_len):
        json_message = json.dumps(self.test_message)
        return json_message.encode(ENCODING)


class TestUtilsClass(unittest.TestCase):
    def setUp(self) -> None:
        self.right_message = {
            ACTION: PRESENCE,
            TIME: 1,
            USER: {ACCOUNT_NAME: 'Guest'}
        }
        self.bad_response = {RESPONSE: 400, ERROR: 'Bad request'}
        self.ok_response = {RESPONSE: 200}

    def test_create_argv_parser(self):
        sys.argv += ['-a', '127.0.1.1', '-p', '8888']
        parser = create_argv_parser()
        namespace = parser.parse_args()
        self.assertListEqual([namespace.a, namespace.p], ['127.0.1.1', 8888])

    def test_send_message_correct_encoding(self):
        test_socket = TestSocket(self.right_message)
        send_message(test_socket, self.right_message)
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)

    def test_get_message_ok_response(self):
        test_socket_ok_resp = TestSocket(self.ok_response)
        self.assertEqual(get_message(test_socket_ok_resp), self.ok_response)

    def test_get_message_raise_value_error(self):
        test_socket_ok_resp = TestSocket("Not dict")
        self.assertRaises(ValueError, get_message, test_socket_ok_resp)

    def test_get_message_bad_response(self):
        test_socket_bad_resp = TestSocket(self.bad_response)
        self.assertEqual(get_message(test_socket_bad_resp), self.bad_response)
