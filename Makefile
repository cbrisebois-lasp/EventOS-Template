BUILD_DIR := build
CROSS_TARGET ?= cross
CROSS_BUILD_DIR := build-$(CROSS_TARGET)
CMAKE_GENERATOR := Ninja
TOOLCHAIN_FILE := cmake/toolchain.cmake

.PHONY: build $(CROSS_TARGET) test coverage clean help

build:
	@echo "Building (native)..."
	@mkdir -p $(BUILD_DIR)
	@cd $(BUILD_DIR) && cmake .. -G $(CMAKE_GENERATOR) \
		-DCMAKE_VERBOSE_MAKEFILE=OFF
	@cd $(BUILD_DIR) && ninja

$(CROSS_TARGET):
	@if [ ! -f $(TOOLCHAIN_FILE) ]; then \
		echo "Toolchain file not found: $(TOOLCHAIN_FILE)"; \
	else \
		echo "Building ($(CROSS_TARGET))..." && \
		mkdir -p $(CROSS_BUILD_DIR) && \
		cd $(CROSS_BUILD_DIR) && cmake .. -G $(CMAKE_GENERATOR) \
			-DCMAKE_TOOLCHAIN_FILE=$(TOOLCHAIN_FILE) \
			-DCMAKE_VERBOSE_MAKEFILE=OFF && \
		ninja; \
	fi

test:
	@$(MAKE) -C test all

coverage:
	@$(MAKE) -C test coverage

clean:
	@rm -rf $(BUILD_DIR)
	@rm -rf $(CROSS_BUILD_DIR)
	@rm -rf test/$(BUILD_DIR)
	@echo "Cleaned build directories"

help:
	@echo "Usage:"
	@echo "  make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build      Build the application with the native compiler"
	@printf "  %-11s Build the application with a cross-compiler\n" "$(CROSS_TARGET)"
	@echo "  test       Build and run unit tests"
	@echo "  coverage   Build with coverage and generate HTML report"
	@echo "  clean      Remove build directories"
	@echo "  help       Show this help message"
	@echo ""
	@echo "Environment variables:"
	@echo "  EVENTOS_PATH    Path to EventOS clone (required)"
	@echo "  UNITTEST_PATH   Path to UnitTest clone (required)"
