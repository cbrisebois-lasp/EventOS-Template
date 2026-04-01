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
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER ${USERNAME}
WORKDIR /home/${USERNAME}/project

ENTRYPOINT ["sleep", "infinity"]
