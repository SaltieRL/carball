#!/bin/sh -eu
# Check if file is in cache and if so then do not build again
FILE=carball/generated/binaries/protoc
if test -f "$FILE"; then
    echo "$FILE exist in cache exiting build"
    exit 0
fi

# Build protoc
protoc_version=$1
wget https://github.com/protocolbuffers/protobuf/releases/download/v${protoc_version}/protobuf-${protoc_version}.zip
unzip protobuf-${protoc_version}.zip
cd protobuf-${protoc_version}
echo "CONFIGURING PROTOBUF"
./configure
echo "COMPILING and INSTALLING PROTOBUF and SHARED LIBRARIES (.libs)"
make
make check
sudo make install
sudo ldconfig
echo "GETTING PROTOBUF VERSION"
./src/protoc --version
echo "CLEANING UP"
pwd
ls -lh
cd ..
pwd
ls -lh
echo "COPYING PROTOBUF TO NEW DIRECTORY"
cp ./protobuf-${protoc_version}/src/protoc carball/generated/binaries
cd carball/generated/binaries
ls -lh
