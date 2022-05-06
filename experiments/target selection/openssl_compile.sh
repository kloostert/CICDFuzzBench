#!/bin/bash
set -e

cd "/home/ubuntu/targsel/openssl"

make clean

export PATH_TO_LIBFUZZER="/usr/lib/llvm-12/lib/clang/12.0.0/lib/linux/libclang_rt.fuzzer-x86_64.a"

CC=clang-12 ./config enable-fuzz-libfuzzer \
        --with-fuzzer-lib=$PATH_TO_LIBFUZZER \
        -DPEDANTIC enable-asan enable-ubsan no-shared \
        -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION \
        -fsanitize=fuzzer-no-link \
        enable-ec_nistp_64_gcc_128 -fno-sanitize=alignment \
        enable-weak-ssl-ciphers enable-rc5 enable-md2 \
        enable-ssl3 enable-ssl3-method enable-nextprotoneg \
        --debug

LDCMD=clang++-12 make -j8
