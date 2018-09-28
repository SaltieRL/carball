#!/bin/sh
set -ex
wget https://github.com/google/protobuf/releases/download/v2.6.1/protobuf-2.6.1.tar.gz
tar -xzvf protobuf-2.6.1.tar.gz
cd protobuf-2.6.1
sudo apt-get update
sudo apt-get install build-essential
sudo ./configure
sudo make
sudo make check
sudo make install
sudo ldconfig
protoc --version
