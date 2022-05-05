#!/bin/bash
set -e

# Working direcotry
WD=".."

# Initialize results directory
echo "Initializing results directory..."
mkdir -p "$WD/results/libpng/artificial/0000"
mkdir -p "$WD/results/libsndfile/artificial/0000"
mkdir -p "$WD/results/libtiff/artificial/0000"
mkdir -p "$WD/results/libxml2/artificial/0000"
mkdir -p "$WD/results/lua/artificial/0000"
mkdir -p "$WD/results/openssl/artificial/0000"
mkdir -p "$WD/results/php/artificial/0000"
mkdir -p "$WD/results/poppler/artificial/0000"
mkdir -p "$WD/results/sqlite3/artificial/0000"

# Download seed corpora
echo "Downloading seed corpora..."
git clone https://github.com/HexHive/magma.git "$WD/magma"
git -C "$WD/magma" checkout 2374f74c26b10c70b3dffb3c24f81fee06c59cd4

# Set up target libraries
echo "Setting up target libraries..."
git clone --no-checkout https://github.com/glennrp/libpng.git "$WD/libpng"
git -C "$WD/libpng" checkout a37d4836519517bdce6cb9d956092321eca3e73b

git clone --no-checkout https://github.com/libsndfile/libsndfile.git "$WD/libsndfile"
git -C "$WD/libsndfile" checkout 86c9f9eb7022d186ad4d0689487e7d4f04ce2b29

git clone --no-checkout https://gitlab.com/libtiff/libtiff.git "$WD/libtiff"
git -C "$WD/libtiff" checkout c145a6c14978f73bb484c955eb9f84203efcb12e
cp "$WD/magma/targets/libtiff/src/tiff_read_rgba_fuzzer.cc" "$WD/libtiff/contrib/oss-fuzz/tiff_read_rgba_fuzzer.cc"

git clone --no-checkout https://gitlab.gnome.org/GNOME/libxml2.git "$WD/libxml2"
git -C "$WD/libxml2" checkout ec6e3efb06d7b15cf5a2328fabd3845acea4c815

git clone --no-checkout https://github.com/lua/lua.git "$WD/lua"
git -C "$WD/lua" checkout dbdc74dc5502c2e05e1c1e2ac894943f418c8431

git clone --no-checkout https://github.com/openssl/openssl.git "$WD/openssl"
git -C "$WD/openssl" checkout 3bd5319b5d0df9ecf05c8baba2c401ad8e3ba130

git clone --no-checkout https://github.com/php/php-src.git "$WD/php"
git -C "$WD/php" checkout bc39abe8c3c492e29bc5d60ca58442040bbf063b
git clone --no-checkout https://github.com/kkos/oniguruma.git "$WD/php/oniguruma"
git -C "$WD/php/oniguruma" checkout 227ec0bd690207812793c09ad70024707c405376

git clone --no-checkout https://gitlab.freedesktop.org/poppler/poppler.git "$WD/poppler"
git -C "$WD/poppler" checkout 1d23101ccebe14261c6afc024ea14f29d209e760
git clone --no-checkout git://git.sv.nongnu.org/freetype/freetype2.git "$WD/freetype2"
git -C "$WD/freetype2" checkout 50d0033f7ee600c5f5831b28877353769d1f7d48

curl "https://www.sqlite.org/src/tarball/sqlite.tar.gz?r=8c432642572c8c4b" -o "$WD/sqlite.tar.gz"
mkdir -p "$WD/sqlite3"
tar -C "$WD/sqlite3" --strip-components=1 -xzf "$WD/sqlite.tar.gz"
rm -rf "$WD/sqlite.tar.gz"

# Download fuzzers
echo "Downloading fuzzers..."
git clone --no-checkout https://github.com/AFLplusplus/AFLplusplus "./fuzzers/aflplusplus/repo"
git -C "./fuzzers/aflplusplus/repo" checkout 5ee63a6e6267e448342ccb28cc8d3c0d34ffc1cd

git clone --no-checkout https://github.com/google/honggfuzz.git "./fuzzers/honggfuzz/repo"
git -C "./fuzzers/honggfuzz/repo" checkout 937ccdd9feb5114c4b32e7b03420366ff9a310ec

git clone --no-checkout https://github.com/llvm/llvm-project.git "./fuzzers/libfuzzer/repo"
git -C "./fuzzers/libfuzzer/repo" checkout 3d120b6f7be816d188bd05271fff17f0030db9b2

# Prepare fuzz duration experiment
echo "Preparing fuzz duration experiment..."
cp "./experiments/fuzz duration/common.py" .
cp "./experiments/fuzz duration/fuzz-duration.py" .
cp "./experiments/fuzz duration/run_experiments.sh" "./run_fuzz-duration.sh"

# Inject Magma bugs
echo "Injecting Magma bugs..."
export COMETFUZZ_INJECT_BUGS=1
./run_fuzz-duration.sh
unset COMETFUZZ_INJECT_BUGS
