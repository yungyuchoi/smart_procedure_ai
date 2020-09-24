SPA_BIN=$(dirname "$0")
SPA_ROOT=$(dirname "${SPA_BIN}")

docker cp ${SPA_ROOT}/postgres/intellian_test.dump postgres_container:/var/lib/postgresql/data/
docker exec -i postgres_container pg_restore -U zinnotech -d ai_test /var/lib/postgresql/data/intellian_test.dump