#!/bin/bash

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
