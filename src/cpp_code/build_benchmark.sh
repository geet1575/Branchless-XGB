#!/bin/bash
# Build Google Benchmark library

set -e

if [ ! -d "benchmark" ]; then
    git clone https://github.com/google/benchmark.git
    cd benchmark
else
    cd benchmark
fi

cmake -E make_directory "build"
cmake -E chdir "build" cmake -DBENCHMARK_DOWNLOAD_DEPENDENCIES=on -DCMAKE_BUILD_TYPE=Release ../
cmake --build "build" --config Release

echo "Google Benchmark built successfully!"