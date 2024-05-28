"""
Client module to effectively connect to the server.

This client connects to the server, and then sends a,
search query request to the server. The search query,
is in a plain text, representing a single line string,
contained in a file
"""

import socket
import ssl
import sys
import argparse
import configparser

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read("config.ini")

# Extract host and port from the configuration
HOST = config.get("server", "host", fallback="0.0.0.0")
PORT = config.getint("server", "port", fallback=44445)
USE_SSL = config.getboolean("server", "use_ssl", fallback=True)


def send_query(query):
    """
    Send a search query to the server and print the response.

    Parameters:
    - query: The search string to be sent to the server.

    This function handles both SSL and non-SSL connections
    based on the USE_SSL flag.
    """
    try:
        if USE_SSL:
            # Create an SSL context for the client
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = (
                False  # Disable hostname verification for testing purposes
            )
            context.verify_mode = (
                ssl.CERT_NONE
            )  # Disable certificate validation for testing purposes
            with socket.create_connection((HOST, PORT)) as sock:
                # Wrap the socket with SSL
                with context.wrap_socket(sock, server_hostname=HOST) as ssock:
                    ssock.sendall(query.encode())
                    response = ssock.recv(1024).decode()
                    print(response)
        else:
            # Non-SSL connection
            with socket.create_connection((HOST, PORT)) as sock:
                sock.sendall(query.encode())
                response = sock.recv(1024).decode()
                print(response)
    except Exception as e:
        # Print the error and exit if any exception occurs
        print(f"Error: {e}")


def main():
    """
    Main function to parse command-line arguments and send the search query.

    This function uses argparse to handle command-line input.
    """
    parser = argparse.ArgumentParser(
        description="Client script for searching a string on the server."
    )
    parser.add_argument(
        "search_string", type=str, help="String to search for.")
    args = parser.parse_args()
    send_query(args.search_string)


if __name__ == "__main__":
    main()
