.PHONY: build install

build:
	@chmod +x ./install/build.sh
	@./install/build.sh || { echo "Build script failed."; exit 1; }

install:
	@chmod +x ./install/install.sh
	@chmod +x ./install/install-no-gum.sh
	@if [ "$(USE_GUM)" != "no" ] && which gum > /dev/null 2>&1; then \
		./install/install.sh; \
	elif [ "$(USE_GUM)" = "no" ]; then \
		echo -e "Skipping gum, running installer without gum."; \
		./install/install-no-gum.sh; \
	else \
		echo -e "gum not found. Install gum for a prettier installer."; \
		./install/install-no-gum.sh; \
	fi
