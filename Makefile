build:
	@pip install -r src/requirements.txt || { echo "error: failed to install dependencies."; exit 1; }
	@if [ "$$(uname)" = "Linux" ]; then \
		pyinstaller --onefile --name=dots-linux src/main.py || { echo "error: pyinstaller failed to build the project."; exit 1; }; \
	elif [ "$$(uname)" = "Darwin" ]; then \
		pyinstaller --onefile --name=dots-macos src/main.py || { echo "error: pyinstaller failed to build the project."; exit 1; }; \
	elif [ "$$(uname | grep MINGW)" ]; then \
		pyinstaller --onefile --name=dots-windows.exe src/main.py || { echo "error: pyinstaller failed to build the project."; exit 1; }; \
	else \
		echo "error: unsupported operating system."; exit 1; \
	fi
	@echo "build successful. executable is located in the dist/ directory."

install: 
	@echo "installing dots..."
	@if [ ! -f dist/dots-linux ] && [ ! -f dist/dots-macos ] && [ ! -f dist/dots-windows.exe ]; then \
		echo "error: no build artifact found. please build the project first." && exit 1; \
	fi
	@if [ "$$(uname)" = "Linux" ]; then \
		sudo cp dist/dots-linux /usr/local/bin/dots || { echo "error: you do not have root access. please run with appropriate permissions."; exit 1; }; \
	elif [ "$$(uname)" = "Darwin" ]; then \
		sudo cp dist/dots-macos /usr/local/bin/dots || { echo "error: you do not have root access. please run with appropriate permissions."; exit 1; }; \
	elif [ "$$(uname | grep MINGW)" ]; then \
		cp dist/dots-windows.exe /c/Windows/System32/dots.exe || { echo "error: failed to copy to System32. please ensure you have administrative rights."; exit 1; }; \
	else \
		echo "error: unsupported operating system."; exit 1; \
	fi
	
	@mkdir -p ~/.dots || { echo "error: failed to create ~/.dots."; exit 1; }
	@if [ ! -f ~/.dots/config.toml ]; then \
		cp src/config.toml ~/.dots/config.toml || { echo "error: failed to move config.toml to ~/.dots/config.toml."; exit 1; }; \
	else \
		echo "warning: ~/.dots/config.toml already exists. skipping..."; \
	fi

	@if [ ! -f ~/.dots/tasks.json ]; then \
			echo "{}" > ~/.dots/tasks.json || { echo "error: failed to create tasks.json in ~/.dots."; exit 1; }; \
	else \
			echo "warning: ~/.dots/tasks.json already exists. skipping..."; \
	fi

	@if [ ! -f ~/.dots/habits.json ]; then \
			echo "{}" > ~/.dots/habits.json || { echo "error: failed to create habits.json in ~/.dots."; exit 1; }; \
	else \
			echo "warning: ~/.dots/habits.json already exists. skipping..."; \
	fi

	@if [ ! -f ~/.dots/lists.json ]; then \
			echo "{}" > ~/.dots/lists.json || { echo "error: failed to create lists.json in ~/.dots."; exit 1; }; \
	else \
			echo "warning: ~/.dots/lists.json already exists. skipping..."; \
	fi

	@if [ ! -f ~/.dots/logs.json ]; then \
			echo "{}" > ~/.dots/logs.json || { echo "error: failed to create logs.json in ~/.dots."; exit 1; }; \
	else \
			echo "warning: ~/.dots/logs.json already exists. skipping..."; \
	fi

	@echo "dots installed successfully."

.PHONY: build install

