#!/bin/bash

echo "Installing dependencies..."

# Update package lists
# sudo apt update

# Install Python 3
echo "Installing Python 3..."
sudo apt install -y python3 python3-pip

# Install Tkinter if not already available
echo "Installing Tkinter..."
sudo apt install -y python3-tk

# Install Pygame using pip
echo "Installing Pygame..."
sudo apt install python3-pygame

echo "All dependencies have been installed successfully!"
