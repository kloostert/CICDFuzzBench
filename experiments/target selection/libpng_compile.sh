#!/bin/bash
set -e

cd "/home/ubuntu/targsel/libpng"

mkdir -p contrib/oss-fuzz
cp ../libpng_read_fuzzer.cc contrib/oss-fuzz/

sed -i 's/#include <stddef.h>/#include <stdlib.h>\n#include <stddef.h>/g' contrib/oss-fuzz/libpng_read_fuzzer.cc
sed -i 's/#ifdef PNG_IGNORE_ADLER32/#ifdef PNG_IGNORE_ADLER3222/g' contrib/oss-fuzz/libpng_read_fuzzer.cc

CXX="clang++-12"
CXXFLAGS="-g -O0 -fsanitize=fuzzer"
OUT="./"
LDFLAGS="-L./ -g -fsanitize=fuzzer"
LIBS="-lrt -lstdc++"

autoreconf -f -i
./configure --with-libpng-prefix=OSS_FUZZ_
make -j$(nproc) clean
make -j$(nproc) libpng16.la

set +e
$CXX $CXXFLAGS -std=c++11 -I. \
     contrib/oss-fuzz/libpng_read_fuzzer.cc \
     -o $OUT/libpng_read_fuzzer \
     $LDFLAGS .libs/libpng16.a $LIBS -lz
STATUS=$?
set -e

git checkout .

echo Exit code: $STATUS
exit $STATUS
