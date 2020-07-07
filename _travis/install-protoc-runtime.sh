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
echo "Attempting download from https://github.com/protocolbuffers/protobuf/releases/download/v3.6.1/protobuf-cpp-3.6.1.zip"
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.6.1/protobuf-cpp-3.6.1.zip
unzip protobuf-cpp-3.6.1.zip
cd protobuf-3.6.1
echo "Config"
./configure
make
make check
echo "INSTALL and UPDATE LIBS"
sudo make install
sudo ldconfig
