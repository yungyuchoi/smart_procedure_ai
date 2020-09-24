SPA_BIN=$(dirname "$0")
SPA_ROOT=$(dirname "${SPA_BIN}")

docker-compose -f ${SPA_ROOT}/postgres/docker-compose.yaml up -d