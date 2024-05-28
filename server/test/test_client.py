import pytest
import unittest
from unittest import mock
import ssl
import socket
from client import send_query, USE_SSL, HOST, PORT


def test_send_query_ssl():
    """
    Test send_query function with SSL enabled.
    """
    query = "test search query"
    expected_response = "mock response"

    # Mock socket and SSL context
    with mock.patch(
        "client.socket.create_connection"
    ) as mock_create_conn, \
            mock.patch(
                "client.ssl.SSLContext"
    ) as mock_ssl_context:

        # Mock objects
        mock_socket = mock.Mock()
        mock_ssl_socket = mock.Mock()

        # Set up mock methods
        mock_create_conn.return_value.__enter__.return_value = mock_socket
        mock_ssl_context_instance = mock_ssl_context.return_value
        mock_wrap_socket = mock_ssl_context_instance.wrap_socket.return_value
        mock_wrap_socket.__enter__.return_value = mock_ssl_socket
        # Mock the response
        mock_ssl_socket.recv.return_value = expected_response.encode(
        )

        # Call the function
        with mock.patch(
                'builtins.print'
        ) as mock_print:
            send_query(query)
            mock_print.assert_called_once_with(
                expected_response)

        # Assert calls
        mock_create_conn.assert_called_once_with(
            (HOST, PORT))
        mock_ssl_context.assert_called_once_with(
            ssl.PROTOCOL_TLS_CLIENT)
        mock_ssl_context_instance.wrap_socket.assert_called_once_with(
            mock_socket, server_hostname=HOST)
        mock_ssl_socket.sendall.assert_called_once_with(
            query.encode())
        mock_ssl_socket.recv.assert_called_once_with(1024)


def test_send_query_non_ssl():
    """
    Test send_query function without SSL enabled.
    """
    query = "test search query"
    expected_response = "mock response"

    # Mock socket
    with mock.patch("client.USE_SSL", False):
        with mock.patch(
                "client.socket.create_connection"
        ) as mock_create_conn:

            # Mock object
            mock_socket = mock.Mock()
            mock_create_conn.return_value.__enter__.return_value = (
                mock_socket
            )

            # Set up mock method
            mock_socket.recv.return_value = expected_response.encode()

            # Call the function
            with mock.patch('builtins.print') as mock_print:
                send_query(query)
                mock_print.assert_called_once_with(expected_response)

            # Assert calls
            mock_create_conn.assert_called_once_with(
                (HOST, PORT))
            mock_socket.sendall.assert_called_once_with(
                query.encode())
            mock_socket.recv.assert_called_once_with(1024)


def test_send_query_connection_error():
    """
    Test send_query function when a connection error occurs.
    """
    query = "test search query"

    # Mock USE_SSL to True and create a connection error
    with mock.patch("client.USE_SSL", True):
        with mock.patch("client.socket.create_connection",
                        side_effect=OSError("Connection error")):
            # Call the function
            with mock.patch('builtins.print') as mock_print:
                send_query(query)
                mock_print.assert_called_once_with(
                    "Error: Connection error")


def test_send_query_ssl_error():
    """
    Test send_query function when an SSL error occurs.
    """
    query = "test search query"

    # Mock USE_SSL to True and create an SSL error
    with mock.patch("client.USE_SSL", True):
        with mock.patch(
            "client.socket.create_connection"
        ) as mock_create_conn, \
                mock.patch(
                    "client.ssl.SSLContext"
        ) as mock_ssl_context:

            mock_ssl_context_instance = mock_ssl_context.return_value
            mock_ssl_context_instance.wrap_socket.side_effect = ssl.SSLError(
                "SSL error")

            # Call the function
            with mock.patch('builtins.print') as mock_print:
                send_query(query)

if __name__ == '__main__':
        unittest.main()
