build:
	@if [ "$$(uname)" = "Linux" ]; then \
		pip install -r src/requirements.txt || { echo "error: failed to install dependencies."; exit 1; } && \
		pyinstaller --onefile --name=dots-linux src/main.py || { echo "error: pyinstaller failed to build the project."; exit 1; }; \
	elif [ "$$(uname)" = "Darwin" ]; then \
		pip install -r src/requirements.txt || { echo "error: failed to install dependencies."; exit 1; } && \
		pyinstaller --onefile --name=dots-macos src/main.py || { echo "error: pyinstaller failed to build the project."; exit 1; }; \
	elif [ "$$(uname | grep MINGW)" ]; then \
		echo "detected windows. running install.ps1 for build and installation."; \
		powershell -ExecutionPolicy Bypass -File install.ps1 -SourcePath "src" || { echo "error: PowerShell script failed."; exit 1; }; \
	else \
		echo "error: unsupported operating system."; exit 1; \
	fi
	@echo "build successful. executable is located in the dist/ directory."

install: build
	@if [ "$$(uname)" != "MINGW" ]; then \
		echo "installing dots..."; \
		if [ -f dist/dots-linux ]; then \
			sudo cp dist/dots-linux /usr/local/bin/dots || { echo "error: you do not have root access. please run with appropriate permissions."; exit 1; }; \
		elif [ -f dist/dots-macos ]; then \
			sudo cp dist/dots-macos /usr/local/bin/dots || { echo "error: you do not have root access. please run with appropriate permissions."; exit 1; }; \
		else \
			echo "error: no build artifact found. please build the project first." && exit 1; \
		fi; \
		# Create ~/.dots directory and configuration files
		mkdir -p ~/.dots || { echo "error: failed to create ~/.dots."; exit 1; }; \
		[ ! -f ~/.dots/config.toml ] && cp src/config.toml ~/.dots/config.toml || echo "warning: ~/.dots/config.toml already exists. skipping..."; \
		[ ! -f ~/.dots/tasks.json ] && echo "{}" > ~/.dots/tasks.json || echo "warning: ~/.dots/tasks.json already exists. skipping..."; \
		[ ! -f ~/.dots/habits.json ] && echo "{}" > ~/.dots/habits.json || echo "warning: ~/.dots/habits.json already exists. skipping..."; \
		[ ! -f ~/.dots/lists.json ] && echo "{}" > ~/.dots/lists.json || echo "warning: ~/.dots/lists.json already exists. skipping..."; \
		[ ! -f ~/.dots/logs.json ] && echo "{}" > ~/.dots/logs.json || echo "warning: ~/.dots/logs.json already exists. skipping..."; \
	fi

	@echo "dots installed successfully."

.PHONY: build install
