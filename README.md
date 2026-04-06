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

If EventOS and UnitTest are cloned next to you project, you can skip this step. Only deplay .env if EventOS or UnitTest are maintained at a custom path.

```bash
cd my-project/docker
cp .env.example .env
```

Edit `docker/.env` to point at your clones:

```bash
EVENTOS_PATH=/absolute/path/to/EventOS
UNITTEST_PATH=/absolute/path/to/UnitTest
```

### 3a. Build the container

```bash
cd my-project/docker
./docker_env.sh build
```

### 3b. Use the container

```bash
cd my-project/docker
./docker_env.sh start
./docker_env.sh login
```

Run ```./docker_env.sh help``` to see other CLI operations.

### 4. Build and test

```bash
# Build application with the native (host) compiler
make build

# Build application with a cross-compiler (see "Getting a Cross-Compiler into the Build")
make cross

# Run unit tests (always uses the host compiler)
make test
```

## Getting a Cross-Compiler into the Build

By default, the container uses the host `gcc` for building and testing. To cross-compile for an embedded target, you need to provide a cross-compiler and a CMake toolchain file. There are two approaches — both end with `make cross`.

### Naming the cross target

The cross-compile target defaults to `cross`, but you can rename it by setting the `CROSS_TARGET` environment variable. For example, to use `make RV32IMAF` instead of `make cross`:

```bash
export CROSS_TARGET=RV32IMAF
```

The build output goes to `build-<target>/` (e.g. `build-RV32IMAF/`), keeping it separate from the native `build/` directory.

### Option 1: Install the toolchain in the Docker image

The toolchain is installed once when the image is built and cached in the Docker layer. Anyone who builds the image gets the right compiler automatically.

1. **Add the toolchain to `docker/Dockerfile`.**
   Add a `RUN` command after the existing `apt-get install` block. For example, for ARM Cortex-M:

   ```dockerfile
   RUN apt-get update && apt-get install -y gcc-arm-none-eabi
   ```

   Or for RISC-V:

   ```dockerfile
   RUN apt-get update && apt-get install -y gcc-riscv64-unknown-elf
   ```

   If your toolchain is not available as a package, download and extract it instead:

   ```dockerfile
   RUN wget -qO- https://example.com/my-toolchain.tar.gz | tar xz -C /opt/toolchain
   ENV PATH="/opt/toolchain/bin:${PATH}"
   ```

2. **Rebuild the Docker image.**

   ```bash
   cd docker
   ./docker_env.sh build
   ```

3. **Create `cmake/toolchain.cmake`.**
   Copy the example and customize it for your target:

   ```bash
   cp cmake/toolchain-example.cmake cmake/toolchain.cmake
   ```

   Edit `cmake/toolchain.cmake` to set the correct compiler prefix, architecture, and flags.

4. **Build with `make cross`.**

   ```bash
   make cross
   ```

### Option 2: Mount a pre-compiled toolchain from the host

The toolchain lives on your host machine and is mounted into the container at runtime. This is more flexible — you can swap toolchains without rebuilding the image.

1. **Set `TOOLCHAIN_PATH` in `docker/.env`.**
   Point it at your local toolchain install:

   ```bash
   cd docker
   cp .env.example .env
   ```

   Edit `docker/.env`:

   ```bash
   TOOLCHAIN_PATH=/absolute/path/to/your/toolchain
   ```

2. **Uncomment the toolchain volume mount in `docker/docker-compose.yaml`.**
   Under the `volumes:` section, uncomment:

   ```yaml
   - ${TOOLCHAIN_PATH}:/home/user/toolchain
   ```

   And under the `environment:` section, uncomment:

   ```yaml
   - TOOLCHAIN_PATH=/home/user/toolchain
   ```

3. **Restart the container** to pick up the new mount:

   ```bash
   cd docker
   ./docker_env.sh stop
   ./docker_env.sh start
   ```

4. **Create `cmake/toolchain.cmake`.**
   Copy the example and customize it for your target:

   ```bash
   cp cmake/toolchain-example.cmake cmake/toolchain.cmake
   ```

   Edit `cmake/toolchain.cmake` to set the correct compiler prefix, architecture, and flags. The `TOOLCHAIN_PATH` environment variable will resolve to `/home/user/toolchain` inside the container.

5. **Build with `make cross`.**

   ```bash
   make cross
   ```

## Project Structure

```bash
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
