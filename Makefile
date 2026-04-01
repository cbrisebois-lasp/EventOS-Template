BUILD_DIR := build
CMAKE_GENERATOR := Ninja

.PHONY: build test coverage clean help

build:
	@echo "Building..."
	@mkdir -p $(BUILD_DIR)
	@cd $(BUILD_DIR) && cmake .. -G $(CMAKE_GENERATOR) \
		-DCMAKE_VERBOSE_MAKEFILE=OFF
	@cd $(BUILD_DIR) && ninja

test:
	@$(MAKE) -C test all

coverage:
	@$(MAKE) -C test coverage

clean:
	@rm -rf $(BUILD_DIR)
	@rm -rf test/$(BUILD_DIR)
	@echo "Cleaned build directories"

help:
	@echo "Usage:"
	@echo "  make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build      Build the application"
	@echo "  test       Build and run unit tests"
	@echo "  coverage   Build with coverage and generate HTML report"
	@echo "  clean      Remove build directories"
	@echo "  help       Show this help message"
	@echo ""
	@echo "Environment variables:"
	@echo "  EVENTOS_PATH    Path to EventOS clone (required)"
	@echo "  UNITTEST_PATH   Path to UnitTest clone (required)"
	@echo "  TOOLCHAIN_PATH  Path to cross-compiler install (optional)"
