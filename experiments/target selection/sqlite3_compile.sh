#!/bin/bash
set -e

cd "/home/ubuntu/targsel/sqlite3/repo"

./configure --disable-shared --enable-rtree

make clean 
make fuzzcheck
