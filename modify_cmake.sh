#!/bin/bash

echo "Modifying CMakeLists.txt to include CSV predictor executable..."

# Set path to CMakeLists.txt
CMAKE_FILE="c_output_demo/xgb_predictor_src/xgb_predictor/CMakeLists.txt"

# Check if CMakeLists.txt exists
if [ ! -f "$CMAKE_FILE" ]; then
    echo "Error: CMakeLists.txt not found at $CMAKE_FILE"
    exit 1
fi

# Backup original CMakeLists.txt
cp "$CMAKE_FILE" "${CMAKE_FILE}.backup"
echo "Created backup: ${CMAKE_FILE}.backup"

# Create new CMakeLists.txt with executable
cat > "$CMAKE_FILE" << 'EOF'
cmake_minimum_required(VERSION 3.13)
project(mushroom LANGUAGES C CXX)

# Build the original shared library
add_library(xgb_predictor SHARED)
target_sources(xgb_predictor PRIVATE header.h main.c tu0.c tu1.c tu10.c tu11.c tu12.c tu13.c tu14.c tu15.c tu16.c tu17.c tu18.c tu19.c tu2.c tu20.c tu21.c tu22.c tu23.c tu24.c tu25.c tu26.c tu27.c tu28.c tu29.c tu3.c tu30.c tu31.c tu32.c tu33.c tu34.c tu35.c tu36.c tu37.c tu38.c tu39.c tu4.c tu40.c tu41.c tu42.c tu43.c tu44.c tu45.c tu46.c tu47.c tu48.c tu49.c tu5.c tu6.c tu7.c tu8.c tu9.c)
target_compile_options(xgb_predictor PRIVATE )
target_include_directories(xgb_predictor PRIVATE "${PROJECT_BINARY_DIR}")
set_target_properties(xgb_predictor PROPERTIES
POSITION_INDEPENDENT_CODE ON
            C_STANDARD 99
            C_STANDARD_REQUIRED ON
            PREFIX ""
            RUNTIME_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}"
            RUNTIME_OUTPUT_DIRECTORY_DEBUG "${PROJECT_BINARY_DIR}"
            RUNTIME_OUTPUT_DIRECTORY_RELEASE "${PROJECT_BINARY_DIR}"
            RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PROJECT_BINARY_DIR}"
            RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${PROJECT_BINARY_DIR}"
            LIBRARY_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}"
            LIBRARY_OUTPUT_DIRECTORY_DEBUG "${PROJECT_BINARY_DIR}"
            LIBRARY_OUTPUT_DIRECTORY_RELEASE "${PROJECT_BINARY_DIR}"
            LIBRARY_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PROJECT_BINARY_DIR}"
            LIBRARY_OUTPUT_DIRECTORY_MINSIZEREL "${PROJECT_BINARY_DIR}")

# Build the CSV predictor executable
add_executable(csv_predictor)
target_sources(csv_predictor PRIVATE 
    ../../../src/tl2cgen_main.cpp
    header.h main.c tu0.c tu1.c tu10.c tu11.c tu12.c tu13.c tu14.c tu15.c tu16.c tu17.c tu18.c tu19.c tu2.c tu20.c tu21.c tu22.c tu23.c tu24.c tu25.c tu26.c tu27.c tu28.c tu29.c tu3.c tu30.c tu31.c tu32.c tu33.c tu34.c tu35.c tu36.c tu37.c tu38.c tu39.c tu4.c tu40.c tu41.c tu42.c tu43.c tu44.c tu45.c tu46.c tu47.c tu48.c tu49.c tu5.c tu6.c tu7.c tu8.c tu9.c)

target_include_directories(csv_predictor PRIVATE "${PROJECT_BINARY_DIR}")
set_target_properties(csv_predictor PROPERTIES
            C_STANDARD 99
            C_STANDARD_REQUIRED ON
            CXX_STANDARD 11
            CXX_STANDARD_REQUIRED ON
            RUNTIME_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}"
            RUNTIME_OUTPUT_DIRECTORY_DEBUG "${PROJECT_BINARY_DIR}"
            RUNTIME_OUTPUT_DIRECTORY_RELEASE "${PROJECT_BINARY_DIR}"
            RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PROJECT_BINARY_DIR}"
            RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${PROJECT_BINARY_DIR}")
EOF

echo "CMakeLists.txt has been modified successfully!"
echo "Added csv_predictor executable target that links with tl2cgen_main.cpp"