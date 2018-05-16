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
if [ -e requirements-testing.txt ]; then
    env/bin/pip -q install -r requirements-testing.txt
fi

export DATABASE_URL=postgresql://$(whoami):@localhost:5432/toshieth_dev
export REDIS_URL=redis://127.0.0.1:6379
export ETHEREUM_NODE_URL=http://159.89.204.101:8545
# export ETHEREUM_NETWORK_ID=1
export PGSQL_SSL_DISABLED=1

env/bin/python -m toshieth
