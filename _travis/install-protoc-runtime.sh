#!/usr/bin/env bash
protoc_version=$1

wget https://github.com/protocolbuffers/protobuf/archive/v${protoc_version}.zip
unzip v${protoc_version}.zip
cd v${protoc_version}
./configure
make
make install
ldconfig
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION=2
