#!/bin/bash

# Function to compare version strings
compare_versions() {
    # Split version strings into arrays
    IFS='.' read -r -a ver1 <<< "$1"
    IFS='.' read -r -a ver2 <<< "$2"

    # Compare each part of the version (major, minor, patch)
    for i in {0..2}; do
        # If ver1 is greater, return 0
        if [[ ${ver1[$i]} -gt ${ver2[$i]} ]]; then
            return 0
        # If ver2 is greater, return 1
        elif [[ ${ver1[$i]} -lt ${ver2[$i]} ]]; then
            return 1
        fi
    done

    # If all parts are equal, return 2
    return 2
}

# Welcome message
echo -e "welcome to the \x1b[1mdots \x1b[0minstaller!"

# Get the latest stable version
latest_stable_version=$(git tag --sort=-v:refname | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | head -n 1)

# Display the prompt with the default version
echo -e "enter the version or branch to install (default: \x1b[1m$latest_stable_version\x1b[0m):"
read -p "version/branch: " ref

# If no selection is made, use the latest stable version as the default
if [ -z "$ref" ]; then 
    echo "no version/branch entered, using default: $latest_stable_version"
    ref="$latest_stable_version"
fi

# Fetch and checkout the selected ref
git fetch --tags &> /dev/null || { echo "error: failed to fetch tags."; exit 1; }
git checkout "$ref" &> /dev/null || { echo "error: failed to checkout $ref."; exit 1; }

echo -e "fetched and checked out to branch/tag \x1b[1m$ref\x1b[0m!"

# Building executable
echo "building executable..."
./install/build.sh || { echo "error: failed to build the project."; exit 1; }
echo "executable built!"

# Check if the build artifacts exist
if [ ! -f dist/dots-linux ] && [ ! -f dist/dots-macos ] && [ ! -f dist/dots-windows.exe ]; then
  echo "error: no build artifact found. please build the project first."
  exit 1
fi

echo "build artifacts found!"

# Extract PATH directories
PATH_DIRS=$(echo "$PATH" | tr ':' '\n')

# Sort the directories and remove duplicates
PATH_DIRS=$(echo "$PATH_DIRS" | sort | uniq)

# If /usr/local/bin is in the list, remove it and add it to the front
if echo "$PATH_DIRS" | grep -q "^/usr/local/bin$"; then
  PATH_DIRS=$(echo "$PATH_DIRS" | grep -v "^/usr/local/bin$")
  PATH_DIRS="/usr/local/bin"$'\n'"$PATH_DIRS"
fi

# Initialize the variable to store unique, valid, and writable directories
unique_dirs=""

# Loop through the PATH directories
echo "available installation directories:"
while IFS= read -r dir; do
  # If the directory is a symlink, resolve it to the full path
  resolved_dir=$(realpath "$dir" 2>/dev/null || echo "$dir")

  # Skip if it's not a directory or is not writable
  if [ ! -d "$resolved_dir" ] || [ ! -w "$resolved_dir" ]; then
    continue 
  fi

  # Add the resolved directory to the list
  unique_dirs+="$resolved_dir\n"
done <<< "$PATH_DIRS"

# Display available installation directories
echo -e "$unique_dirs"

# Ask user to select the installation directory
read -p "enter the installation directory: " INSTALL_DIR

# If no selection is made or invalid ref
if [ -z "$INSTALL_DIR" ]; then 
  echo "error: no installation directory selected."; exit 1; 
fi

# Installing executable based on OS
if [ "$(uname)" = "Linux" ]; then
  sudo cp dist/dots-linux "$INSTALL_DIR/dots" || { echo "error: failed to copy to $INSTALL_DIR."; exit 1; }
elif [ "$(uname)" = "Darwin" ]; then
  sudo cp dist/dots-macos "$INSTALL_DIR/dots" || { echo "error: failed to copy to $INSTALL_DIR."; exit 1; }
elif [ "$(uname | grep MINGW)" ]; then
  sudo cp dist/dots-windows.exe "$INSTALL_DIR/dots.exe" || { echo "error: failed to copy to $INSTALL_DIR."; exit 1; }
else
  echo "error: unsupported operating system."; exit 1
fi

echo -e "executable installed in \x1b[1m$INSTALL_DIR\x1b[0m!"

# Setting up ~/.dots
DOTS_DIR=~/.dots
FILES="tasks.json habits.json lists.json logs.json"

mkdir -p $DOTS_DIR || { echo "error: failed to create \x1b[1m$DOTS_DIR\x1b[0m"; exit 1; }

if [ ! -f $DOTS_DIR/config.toml ]; then
  cp src/config.toml $DOTS_DIR/config.toml || { echo "error: failed to copy \x1b[1mconfig.toml\x1b[0m."; exit 1; }
else
  echo -e "warning: \x1b[1m$DOTS_DIR/config.toml\x1b[0m already exists. skipping..."
fi

for file in $FILES; do
  if [ ! -f $DOTS_DIR/$file ]; then
    echo "{}" > $DOTS_DIR/$file || { echo "error: failed to create \x1b[1m$file\x1b[0m."; exit 1; }
  else
    echo -e "warning: \x1b[1m$DOTS_DIR/$file\x1b[0m already exists. skipping..."
  fi
done

echo -e "\x1b[1m~/.dots\x1b[0m set up!"

echo -e "dots installed successfully. run \x1b[1mdots\x1b[0m to continue."
