# eth-node

A light service that sits ontop of a standard ethereum node and provides helper functions for creating and sending transactions.

## Running

### Requirements

- Python >= 3.5
- Postgresql >= 9.6
- Redis >= 3.0.0
- Parity == 1.8.9

### Setup env

```
virtualenv -p python3 env
env/bin/pip install -r requirements-base.txt
env/bin/pip install -r requirements-development.txt
```

### Running

```
export DATABASE_URL=postgres://<postgres-dsn>
export REDIS_URL=redis://<redis-dsn>
export ETHEREUM_NODE_URL=<jsonrpc-url>
trap 'kill $(jobs -p)' EXIT
env/bin/python -m toshieth &
env/bin/python -m toshieth.monitor &
env/bin/python -m toshieth.manager &
wait
```

## Running on heroku

### Add heroku git

```
heroku git:remote -a <heroku-project-name> -r <remote-name>
```

### Config

NOTE: if you have multiple deploys you need to append
`--app <heroku-project-name>` to all the following commands.

#### Addons

```
heroku addons:create heroku-postgresql:hobby-basic
heroku addons:create heroku-redis:hobby-dev
```

#### Buildpacks

```
heroku buildpacks:add https://github.com/weibeld/heroku-buildpack-run.git
heroku buildpacks:add heroku/python

heroku config:set BUILDPACK_RUN=configure_environment.sh
```

#### Extra Config variables

```
heroku config:set PUSH_URL=<toshi-push-service-url>
heroku config:set PUSH_USERNAME=<toshi-push-service-username>
heroku config:set PUSH_PASSWORD=<toshi-push-service-password>
heroku config:set ETHEREUM_NODE_URL=<jsonrpc-url>
heroku config:set COLLECTIBLE_IMAGE_FORMAT_STRING=<python style format string with {contract_address} and {token_id} fields>
```

Optional:

```
heroku config:set MONITOR_ETHEREUM_NODE_URL=<jsonrpc-url>
heroku config:set SLACK_LOG_URL=<slack-webhook-url>
heroku config:set SLACK_LOG_USERNAME="toshi-eth-log-bot"
```

The `Procfile` and `runtime.txt` files required for running on heroku
are provided.

### Start

```
heroku ps:scale web:1
```

## Tests

### Install external software dependencies

#### Mac OS X

```
brew install postgresql
brew install redis
brew tap ethcore/ethcore
brew install parity --stable
```
Ethminer needs to be installed manually

```
brew install llvm
export CC=/usr/local/opt/llvm/bin/clang
export CXX=/usr/local/opt/llvm/bin/clang++
export CXXFLAGS='-I/usr/local/opt/llvm/include -I/usr/local/opt/llvm/include/c++/v1/'
export CPPFLAGS='-I/usr/local/opt/llvm/include -I/usr/local/opt/llvm/include/c++/v1/'
export LDFLAGS='-L/usr/local/opt/llvm/lib -Wl,-rpath,/usr/local/opt/llvm/lib'
git clone --recursive https://github.com/ethereum/cpp-ethereum.git
cd cpp-ethereum
mkdir build
cd build
cmake ..
cmake --build . --target ethminer
export PATH="$(pwd)/ethminer:$PATH"
ethminer -D 0
```

#### Ubuntu

```
sudo apt-get install postgresql
sudo apt-get install redis-server
```

Parity

download latest stable release from https://github.com/paritytech/parity/releases and run `sudo dpkg -i parity_*.deb`

Ethminer

```
git clone https://github.com/ethereum/cpp-ethereum.git
cd cpp-ethereum/
git checkout 38ac899bf30b87ec76f0e940674046bed952b229
git submodule update --init
./scripts/install_deps.sh
cmake -H. -Bbuild
cd build/ethminer
make
sudo cp ethminer /usr/local/bin/
ethminer -D 0
```

If you get errors like `-Werror=implicit-fallthrough=` and `-Werror=maybe-uninitialized` you have a newer version of gcc than expected and need to patch `cmake/EthCompilerSettings.cmake` with the following and restart from the `cmake -H. -Bbuild` step.

```
diff --git a/cmake/EthCompilerSettings.cmake b/cmake/EthCompilerSettings.cmake
index d6c0347bc..c4e2dd50c 100644
--- a/cmake/EthCompilerSettings.cmake
+++ b/cmake/EthCompilerSettings.cmake
@@ -34,6 +34,9 @@ if (("${CMAKE_CXX_COMPILER_ID}" MATCHES "GNU") OR ("${CMAKE_CXX_COMPILER_ID}" MA

        # Disable warnings about unknown pragmas (which is enabled by -Wall).
        add_compile_options(-Wno-unknown-pragmas)
+       add_compile_options(-Wno-implicit-fallthrough)
+       add_compile_options(-Wno-maybe-uninitialized)
+       add_compile_options(-Wno-deprecated)

        # Configuration-specific compiler settings.
        set(CMAKE_CXX_FLAGS_DEBUG          "-Og -g -DETH_DEBUG")
```

### Running tests

A convinience script exists to run all tests:
```
./run_tests.sh
```

To run a single test, use:

```
env/bin/python -m tornado.testing toshieth.test.<test-package>
```

- - -

Copyright &copy; 2017-2018 Toshi Holdings Pte. Ltd. &lt;[https://www.toshi.org/](https://www.toshi.org/)&gt;

"Toshi" is a registered trade mark. This License does not grant
permission to use the trade names, trademarks, service marks, or
product names of the Licensor.

This program is free software: you can redistribute it and/or modify
it under the terms of the version 3 of the GNU Affero General Public License
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see &lt;[https://www.gnu.org/licenses/](http://www.gnu.org/licenses/)&gt;.
