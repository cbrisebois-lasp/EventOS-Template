#!/bin/bash

this_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
export PROJECT_DIR="${PROJECT_DIR:-$(basename "$(cd "${this_dir}/.." && pwd)")}"

set +e

if ! command -v docker &> /dev/null
then
  if command -v podman &> /dev/null
  then
    function docker() {
      podman "$@"
    }
  else
    echo "Neither docker nor podman found!!!"
    exit 1
  fi
fi

set -e

DOCKER_COMPOSE_COMMAND="docker compose"
DOCKER_COMPOSE_CONFIG="${this_dir}/docker-compose.yaml"
export DOCKER_COMPOSE_COMMAND
export DOCKER_COMPOSE_CONFIG
${DOCKER_COMPOSE_COMMAND} version &> /dev/null
if [ "$?" -ne 0 ]; then
  export DOCKER_COMPOSE_COMMAND="docker-compose"
fi

execute () {
  echo "$ $@"
  eval "$@"
}

usage() {
  echo "Usage: $1 [start, stop, login, build, remove]" >&2
  echo "*  start: create and start the container" >&2
  echo "*  stop: stop the running container" >&2
  echo "*  login: login to the container" >&2
  echo "*  build: build the image from the Dockerfile" >&2
  echo "*  remove: remove container, network, and volumes" >&2
  exit 1
}

case $1 in
  start )
    execute "${DOCKER_COMPOSE_COMMAND} -f ${DOCKER_COMPOSE_CONFIG} up -d --build"
    ;;
  stop )
    execute "${DOCKER_COMPOSE_COMMAND} -f ${DOCKER_COMPOSE_CONFIG} stop"
    ;;
  login )
    execute "${DOCKER_COMPOSE_COMMAND} -f ${DOCKER_COMPOSE_CONFIG} exec -it -u user eventos-app bash"
    ;;
  build )
    execute "${DOCKER_COMPOSE_COMMAND} -f ${DOCKER_COMPOSE_CONFIG} build"
    ;;
  remove )
    if [ "$2" == "force" ]
    then
      execute "${DOCKER_COMPOSE_COMMAND} -f ${DOCKER_COMPOSE_CONFIG} down -t 30 -v"
    else
      echo "Are you sure? This removes ALL docker volumes and container data! (1-Yes / 2-No)"
      select yn in "Yes" "No"; do
        case $yn in
          Yes ) execute "${DOCKER_COMPOSE_COMMAND} -f ${DOCKER_COMPOSE_CONFIG} down -t 30 -v"; break;;
          No ) exit;;
        esac
      done
    fi
    ;;
  * )
    usage $0
    ;;
esac
