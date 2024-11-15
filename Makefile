.PHONY: build install

FILES = tasks.json habits.json lists.json logs.json
DOTS_DIR = ~/.dots

build:
	@pip install -r src/requirements.txt || { echo "error: failed to install dependencies."; exit 1; }
	@if [ "$$(uname)" = "Linux" ]; then \
		pyinstaller --onefile --name=dots-linux src/main.py; \
	elif [ "$$(uname)" = "Darwin" ]; then \
		pyinstaller --onefile --name=dots-macos src/main.py; \
	elif [ "$$(uname | grep MINGW)" ]; then \
		pyinstaller --onefile --name=dots-windows.exe src/main.py; \
	else \
		echo "error: unsupported operating system."; exit 1; \
	fi || { echo "error: pyinstaller failed to build the project."; exit 1; }
	@echo "build successful. executable is located in the dist/ directory."

install:
	@echo "updating and installing dots..."
	@read -p "Enter tag or branch to checkout (default: latest stable): " ref; \
	ref=$${ref:-`git describe --tags $(git rev-list --tags --max-count=1)`}; \
	git fetch --tags || { echo "error: failed to fetch tags."; exit 1; } \
	&& git checkout $$ref || { echo "error: failed to checkout $$ref."; exit 1; }

	@$(MAKE) build

	@if [ ! -f dist/dots-linux ] && [ ! -f dist/dots-macos ] && [ ! -f dist/dots-windows.exe ]; then \
		echo "error: no build artifact found. please build the project first."; exit 1; \
	fi
	@if [ "$$(uname)" = "Linux" ]; then \
		sudo cp dist/dots-linux /usr/local/bin/dots; \
	elif [ "$$(uname)" = "Darwin" ]; then \
		sudo cp dist/dots-macos /usr/local/bin/dots; \
	elif [ "$$(uname | grep MINGW)" ]; then \
		cp dist/dots-windows.exe /c/Windows/System32/dots.exe; \
	else \
		echo "error: unsupported operating system."; exit 1; \
	fi || { echo "error: failed to copy executable. check permissions."; exit 1; }

	@mkdir -p $(DOTS_DIR) || { echo "error: failed to create $(DOTS_DIR)."; exit 1; }
	@if [ ! -f $(DOTS_DIR)/config.toml ]; then \
		cp src/config.toml $(DOTS_DIR)/config.toml || { echo "error: failed to copy config.toml."; exit 1; }; \
	else \
		echo "warning: $(DOTS_DIR)/config.toml already exists. skipping..."; \
	fi
	@for file in $(FILES); do \
		if [ ! -f $(DOTS_DIR)/$$file ]; then \
			echo "{}" > $(DOTS_DIR)/$$file || { echo "error: failed to create $$file."; exit 1; }; \
		else \
			echo "warning: $(DOTS_DIR)/$$file already exists. skipping..."; \
		fi; \
	done
	@echo "dots installed successfully."
