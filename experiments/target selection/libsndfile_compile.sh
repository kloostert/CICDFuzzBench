#!/bin/bash
set -e

cd "/home/ubuntu/targsel/libsndfile"

# patch -p1 -i "../magma/targets/libsndfile/patches/setup/libsndfile.patch"

./autogen.sh
./configure --disable-shared --enable-ossfuzzers
make -j$(nproc) clean
make -j$(nproc) ossfuzz/sndfile_fuzzer

git checkout .
