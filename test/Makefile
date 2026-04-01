BUILD_DIR := build
COVERAGE_INFO := $(BUILD_DIR)/coverage.info
COVERAGE_DIR := $(BUILD_DIR)/coverage_report
CMAKE_GENERATOR := Ninja

NO_REPORTS ?= 1

.PHONY: all clean build test coverage help

all: test

build:
	@mkdir -p $(BUILD_DIR)
	@cd $(BUILD_DIR) && cmake .. \
		-G $(CMAKE_GENERATOR) \
		-DCMAKE_VERBOSE_MAKEFILE=OFF \
		-DVERBOSE_CUSTOM=OFF \
		-DNO_REPORTS=$(shell [ "$(NO_REPORTS)" = "1" ] && echo ON || echo OFF)
	@cd $(BUILD_DIR) && ninja

test:
	@$(MAKE) build && cd $(BUILD_DIR) && ctest --output-on-failure

coverage:
	@$(MAKE) test NO_REPORTS=0
	@echo "Capturing coverage data..."
	@lcov --capture --directory $(BUILD_DIR) --output-file $(COVERAGE_INFO)
	@lcov --remove $(COVERAGE_INFO) '*/test_*' --output-file $(COVERAGE_INFO)
	@genhtml $(COVERAGE_INFO) --output-directory $(COVERAGE_DIR)
	@echo "Coverage report available at $(COVERAGE_DIR)/index.html"

clean:
	@rm -rf $(BUILD_DIR)
	@echo "Cleaned build directory"

help:
	@echo "Usage:"
	@echo "  make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  all        Default, runs test"
	@echo "  build      Configure and build tests (no coverage by default)"
	@echo "  test       Build and run tests with CTest"
	@echo "  coverage   Build with coverage and generate HTML report"
	@echo "  clean      Remove build directory"
	@echo "  help       Show this help message"
