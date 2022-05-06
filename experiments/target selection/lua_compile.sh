#!/bin/bash
set -e

cd "/home/ubuntu/targsel/lua"

sed -i 's/rcsclean -u//g' makefile

make -j$(nproc) clean
make -j$(nproc) liblua.a
make -j$(nproc) lua

git checkout .
