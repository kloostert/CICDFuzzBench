#!/bin/bash

nohup python3 -u targsel.py php > php.log 2>&1 &
nohup python3 -u targsel.py openssl > openssl.log 2>&1 &

nohup python3 -u targsel.py sqlite3 > sqlite3.log 2>&1 &
nohup python3 -u targsel.py poppler > poppler.log 2>&1 &

nohup python3 -u targsel.py lua > lua.log 2>&1 &
nohup python3 -u targsel.py libxml2 > libxml2.log 2>&1 &
nohup python3 -u targsel.py libsndfile > libsndfile.log 2>&1 &

nohup python3 -u targsel.py libpng > libpng.log 2>&1 &
nohup python3 -u targsel.py libtiff > libtiff.log 2>&1 &
