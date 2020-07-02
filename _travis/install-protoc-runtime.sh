#!/usr/bin/env bash
protoc_version=$1

wget https://github.com/protocolbuffers/protobuf/releases/protobuf-cpp-${protoc_version}.zip
unzip protobuf-cpp-${protoc_version}.zip
cd protobuf-cpp-${protoc_version}
./configure
make

# Environment variables should be set _prior_ to installing the protobuf library.
# https://developers.google.com/protocol-buffers/docs/reference/python-generated#cpp_impl
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION=2

# Install the protobuf library.
make install
ldconfig
