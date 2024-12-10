.PHONY: build install

build:
	@chmod +x ./install/build.sh
	@./install/build.sh || { echo "Build script failed."; exit 1; }

install:
	@chmod +x ./install/install.sh
	@chmod +x ./install/install-no-gum.sh
	@if [ "$(findstring --no-gum, $(MAKECMDGOALS))" ]; then \
		echo -e "skipping \x1b[1mgum\x1b[0m, running installer without \x1b[1mgum\x1b[0m."; \
		./install/install-no-gum.sh; \
	elif which gum > /dev/null 2>&1; then \
		./install/install.sh; \
	else \
		echo -e "\x1b[1mgum\x1b[0m not found. install \x1b[1mgum\x1b[0m for a prettier installer."; \
		./install/install-no-gum.sh; \
	fi
