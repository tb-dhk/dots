#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
pip install -r src/requirements.txt || { echo "Error: Failed to install dependencies."; exit 1; }

# Build the project for different operating systems
echo "Building project..."

if [ "$(uname)" = "Linux" ]; then
	pyinstaller --onefile --name=dots-linux src/main.py
elif [ "$(uname)" = "Darwin" ]; then
	pyinstaller --onefile --name=dots-macos src/main.py
elif [ "$(uname | grep MINGW)" ]; then
	pyinstaller --onefile --name=dots-windows.exe src/main.py
else
	echo "Error: Unsupported operating system."; exit 1
fi

echo "Build successful. Executable is located in the dist/ directory."
