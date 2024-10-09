build:
	@pyinstaller --onefile --name=dots src/main.py || { echo "error: pyinstaller failed to build the project."; exit 1; }
	@echo "build successful. executable is located at dist/dots."

install: build
	@echo "installing dots to /usr/local/bin..."
	@if [ ! -f dist/dots ]; then \
		echo "error: dist/dots does not exist. please build the project first." && exit 1; \
	fi
	@sudo mv dist/dots /usr/local/bin/dots || { echo "error: you do not have root access. please run with appropriate permissions."; exit 1; }
	@echo "dots installed successfully."

.phony: build install
