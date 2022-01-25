#!/bin/sh

run_tests() {
  cd root/provider_backend || exit 1
  PYTHONDONTWRITEBYTECODE=1 pytest -v -rxXs --color=yes test/tests/
  test_code=$?
  echo -n "pytest result: " && echo "$test_code"
  return $test_code
}

run_tests || exit $?
