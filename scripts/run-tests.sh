#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# output the docker-compose version for debugging
docker-compose --version

env_file=.env
echo "Setting up environment variables from $env_file"
set -o allexport
source "$env_file"
set +o allexport

echo "Starting docker-compose service"
docker-compose up -d

# waits until neo4j is ready by trying to execute a cypher query using the cypher-shell interface
wait_for_neo4j=$(
cat <<'END_HEREDOC'
t=0
until echo "MATCH(n) RETURN COUNT(n);" | cypher-shell -a $NEO_URI -u $NEO_USERNAME -p $NEO_PASSWORD;
do
    if [[ $t -gt 60 ]]; then
        echo "Neo4j not ready after 60 seconds, aborting"
        exit 1
    fi
    t=$((t+1))
    echo -ne "\r"
    echo -ne "Waiting for Neo4j to be ready... ($t s)"
    sleep 1
done
echo -ne "\r"
if [[ $t -gt 0 ]]; then
    echo "Neo4j ready after $t seconds"
else
    echo "Neo4j already up"
fi
END_HEREDOC
)
docker-compose exec -T neo4j bash -c "$wait_for_neo4j"

echo "Running tests"
docker-compose exec -T nlp pip install -e .
docker-compose exec -T nlp coverage run --source=src -m pytest --cov src/soda_data -v tests
docker-compose exec -T nlp coverage lcov -o coverage.lcov
