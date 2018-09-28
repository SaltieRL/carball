#!/bin/sh -eu
protoc_version=$1
if test -z "${protoc_version}"; then
	echo "Usage: .travis/install-protoc.sh protoc-version"
	exit 1
fi
if [ "`$HOME/local/bin/protoc --version 2>/dev/null | cut -d' ' -f 2`" != ${protoc_version} ]; then
	rm -rf $HOME/local/bin $HOME/local/include

	mkdir -p $HOME/tmp $HOME/local
	cd $HOME/tmp
	wget https://github.com/protocolbuffers/protobuf/releases/download/v${protoc_version}/protobuf-${protoc_version}.zip
	unzip protobuf-${protoc_version}.zip
	cd protobuf-${protoc_version}
	make
	make install
fi

echo \$ $HOME/local/bin/protoc --version
$HOME/local/bin/protoc --version