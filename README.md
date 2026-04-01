# EventOS-Template

A template repository for bootstrapping new [EventOS](https://github.com/NAND-Gate-Technologies/EventOS)-based projects.

## Prerequisites

- [EventOS](https://github.com/NAND-Gate-Technologies/EventOS) cloned locally
- [UnitTest](https://github.com/NAND-Gate-Technologies/UnitTest) cloned locally
- Docker and Docker Compose (for containerized builds)
- A cross-compiler for your target platform (optional, for cross-compilation)

## Quick Start

### 1. Clone the repos

```bash
git clone <this-repo-url> my-project
git clone <eventos-repo-url> EventOS
git clone <unittest-repo-url> UnitTest
```

### 2. Configure environment

```bash
cd my-project/docker
cp .env.example .env
```

Edit `docker/.env` to point at your local clones:

```
EVENTOS_PATH=/absolute/path/to/EventOS
UNITTEST_PATH=/absolute/path/to/UnitTest
```

### 3. Start the container

```bash
docker compose -f docker/docker-compose.yaml up -d --build
```

### 4. Build and test

```bash
# Run tests (host compiler, inside container)
docker compose -f docker/docker-compose.yaml exec -u user eventos-app make test

# Build application (requires a toolchain — see below)
docker compose -f docker/docker-compose.yaml exec -u user eventos-app make build
```

## Getting a Cross-Compiler into the Build

The template is compiler-agnostic. You have three options:

### Option 1: Install in the Docker image

Add the toolchain to `docker/Dockerfile`:

```dockerfile
RUN apt-get update && apt-get install -y gcc-riscv64-unknown-elf
```

### Option 2: Mount a local toolchain

Set `TOOLCHAIN_PATH` in `docker/.env` and uncomment the volume mount in `docker/docker-compose.yaml`:

```yaml
volumes:
  - ${TOOLCHAIN_PATH}:/home/user/toolchain
environment:
  - TOOLCHAIN_PATH=/home/user/toolchain
```

Then pass the toolchain file to CMake:

```bash
cmake -DCMAKE_TOOLCHAIN_FILE=cmake/my-toolchain.cmake ..
```

### Option 3: System install (no container)

If building outside Docker, ensure the cross-compiler is on your `$PATH` and pass a toolchain file:

```bash
export EVENTOS_PATH=/path/to/EventOS
export UNITTEST_PATH=/path/to/UnitTest
mkdir build && cd build
cmake -DCMAKE_TOOLCHAIN_FILE=../cmake/my-toolchain.cmake ..
ninja
```

## Project Structure

```
app/
  include/        Your public headers
  source/         Your application sources (auto-discovered)
test/
  include/        Test-specific headers and mock overrides
  source/         Test files (test_<source>.c, mirroring app/source/)
cmake/            Toolchain files
docker/           Container configuration
```

## Writing Your First Service

1. Add headers under `app/include/myservice/`
2. Add sources under `app/source/myservice/`
3. Add tests under `test/source/myservice/test_<source>.c`
4. Run `make test` — the new files are picked up automatically
