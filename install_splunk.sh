#!/bin/bash

# Variables
SPLUNK_PACKAGE="splunk-9.3.1-0b8d769cb912.x86_64.rpm"
SPLUNK_HOME="/opt/splunk"
SPLUNK_USER="splunk"

# Update and install necessary dependencies
echo "Updating system and installing dependencies..."
sudo yum update -y
sudo yum install -y wget tar

# Check if the package is available
if [ ! -f "$SPLUNK_PACKAGE" ]; then
    echo "Error: Splunk package $SPLUNK_PACKAGE not found!"
    exit 1
fi

# Create a dedicated user for Splunk
echo "Creating Splunk user..."
sudo useradd -m $SPLUNK_USER

# Install Splunk Enterprise
echo "Installing Splunk..."
sudo rpm -i --prefix="$SPLUNK_HOME" "$SPLUNK_PACKAGE"

# Set permissions for Splunk directory
echo "Setting permissions..."
sudo chown -R $SPLUNK_USER:$SPLUNK_USER $SPLUNK_HOME

# Start Splunk for the first time and accept the license
echo "Starting Splunk for the first time and accepting license..."
sudo -u $SPLUNK_USER $SPLUNK_HOME/bin/splunk start --accept-license --answer-yes --no-prompt

# Enable Splunk to start on boot
echo "Enabling Splunk to start on boot..."
sudo $SPLUNK_HOME/bin/splunk enable boot-start -user $SPLUNK_USER

# Verify installation
echo "Splunk installation complete. Checking status..."
sudo $SPLUNK_HOME/bin/splunk status

echo "Splunk has been successfully installed and started."
