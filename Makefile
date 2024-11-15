.PHONY: build install

build:
	@chmod +x ./install/build.sh
	@./install/build.sh || { echo "Build script failed."; exit 1; }

install:
	@chmod +x ./install/install.sh
	@./install/install.sh || { echo "Install script failed."; exit 1; }
