build:
	@pip install -r src/requirements.txt || { echo "error: failed to install dependencies."; exit 1; }
	@pyinstaller --onefile --name=dots src/main.py || { echo "error: pyinstaller failed to build the project."; exit 1; }
	@echo "build successful. executable is located at dist/dots."

install: 
	@echo "installing dots to /usr/local/bin..."
	@if [ ! -f dist/dots ]; then \
		echo "error: dist/dots does not exist. please build the project first." && exit 1; \
	fi
	@sudo cp dist/dots /usr/local/bin/dots || { echo "error: you do not have root access. please run with appropriate permissions."; exit 1; }
	@mkdir -p ~/.dots || { echo "error: failed to create ~/.dots."; exit 1; }
	@if [ ! -f ~/.dots/config.toml ]; then \
		cp src/config.toml ~/.dots/config.toml || { echo "error: failed to move config.toml to ~/.config/dots.toml."; exit 1; }; \
	else \
		echo "warning: ~/.config/dots.toml already exists. skipping..."; \
	fi
	@if [ ! -f ~/.dots/tasks.json ]; then \
		echo "{}" > ~/.dots/tasks.json || { echo "error: failed to create tasks.json in ~/.dots."; exit 1; }; \
	else \
		echo "warning: ~/.dots/tasks.json already exists. skipping..."; \
	fi
	@echo "dots installed successfully."

.PHONY: build install
