#!/bin/bash

echo "=== TL2cgen CSV Processing Pipeline ==="
echo "This script will:"
echo "1. Generate TL2cgen C code from XGBoost model"
echo "2. Modify CMakeLists.txt to include CSV processor"
echo "3. Build the executable"
echo "4. Process CSV data and generate predictions"
echo ""

# Check prerequisites
if [ ! -f "inputs/inputs.csv" ]; then
    echo "❌ Error: inputs/inputs.csv not found"
    echo "Please ensure input CSV file exists with header: feature_0,feature_1,...,feature_9"
    exit 1
fi

if [ ! -f "src/tl2cgen_main.cpp" ]; then
    echo "❌ Error: src/tl2cgen_main.cpp not found"
    echo "Please ensure the C++ main file exists"
    exit 1
fi

if [ ! -f "modify_cmake.sh" ]; then
    echo "❌ Error: modify_cmake.sh not found"
    echo "Please ensure the CMake modification script exists"
    exit 1
fi

# Step 1: Generate TL2cgen code
echo "🔧 Step 1: Generating TL2cgen C code..."
bash tl2cgen_codegen.sh
if [ $? -ne 0 ]; then
    echo "❌ Error: TL2cgen code generation failed"
    exit 1
fi
echo "✅ TL2cgen code generated successfully"

# Step 2: Modify CMakeLists.txt
echo "🔧 Step 2: Modifying CMakeLists.txt..."
./modify_cmake.sh
if [ $? -ne 0 ]; then
    echo "❌ Error: CMakeLists.txt modification failed"
    exit 1
fi
echo "✅ CMakeLists.txt modified successfully"

# Step 3: Build the project
echo "🔧 Step 3: Building project..."
mkdir -p c_output_demo/xgb_predictor_src/xgb_predictor/build
cd c_output_demo/xgb_predictor_src/xgb_predictor/build

echo "  - Configuring with CMake..."
cmake .. > cmake.log 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Error: CMake configuration failed"
    cat cmake.log
    exit 1
fi

echo "  - Compiling with make..."
make -j$(nproc) > make.log 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Error: Compilation failed"
    cat make.log
    exit 1
fi

# Verify executable was created
if [ ! -f "csv_predictor" ]; then
    echo "❌ Error: csv_predictor executable not found"
    exit 1
fi

echo "✅ Project built successfully"
cd - > /dev/null

# Step 4: Run CSV processing
echo "🔧 Step 4: Processing CSV data..."
EXECUTABLE="c_output_demo/xgb_predictor_src/xgb_predictor/build/csv_predictor"

if [ ! -x "$EXECUTABLE" ]; then
    echo "❌ Error: Executable not found or not executable: $EXECUTABLE"
    exit 1
fi

# Create outputs directory
mkdir -p outputs

# Run the predictor
# ./"$EXECUTABLE"
# if [ $? -ne 0 ]; then
#     echo "❌ Error: CSV processing failed"
#     exit 1
# fi

# # Verify output
# if [ ! -f "outputs/tl2cgen.csv" ]; then
#     echo "❌ Error: Output file not created"
#     exit 1
# fi

# echo "✅ CSV processing completed successfully"

# # Show results summary
# echo ""
# echo "🎉 Pipeline completed successfully!"
# echo ""
# echo "📁 Files created:"
# echo "  - Executable: $EXECUTABLE"
# echo "  - Output:     outputs/tl2cgen.csv"
# echo ""
# echo "📊 Results summary:"
# NUM_PREDICTIONS=$(tail -n +2 outputs/tl2cgen.csv | wc -l)
# echo "  - Total predictions: $NUM_PREDICTIONS"
# echo ""
# echo "First 5 predictions:"
# head -n 6 outputs/tl2cgen.csv
# echo ""
# echo "To run again: ./$EXECUTABLE"