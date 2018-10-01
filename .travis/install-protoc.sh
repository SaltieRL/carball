#!/bin/sh -eu
protoc_version=$1
wget https://github.com/protocolbuffers/protobuf/releases/download/v${protoc_version}/protobuf-${protoc_version}.zip
unzip protobuf-${protoc_version}.zip
cd protobuf-${protoc_version}
./configure
make
./src/protoc --version
pwd
ls -lh
cd ..
pwd
ls -lh
cp ./protobuf-${protoc_version}/src/protoc .