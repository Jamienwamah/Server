# Server/Client Application Documentation

## Overview

This Python server application is designed to search for strings in a specified file. 
It provides a simple interface for clients to send search queries, 
and the server responds with whether the string was found or not.

## Functions
search_string_in_file(search_string: str, file_path: str, reread_on_query: bool) -> str
Searches for a string in the specified file.

search_string: The string to search for.
file_path: The path of the file to search in.
reread_on_query: Boolean indicating whether to reread the file on each query.
search_algorithms: Search options can also be specified by user, with a binary_search as default.
Returns a string indicating whether the search string was found or not.

handle_client(conn, addr)
Handles the client connection and processes the search query.

conn: The connection object.
addr: The address of the client.

## Installation Guide

# Install necessary packages
sudo apt-get update
sudo apt-get install -y python3 python3-pip

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required Python packages
pip install -r requirements.txt

# Copy service file to systemd
sudo cp server.service /etc/systemd/system/

# Start and enable the service
sudo systemctl daemon-reload
sudo systemctl start server.service
sudo systemctl enable server.service

# Configuration
The server can be configured using the config.ini file. 
The following parameters can be adjusted:

host: The hostname or IP address the server listens on. Default is 0.0.0.0
port: The port number the server listens on. Default is 44445.
reread_on_query: Whether to reread the file on each query. Default is False.
ssl_enabled: Whether SSL encryption is enabled. Default is False.
certfile: Path to the SSL certificate file. Default is cert.pem.
keyfile: Path to the SSL key file. Default is key.pem.
search_algorithms: The search algorithm to use. Default is binary_search.

## To Test Locally
cd test
# Server
pytest test_server.py

# Client
pytest test_client.py

## To run locally
# Server
python server.py

# Client
python client.py




