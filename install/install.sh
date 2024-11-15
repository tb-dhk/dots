#!/bin/bash

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
echo "welcome to the dots installer!"

latest_stable_version=$(git tag --sort=-v:refname | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | head -n 1)

# Build the table rows with version information
table_rows=$'version or branch,type\n'

# Get the tags and branches, and categorize them
for ref in $(git for-each-ref --format='%(refname:short)' refs/heads/ && git tag | sort -r); do
    # Initialize the category based on the ref
    if [[ "$ref" == "main" ]]; then
        category="development for latest release"
    elif [[ "$ref" == *"-"* ]]; then
        category="unstable release"
    elif [[ "$ref" == *"/"* ]] || compare_versions "$ref" "$latest_stable_version" && [ $? -eq 0 ]; then
        category="development branch"
    else
        category="stable release"
    fi
    
    # Add row to table
    table_rows+="$ref,$category\n"
done

# Display the table using gum
ref=$(echo -e "$table_rows" | gum table --height=$(echo -e "$table_rows" | wc -l) --widths=20,50)
ref=$(echo $ref | cut -d',' -f1)

# If no selection is made or invalid ref
if [ -z "$ref" ]; then 
	echo "error: No selection made or invalid reference."; exit 1; 
fi

# Fetch and checkout the selected ref
gum spin --show-error --title "fetching and checking out..." -- \
"
git fetch --tags || { echo "error: failed to fetch tags."; exit 1; }
git checkout $ref || { echo "error: failed to checkout $ref."; exit 1; }
"
echo "fetched and checked out to branch/tag \"$ref\"!"

# Building executable
gum spin --show-error ./install/build.sh --title "building executable..." || { echo "error: failed to build the project."; exit 1; }
echo "executable built!"

# Check if the build artifacts exist
gum spin --show-error --title "checking for build artifacts..." -- \
"
if [ ! -f dist/dots-linux ] && [ ! -f dist/dots-macos ] && [ ! -f dist/dots-windows.exe ]; then
  echo \"error: no build artifact found. please build the project first.\";
  exit 1;
fi
"
echo "build artifacts found!"

# Installing executable
gum spin --show-error --title "installing executable..." -- \
"
if [ \"\$(uname)\" = \"Linux\" ]; then
  sudo cp dist/dots-linux /usr/local/bin/dots || { echo \"error: failed to copy to /usr/local/bin.\"; exit 1; }
elif [ \"\$(uname)\" = \"Darwin\" ]; then
  sudo cp dist/dots-macos /usr/local/bin/dots || { echo \"error: failed to copy to /usr/local/bin.\"; exit 1; }
elif [ \"\$(uname | grep MINGW)\" ]; then
  cp dist/dots-windows.exe /c/Windows/System32/dots.exe || { echo \"error: failed to copy to system32.\"; exit 1; }
else
  echo \"error: unsupported operating system.\"; exit 1
fi
"
echo "executable installed"!

# Setting up ~/.dots
DOTS_DIR=~/.dots
FILES="tasks.json habits.json lists.json logs.json"

gum spin --show-error --title "setting up ~/.dots..." -- \
"
mkdir -p \$DOTS_DIR || { echo \"error: failed to create \$DOTS_DIR.\"; exit 1; }

if [ ! -f \$DOTS_DIR/config.toml ]; then
  cp src/config.toml \$DOTS_DIR/config.toml || { echo \"error: failed to copy config.toml.\"; exit 1; }
else
  echo \"warning: \$DOTS_DIR/config.toml already exists. Skipping...\"
fi

for file in \$FILES; do
  if [ ! -f \$DOTS_DIR/\$file ]; then
    echo \"{}\" > \$DOTS_DIR/\$file || { echo \"error: failed to create \$file.\"; exit 1; }
  else
    echo \"warning: \$DOTS_DIR/\$file already exists. skipping...\"
  fi
done
"
echo "~/.dots set up!"

echo "dots installed successfully. type \"dots\" in your terminal to continue."
