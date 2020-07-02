#!/usr/bin/env bash
protoc_version=$1

# Environment variables should be set _prior_ to installing the protobuf library.
# https://developers.google.com/protocol-buffers/docs/reference/python-generated#cpp_impl
echo "Setting environment variables."
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION=2

# Process used from:
# https://github.com/protocolbuffers/protobuf/tree/master/src
apt-get install autoconf automake libtool curl make g++ unzip
wget https://github.com/protocolbuffers/protobuf/releases/protobuf-cpp-${protoc_version}.zip
unzip protobuf-cpp-${protoc_version}.zip
cd protobuf-cpp-${protoc_version}
./configure
make
make check
make install
ldconfig
