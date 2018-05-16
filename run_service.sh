#!/bin/bash
set -euo pipefail

IFS=$'\n\t'
if [ ! -d 'env' ]; then
    echo "setting up virtualenv"
    python3 -m virtualenv env
fi
if [ -e requirements-base.txt ]; then
    env/bin/pip -q install -r requirements-base.txt
fi
if [ -e requirements-development.txt ]; then
    env/bin/pip -q install -r requirements-development.txt
fi

DBNAME=toshieth_dev
if [[ $(psql -d postgres -c "SELECT datname from pg_database WHERE datname='$DBNAME'" | grep $DBNAME) ]]; then
  echo "$DBNAME exists"
else
  echo "$DBNAME does not exists"
  createdb $DBNAME
fi

export DATABASE_URL=postgresql://$(whoami):@localhost:5432/toshieth_dev
export REDIS_URL=redis://127.0.0.1:6379
export ETHEREUM_NODE_URL=http://159.89.204.101:8545
# export ETHEREUM_NETWORK_ID=1
export PGSQL_SSL_DISABLED=1

env/bin/python -m toshieth --port=3100
