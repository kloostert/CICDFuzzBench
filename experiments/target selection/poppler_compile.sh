#!/bin/bash
set -e

cd "/home/ubuntu/targsel/poppler"

sed -i 's/(win32|fontconfig)/(win32|generic|fontconfig)/g' poppler/CMakeLists.txt
sed -i 's/set(_default_fontconfiguration "win32")/set(_default_fontconfiguration "win32")\nelseif(ANDROID)\n  set(_default_fontconfiguration "generic")/g' poppler/CMakeLists.txt
sed -i 's/set(WITH_FONTCONFIGURATION_FONTCONFIG ON)/set(WITH_FONTCONFIGURATION_FONTCONFIG ON)\nelseif(font_configuration STREQUAL "generic")\n  message(STATUS "no fontconfig or win32 specific code")/g' poppler/CMakeLists.txt

export WORK="/home/ubuntu/targsel/poppler/work"
rm -rf "$WORK"
mkdir -p "$WORK"
mkdir -p "$WORK/lib" "$WORK/include"

rm -rf ./poppler/freetype2
cp -a freetype2 ./poppler/
pushd "/home/ubuntu/targsel/poppler/poppler/freetype2"
./autogen.sh
./configure --prefix="$WORK" --disable-shared PKG_CONFIG_PATH="$WORK/lib/pkgconfig"
make -j$(nproc) clean
make -j$(nproc)
make install

mkdir -p "$WORK/poppler"
cd "$WORK/poppler"
rm -rf *

EXTRA=""
test -n "$AR" && EXTRA="$EXTRA -DCMAKE_AR=$AR"
test -n "$RANLIB" && EXTRA="$EXTRA -DCMAKE_RANLIB=$RANLIB"

cmake "/home/ubuntu/targsel/poppler/poppler" \
  $EXTRA \
  -DCMAKE_BUILD_TYPE=debug \
  -DBUILD_SHARED_LIBS=OFF \
  -DFONT_CONFIGURATION=generic \
  -DBUILD_GTK_TESTS=OFF \
  -DBUILD_QT5_TESTS=OFF \
  -DBUILD_CPP_TESTS=OFF \
  -DENABLE_LIBPNG=ON \
  -DENABLE_LIBTIFF=ON \
  -DENABLE_LIBJPEG=ON \
  -DENABLE_SPLASH=ON \
  -DENABLE_UTILS=ON \
  -DWITH_Cairo=ON \
  -DENABLE_CMS=none \
  -DENABLE_LIBCURL=OFF \
  -DENABLE_GLIB=OFF \
  -DENABLE_GOBJECT_INTROSPECTION=OFF \
  -DENABLE_QT5=OFF \
  -DENABLE_LIBCURL=OFF \
  -DWITH_NSS3=OFF \
  -DFREETYPE_INCLUDE_DIRS="$WORK/include/freetype2" \
  -DFREETYPE_LIBRARY="$WORK/lib/libfreetype.a" \
  -DICONV_LIBRARIES="/usr/lib/x86_64-linux-gnu/libc.so" \
  -DTESTDATADIR="/home/ubuntu/targsel/poppler/test" \
  -DCMAKE_EXE_LINKER_FLAGS_INIT="$LIBS"
make -j$(nproc) poppler poppler-cpp pdfimages pdftoppm
EXTRA=""

cp "$WORK/poppler/utils/"{pdfimages,pdftoppm} "/home/ubuntu/targsel/poppler/"

rm -rf "/home/ubuntu/targsel/poppler/poppler/freetype2"

git -C "/home/ubuntu/targsel/poppler/poppler" checkout .

# clang++-12 $CXXFLAGS -std=c++11 -I"$WORK/poppler/cpp" -I"/home/ubuntu/targsel/poppler/poppler/cpp" \
#     "/home/ubuntu/targsel/poppler/pdf_fuzzer.cc" -o "/home/ubuntu/targsel/poppler/pdf_fuzzer" \
#     "$WORK/poppler/cpp/libpoppler-cpp.a" "$WORK/poppler/libpoppler.a" \
#     "$WORK/lib/libfreetype.a" $LDFLAGS $LIBS -ljpeg -lz \
#     -lopenjp2 -lpng -ltiff -llcms2 -lm -lpthread -pthread
