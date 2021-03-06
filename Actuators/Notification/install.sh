#!/bin/bash

# Install required packages
sudo apt-get update;
sudo apt-get install -y python3;
sudo apt-get install -y python3-pip;
pip3 install --upgrade pip;
pip3 install -r requirements.txt

echo "Requirements downloaded successfully"
