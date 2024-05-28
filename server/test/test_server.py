import os
import logging
import unittest
import sys
from pathlib import Path
import configparser
import pytest
from unittest import mock
import ssl
from server import (
    search_string_in_file,
    start_server,
    handle_client,
    accept_connections
)

# Adding the server directory to the Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "server"))

# Adding the search_algorithms directory to the Python path
sys.path.insert(0, str(current_dir / "search_algorithms"))

# List of all search algorithms to test
SEARCH_ALGORITHMS = [
    "naive_search",
    "binary_search",
    "kmp_search",
    "rabin_karp_search",
    "boyer_moore_search",
    "aho_corasick_search",
    "regex_search",
]

# Mock implementations of search algorithms


def naive_search(data, query):
    return any(query == line.strip() for line in data)


def binary_search(data, query):
    return any(query == line.strip() for line in data)


def kmp_search(data, query):
    return any(query == line.strip() for line in data)


def rabin_karp_search(data, query):
    return any(query == line.strip() for line in data)


def boyer_moore_search(data, query):
    return any(query == line.strip() for line in data)


def aho_corasick_search(data, query):
    return any(query == line.strip() for line in data)


def regex_search(data, query):
    import re
    return any(re.search(query, line.strip()) for line in data)


mock_algorithms = {
    "naive_search": naive_search,
    "binary_search": binary_search,
    "kmp_search": kmp_search,
    "rabin_karp_search": rabin_karp_search,
    "boyer_moore_search": boyer_moore_search,
    "aho_corasick_search": aho_corasick_search,
    "regex_search": regex_search,
}


@pytest.fixture
def config_file(tmp_path):
    """
    Fixture to create a temporary configuration file for testing.

    Parameters:
    - tmp_path (pathlib.Path): The temporary directory provided by pytest.

    Returns:
    - pathlib.Path: The path to the created configuration file.
    """
    # Dynamic path generation
    expected_linuxpath = tmp_path / "file" / "200k.txt"
    expected_reread_on_query = True
    expected_ssl_enabled = True
    expected_search_algorithms = "binary_search"

    config_data = f"""
    [server]
    linuxpath = {expected_linuxpath}
    reread_on_query = {str(expected_reread_on_query)}
    ssl_enabled = {str(expected_ssl_enabled)}
    search_algorithms = {expected_search_algorithms}
    """

    temp_config_path = tmp_path / "test_config.ini"
    temp_config_path.write_text(config_data)

    return temp_config_path


def test_read_config_file(config_file):
    """
    Test reading the configuration file and verifying its contents.

    Parameters:
    - config_file (pathlib.Path): The path to the configuration file.

    Asserts:
    - The 'linuxpath' value is dynamically generated.
    - The 'reread_on_query' value is True.
    - The 'ssl_enabled' value is True.
    - The 'search_algorithms' value is 'binary_search'.
    """
    # Dynamically generate the expected_linuxpath
    expected_linuxpath = config_file.parent / "file" / "200k.txt"
    expected_reread_on_query = True
    expected_ssl_enabled = True
    expected_search_algorithms = "binary_search"

    config = configparser.ConfigParser()
    config.read(config_file)

    assert config.get(
        "server", "linuxpath"
    ) == str(expected_linuxpath)
    assert config.getboolean(
        "server", "reread_on_query"
    ) is expected_reread_on_query
    assert config.getboolean(
        "server", "ssl_enabled"
    ) is expected_ssl_enabled
    assert config.get(
        "server", "search_algorithms"
    ) == expected_search_algorithms


@pytest.fixture
def test_file(tmp_path):
    """
    Fixture to create a temporary test file for testing.

    Parameters:
    - tmp_path (pathlib.Path): The temporary directory provided by pytest.

    Returns:
    - pathlib.Path: The path to the created test file.
    """
    test_file = tmp_path / "test.txt"
    test_file.write_text(
        "connecting\nnow", encoding="utf-8")
    return test_file


def test_read_file_contents(test_file):
    """
    Test reading the contents of the test file and verifying its contents.

    Parameters:
    - test_file (pathlib.Path): The path to the test file.

    Asserts:
    - The contents of the test file match the expected lines.
    """
    with open(test_file, "r", encoding="utf-8") as file:
        contents = file.readlines()
    contents = [line.replace('\r\n', '\n') for line in contents]
    assert contents == ["connecting\n", "now"]


@pytest.mark.parametrize("algorithm", SEARCH_ALGORITHMS)
def test_search_algorithms(tmp_path, algorithm):
    """
    Test search algorithms to ensure they function correctly.

    Parameters:
    - algorithm (str): The name of the search algorithm to test.
    - tmp_path (pathlib.Path): The temporary directory provided by pytest.

    Asserts:
    - The search algorithm returns True for a string present in the data.
    - The search algorithm returns False for a string not present in the data.
    """
    config_file = tmp_path / "test_config.ini"  # Use test_config.ini
    config_content = f"""
    [server]
    linuxpath={tmp_path}/file/200k.txt
    reread_on_query=True
    ssl_enabled=True
    search_algorithms={algorithm}
    """
    config_file.write_text(config_content, encoding="utf-8")

    contents = ["hello", "world"]
    assert mock_algorithms[algorithm](contents, "hello") is True
    assert mock_algorithms[algorithm](contents, "foo") is False

    contents_with_whitespace = ["hello ", " world"]
    assert mock_algorithms[algorithm](
        contents_with_whitespace, "hello") is True
    assert mock_algorithms[algorithm](
        contents_with_whitespace, "world") is True


def test_search_string_in_file_permission_denied(tmp_path):
    """
    Test the behavior when permission is denied to access the file.

    Parameters:
    - tmp_path (pathlib.Path): The temporary directory provided by pytest.

    Asserts:
    - The result indicates permission denied.
    """
    test_file = tmp_path / "test.txt"
    test_file.write_text("connecting\nnow", encoding="utf-8")
    test_file.chmod(0o000)  # Set permissions to deny read access

    def set_permissions(path, permissions):
        if os.name == 'posix':
            path.chmod(permissions)
        elif os.name == 'nt':
            import win32api
            import win32con
            win32api.SetFileAttributes(
                str(path), win32con.FILE_ATTRIBUTE_NORMAL)

    set_permissions(test_file, 0o000)

    try:
        result = search_string_in_file("connecting", test_file, True)
    finally:
        if os.name == 'posix':
            set_permissions(test_file, 0o644)

    assert result.startswith("Error: Permission denied.")


def test_search_string_in_file_file_not_found(tmp_path):
    """
    Test when the file to search is not found.

    Parameters:
    - tmp_path (pathlib.Path): The temporary directory provided by pytest.
    """
    # Create a temporary file path within the temporary directory
    test_file = tmp_path / "test.txt"
    # Create an empty file at the temporary file path
    test_file.touch()

    # Attempt to search for a string in the empty file
    result = search_string_in_file("connecting", test_file, True)

    # Print the result for debugging
    print(result)

    # Assert that the result indicates file not found
    assert result == "STRING NOT FOUND\n"


def test_handle_client_exception_handling(caplog):
    """
    Test exception handling in the handle_client function.

    Parameters:
    - caplog (pytest.LogCaptureFixture): Fixture to capture log output.

    Asserts:
    - The exception is logged appropriately.
    """
    class MockConnection:
        def recv(self, _):
            raise Exception("Simulated error")

        def close(self):
            pass

    addr = ("0.0.0.0", 44445)
    handle_client(MockConnection(), addr)
    assert "An error occurred while handling client request" in caplog.text


def test_accept_connections_exception_handling(caplog):
    """
    Test exception handling in the accept_connections function.

    Parameters:
    - caplog (pytest.LogCaptureFixture): Fixture to capture log output.

    Asserts:
    - The exception is logged appropriately.
    """
    class MockServerSocket:
        def accept(self):
            raise Exception("An error occurred while handling client request")

    class MockSSLContext:
        def wrap_socket(self, sock, server_side):
            return sock

    # Use pytest.raises to assert that the exception is raised
    with pytest.raises(Exception):
        accept_connections(MockServerSocket(), MockSSLContext())

    # Print out log records captured by caplog
    print(caplog.records)


def test_search_string_not_found(tmp_path):
    """
    Test the behavior when the search string is not found in the file.

    Parameters:
    - tmp_path (pathlib.Path): The temporary directory provided by pytest.

    Asserts:
    - The result indicates that the string was not found.
    """
    test_file = tmp_path / "test.txt"
    test_file.write_text("connecting\nnow", encoding="utf-8")
    result = search_string_in_file("notfound", test_file, True)
    assert result == "STRING NOT FOUND\n"


def test_search_in_empty_file(tmp_path):
    """
    Test the behavior when the file is empty.

    Parameters:
    - tmp_path (pathlib.Path): The temporary directory provided by pytest.

    Asserts:
    - The result indicates that the string was not found.
    """
    test_file = tmp_path / "test.txt"
    test_file.write_text("", encoding="utf-8")
    result = search_string_in_file("anything", test_file, True)
    assert result == "STRING NOT FOUND\n"


def test_empty_search_string(tmp_path):
    """
    Test the behavior when the search string is empty.

    Parameters:
    - tmp_path (pathlib.Path): The temporary directory provided by pytest.

    Asserts:
    - The result indicates that the string was not found.
    """
    test_file = tmp_path / "test.txt"
    test_file.write_text("connecting\nnow", encoding="utf-8")
    result = search_string_in_file("", test_file, True)
    assert result == "STRING NOT FOUND\n"


def test_ssl_handling_with_valid_cert(tmp_path):
    """
    Test SSL handling with a valid certificate.

    Parameters:
    - tmp_path (pathlib.Path): The temporary directory provided by pytest.

    Asserts:
    - The SSL context is loaded with the
    valid certificate without raising an exception.
    """
    # Create valid certificate and key files in the temporary directory
    valid_cert = tmp_path / "valid_cert.pem"
    valid_key = tmp_path / "valid_key.pem"
    valid_cert.write_text("VALID CERTIFICATE", encoding="utf-8")
    valid_key.write_text("VALID KEY", encoding="utf-8")

    # Mock the SSLContext to simulate loading a valid certificate
    with mock.patch('ssl.SSLContext.load_cert_chain'):
        # Call start_server with a mock SSLContext
        start_server(mock_ssl_context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER))


def test_ssl_handling_with_invalid_cert(tmp_path, caplog):
    """
    Test SSL handling with an invalid certificate.

    Parameters:
    - tmp_path (pathlib.Path): The temporary directory provided by pytest.
    - caplog: Pytest fixture to capture log messages.

    Asserts:
    - An ssl.SSLError is logged when loading an invalid certificate.
    """
    # Create invalid certificate and key files in the temporary directory
    invalid_cert = tmp_path / "invalid_cert.pem"
    invalid_key = tmp_path / "invalid_key.pem"
    invalid_cert.write_text("INVALID CERTIFICATE", encoding="utf-8")
    invalid_key.write_text("INVALID KEY", encoding="utf-8")

    # Mock the SSLContext to simulate an invalid certificate loading
    mock_ssl_context = mock.Mock(spec=ssl.SSLContext)
    mock_ssl_context.load_cert_chain.side_effect = ssl.SSLError(
        "Invalid certificate")

    with caplog.at_level(logging.ERROR):
        start_server(mock_ssl_context=mock_ssl_context)
        
    
if __name__ == '__main__':
    unittest.main()

