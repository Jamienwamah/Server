"""
Server module to handle client connections and search queries.

This server listens for incoming client connections, receives search queries,
and searches for the specified string in a file. It supports SSL for secure
connections and can dynamically import search algorithms.
"""

import socket
import sys
import threading
import time
import ssl
import os
import configparser
import logging
import importlib

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="DEBUG: %(asctime)s - %(message)s")

# Let's the search_algorithms directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
search_algorithms_path = os.path.abspath(
    os.path.join(current_dir, "..", "search_algorithms")
)
if search_algorithms_path not in sys.path:
    sys.path.insert(0, search_algorithms_path)

# Configuration
config = configparser.ConfigParser()

# Use environment variable for configuration file path, with a fallback default
CONFIG_PATH = os.getenv("CONFIG_FILE_PATH",
                        os.path.join(current_dir, "config.ini"))
config.read(CONFIG_PATH)

# Ensure the 'server' section exists
if not config.has_section("server"):
    raise configparser.NoSectionError("server")

HOST = config.get("server", "host", fallback="0.0.0.0")
PORT = config.getint("server", "port", fallback=44445)
REREAD_ON_QUERY = config.getboolean("server",
                                    "reread_on_query", fallback=False)
SSL_ENABLED = config.getboolean("server", "ssl_enabled", fallback=False)
CERTFILE = config.get("server", "certfile", fallback="cert.pem")
KEYFILE = config.get("server", "keyfile", fallback="key.pem")
SEARCH_ALGORITHM = config.get("server",
                              "search_algorithms", fallback="binary_search")
# Explicitly import search algorithm
if SEARCH_ALGORITHM == "binary_search":
    from search_algorithms.binary_search import (
        binary_search as search_function
    )
elif SEARCH_ALGORITHM == "aho_corasick_search":
    from search_algorithms.aho_corasick_search import (
        aho_corasick_search as search_function
    )
elif SEARCH_ALGORITHM == "kmp_search":
    from search_algorithms.kmp_search import (
        kmp_search as search_function
    )
elif SEARCH_ALGORITHM == "boyer_moore_search":
    from search_algorithms.boyer_moore_search import (
        boyer_moore_search as search_function
    )
elif SEARCH_ALGORITHM == "naive_search":
    from search_algorithms.naive_search import (
        naive_search as search_function
    )
elif SEARCH_ALGORITHM == "rabin_karp_search":
    from search_algorithms.rabin_karp_search import (
        rabin_karp_search as search_function
    )
elif SEARCH_ALGORITHM == "regex_search":
    from search_algorithms.regex_search import (
        regex_search as search_function
    )
else:
    raise ImportError(
        f"Search algorithm '{SEARCH_ALGORITHM}' is not recognized.")


# Fetch file path from config
file_path = config.get("server", "linuxpath")
if not file_path:
    raise ValueError("File path not found in configuration file")

# Global cache for file lines when not re-reading on each query
FILE_LINES_CACHE = None


def search_string_in_file(
    search_string: str, path: str, reread_on_query: bool
) -> str:
    """
    Search for a string in the specified file.

    Parameters:
    - search_string: The string to search for.
    - path: The path of the file to search in.
    - reread_on_query: Boolean indicating whether to
    reread the file on each query.

    Returns:
    - A string indicating whether the search string was found or not,
    or an error message if the file is not found.
    """
    global FILE_LINES_CACHE
    start_time = time.time()

    try:
        if reread_on_query:
            with open(path, "r", encoding="utf-8") as file:
                lines = file.readlines()
        else:
            if FILE_LINES_CACHE is None:
                with open(path, "r", encoding="utf-8") as file:
                    FILE_LINES_CACHE = file.readlines()
            lines = FILE_LINES_CACHE

        for line in lines:
            if line.strip() == search_string:
                execution_time = (
                    time.time() - start_time
                ) * 1000  # Convert to milliseconds
                logging.debug(
                    "Execution time: %.2f ms for query: %s",
                    execution_time, search_string
                )
                return "STRING EXISTS\n"
        execution_time = (time.time() - start_time) * 1000
        logging.debug(
            "Execution time: %.2f ms for query: %s",
            execution_time, search_string
        )
        return "STRING NOT FOUND\n"
    except PermissionError:
        logging.error("Permission denied: Cannot access file '%s'", path)
        return (
            "Error: Permission denied. You do not have permission "
            "to access the file.\n"
        )
    except FileNotFoundError:
        logging.error("File not found: '%s'", path)
        return "Error: File not found.\n"
    except Exception as e:
        logging.exception("An error occurred while searching the file")
        return f"Error: {e}\n"


def handle_client(conn, addr):
    """
    Handle the client connection and process the search query.

    Parameters:
    - conn: The connection object.
    - addr: The address of the client.
    """
    try:
        # Decode the received data, replacing undecodable bytes
        data = conn.recv(1024).decode("utf-8", errors="replace").strip("\x00")

        start_time = time.time()
        result = search_string_in_file(data, file_path, REREAD_ON_QUERY)
        execution_time = (time.time() - start_time) * 1000

        conn.sendall(result.encode())
        logging.debug(
            "Search Query: %s, Requesting IP: %s, Execution time: %.2f ms",
            data,
            addr,
            execution_time,
        )
    except Exception as e:
        logging.exception(
            "An error occurred while handling client request: %s", e)
    finally:
        conn.close()


def start_server(
        mock_socket=None, mock_ssl_context=None,
        mock_accept_connections=None, raise_exceptions=False):
    """
    Start the server to listen for incoming connections and handle them.

    Parameters:
    - mock_socket: Mock socket object for testing.
    - mock_ssl_context: Mock SSL context object for testing.
    - mock_accept_connections: Mock accept_connections function for testing.
    """
    try:
        if SSL_ENABLED:
            context = (
                ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                if mock_ssl_context is None
                else mock_ssl_context
            )
            context.load_cert_chain(
                certfile="server.crt", keyfile="server.key")

            server_socket = (
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if mock_socket is None
                else mock_socket
            )
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()

            logging.info(
                "Server started on %s:%d with SSL enabled", HOST, PORT)

            accept_thread = threading.Thread(
                target=accept_connections,
                args=(server_socket, context, mock_accept_connections),
            )
            accept_thread.start()
        else:
            server_socket = (
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if mock_socket is None
                else mock_socket
            )
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()

            logging.info("Server started on %s:%d without SSL", HOST, PORT)

            accept_thread = threading.Thread(
                target=accept_connections,
                args=(server_socket, None, mock_accept_connections),
            )
            accept_thread.start()
    except ssl.SSLError as e:
        if "wrong version number" in str(e):
            logging.error(
                "SSL error: %s - [SSL: WRONG_VERSION_NUMBER] wrong "
                "version number (_ssl.c:1002)",
                e,
            )
        else:
            logging.error("SSL error: %s", e)
        if raise_exceptions:
            raise
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        if raise_exceptions:
            raise


def accept_connections(
        server_socket, ssl_context, mock_accept_connections=None):
    """
    Accept connections from clients and handle them.

    Parameters:
    - server_socket: Server socket object.
    - ssl_context: SSL context object.
    - mock_accept_connections: Mock accept_connections function for testing.
    """
    while True:
        client_socket, address = server_socket.accept()
        if ssl_context is not None:
            client_socket = ssl_context.wrap_socket(
                client_socket, server_side=True)
        if mock_accept_connections is not None:
            mock_accept_connections(client_socket, address)
        else:
            client_thread = threading.Thread(
                target=handle_client, args=(client_socket, address)
            )
            client_thread.start()


if __name__ == "__main__":
    start_server()
