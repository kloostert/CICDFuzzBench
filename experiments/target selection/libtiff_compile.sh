#!/bin/bash
set -e

cd "/home/ubuntu/targsel/libtiff"

# sed -i 's/add_subdirectory(test)//g' CMakeLists.txt
# sed -i 's/add_subdirectory(contrib)//g' CMakeLists.txt
sed -i 's/#ifdef JBIG_SUPPORT/#ifdef JBIG_SUPPORTTT/g' libtiff/tif_jbig.c
sed -i 's/{ "ISO JBIG",	COMPRESSION_JBIG,	TIFFInitJBIG },//g' libtiff/tif_codec.c

mkdir -p contrib/oss-fuzz
cp ../tiff_read_rgba_fuzzer.cc contrib/oss-fuzz/

CXX="clang++-12"
CXXFLAGS="-g -O0 -fsanitize=fuzzer"
OUT="."
LDFLAGS="-L./ -g -fsanitize=fuzzer"
LIBS="-lrt -lstdc++"

WORK="`pwd`/work"
rm -rf "$WORK"
mkdir -p "$WORK"
mkdir -p "$WORK/lib" "$WORK/include"

./autogen.sh
./configure --disable-shared --prefix="$WORK"
make -j$(nproc) clean
make -j$(nproc)
make install

cp "$WORK/bin/tiffcp" "$OUT/"
$CXX $CXXFLAGS -std=c++11 -I$WORK/include \
    contrib/oss-fuzz/tiff_read_rgba_fuzzer.cc -o $OUT/tiff_read_rgba_fuzzer \
    $WORK/lib/libtiffxx.a $WORK/lib/libtiff.a -lz -ljpeg -Wl,-Bstatic -llzma -Wl,-Bdynamic \
    $LDFLAGS $LIBS

git checkout .
