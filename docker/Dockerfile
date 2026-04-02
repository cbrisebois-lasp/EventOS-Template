FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

# Build essentials
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    gcc \
    g++ \
    gdb \
    lcov \
    gawk \
    python3 \
    python3-pip \
    git \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
ARG USERNAME=user
RUN useradd -m ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER ${USERNAME}
ARG PROJECT_DIR=project
WORKDIR /home/${USERNAME}/${PROJECT_DIR}

ENTRYPOINT ["sleep", "infinity"]
