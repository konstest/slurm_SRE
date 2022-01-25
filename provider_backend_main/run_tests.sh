#!/bin/sh

test_start() {
    docker build -f test/docker/Dockerfile -t test:local --pull .

    docker run --rm \
        -e PYTEST_ADDOPTS="-v -rxXs --color=yes" \
        --name provider_backend_test \
        --network provider_backend_test_net \
        test:local
    return $?
}

test_start || exit $?