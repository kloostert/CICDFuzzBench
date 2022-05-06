#!/bin/bash
set -e

cd "/home/ubuntu/targsel/php"

sed -i 's/php_info_print_table_row(2, "Build Date", __DATE__ " " __TIME__);//g' ext/standard/info.c

make clean

pushd oniguruma
autoreconf -vfi
./configure CC=clang-12 CFLAGS="-fsanitize=fuzzer-no-link,address -O2 -g"
make -j8
popd

export ONIG_CFLAGS="-I$PWD/oniguruma/src"
export ONIG_LIBS="-L$PWD/oniguruma/src/.libs -l:libonig.a"

./buildconf

CC=clang-12 CFLAGS="-Wno-builtin-macro-redefined -D__DATE__=0 -D__TIME__=0 -D__TIMESTAMP__=0" CXX=clang++-12 \
./configure \
    --disable-all \
    --enable-fuzzer \
    --with-pic \
    --enable-debug-assertions \
    --enable-address-sanitizer \
    --enable-exif \
    --enable-mbstring

make -j8

git checkout .
