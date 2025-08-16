# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Citation Requirements
**ALWAYS cite sources** for technical claims, implementation details, or statements about how libraries/frameworks work. Include:
- GitHub issue links for documented problems
- Official documentation references  
- Source code links when referencing implementation details
- Version numbers when behavior is version-specific

## Code Style Requirements
**Python Import Organization**: ALL imports must be placed at the top of Python files, grouped as follows:
1. Standard library imports
2. Third-party library imports  
3. Local/project imports
Never use imports inside functions or methods unless absolutely necessary for avoiding circular imports.

## Project Overview

BranchLessXGBoost is a Python project that provides tools for reading, parsing, and analyzing XGBoost model trees without using branching logic. The project focuses on converting XGBoost models to a custom tree representation that can be analyzed and visualized.

## Common Commands

### Setup
```bash
bash setup.sh  # Install dependencies (xgboost, numpy, scikit-learn)

# For C code generation capabilities, also install:
pip install treelite tl2cgen  # Required for XGBoost to C conversion
```

### Testing
```bash
bash test_treegen.sh  # Run the main test suite
python3 -m tests.test_treegen  # Alternative way to run tests

# Enhanced testing with configurable parameters
python3 -m tests.test_treegen --num-models 5 --num-arrays 20  # Test 5 models with 20 arrays each
python3 -m tests.test_treegen --num-models 3 --num-arrays 10 --verbose  # Verbose output with debug info
python3 -m tests.test_treegen --help  # Show all available options

# TL2cgen C code generation testing
python3 -m tests.test_tl2cgen  # Test XGBoost to C conversion and validation
python3 -m tests.test_tl2cgen --num-features 10 --num-samples 200 --verbose  # Custom parameters
```

### Model Generation and Analysis
```bash
# Generate a random XGBoost model with custom parameters
python3 src/generate_random_xgb.py --num-features 10 --n_estimators 1 --max_depth 3

# Generate test data and XGBoost outputs for benchmarking
python3 src/generate_random_xgb.py --num-features 10 --num-samples 100
# This creates data/inputs.csv (100 samples × 10 features) and data/xgboost_outputs.csv (XGBoost predictions)

# Parse and analyze the generated model
python3 src/generate_code.py

# Compare custom implementation with XGBoost's native predictions
python3 tests/test_treegen.py
```

### C Code Generation with TL2cgen
```bash
# Convert XGBoost JSON model to optimized C code
python3 src/xgb_to_c_converter.py  # Uses default input/output paths

# Specify custom input and output
python3 src/xgb_to_c_converter.py --input path/to/model.json --output ./c_code --libname my_predictor

# Test the generated C library (requires compilation first)
python3 src/xgb_to_c_converter.py --test

# Build the generated C code (after conversion)
cd c_output/xgb_predictor_src
mkdir build && cd build
cmake .. && make -j$(nproc)
```

### C++ Branchless Implementation Testing
```bash
# Build and test the custom C++ implementations (naive vs branchless)
cd src/cpp_code

# Build naive implementation
make naive
./predictor_naive  # Outputs to data/naive_outputs.csv

# Build branchless implementation  
make branchless
./predictor_branchless  # Outputs to data/branchless_outputs.csv

# Build and test both implementations
make all
make test  # Runs both variants and compares outputs
```

### Comprehensive End-to-End Testing
```bash
# Run comprehensive tests that validate the complete pipeline
python3 tests/test_codegen.py --num-tests 10  # Test 10 random models

# Customizable test parameters
python3 tests/test_codegen.py \
  --num-tests 5 \
  --min-features 3 --max-features 8 \
  --min-trees 1 --max-trees 5 \
  --min-depth 1 --max-depth 4 \
  --min-samples 50 --max-samples 200 \
  --verbose

# Quick validation with smaller models
python3 tests/test_codegen.py --num-tests 3 --max-trees 3 --max-depth 2

# Help and all available options
python3 tests/test_codegen.py --help
```

### Benchmark Dataset Generation
```bash
# Generate large datasets for performance benchmarking
bash generate_benchmark_data.sh  # Creates 100,000 samples with default settings

# The script automatically:
# - Generates XGBoost model with 10 features and 5 trees
# - Creates 100,000 test samples in data/inputs.csv
# - Generates reference predictions in data/xgboost_outputs.csv
# - Builds C++ prediction code for benchmarking
```

## Code Architecture

### Core Components

1. **Node Class** (`src/xgboost_reader.py`): Represents individual tree nodes with attributes for splits, children, and path tracking. Each node stores whether it represents a "yes" or "no" path from its parent.

2. **Tree Class** (`src/xgboost_reader.py`): Represents complete decision trees with methods for:
   - Building tree structure from XGBoost JSON data
   - Visual tree printing with explicit yes/no paths
   - Custom prediction logic that traverses nodes without branching

3. **Model Generation** (`src/generate_random_xgb.py`): Creates synthetic XGBoost regressors with configurable parameters for testing and analysis.

4. **Tree Parser** (`src/generate_code.py`): Demonstrates how to load XGBoost JSON models and convert them to the custom tree representation.

5. **C Code Generator** (`src/xgb_to_c_converter.py`): Converts XGBoost JSON models to optimized C code using TL2cgen for deployment without Python dependencies.

6. **C++ Implementation Testing** (`src/cpp_code/`): Contains main.cpp, Makefile, and prediction functions for benchmarking naive vs branchless approaches.

7. **End-to-End Test Framework** (`tests/test_codegen.py`): Comprehensive testing system that validates the complete pipeline from model generation to C++ prediction accuracy.

### Key Features

- **Branch-less Design**: The core focus is on representing tree logic without traditional if/else branching
- **Path Tracking**: Each node maintains explicit "yes"/"no" path information from its parent
- **JSON Integration**: Direct parsing of XGBoost's native JSON model format
- **Prediction Validation**: Tests compare custom tree predictions against XGBoost's native predictions

### File Structure
- `src/xgboost_reader.py`: Core tree and node classes
- `src/generate_random_xgb.py`: XGBoost model generation utilities with `--num-samples` support
- `src/generate_code.py`: Example usage and model parsing
- `src/cpp_code/`: C++ implementation directory
  - `main.cpp`: Main program that loads CSV data and runs predictions
  - `predict.cpp`: Generated prediction functions (naive and branchless)
  - `Makefile`: Build system for both prediction variants
- `tests/test_treegen.py`: Basic validation tests comparing predictions
- `tests/test_codegen.py`: Comprehensive end-to-end test framework
- `src/random_xgb_regressor.json`: Generated XGBoost model in JSON format
- `src/xgb_to_c_converter.py`: TL2cgen-based converter for generating optimized C code
- `data/`: Directory containing test data and prediction outputs
  - `inputs.csv`: Generated feature vectors for testing
  - `xgboost_outputs.csv`: Reference predictions from XGBoost
  - `naive_outputs.csv`: Predictions from naive C++ implementation
  - `branchless_outputs.csv`: Predictions from branchless C++ implementation

### Testing Strategy

The project validates correctness by comparing predictions between:
1. XGBoost's native `predict()` method
2. Custom tree traversal implementation

#### Enhanced Test Suite Features

- **Configurable Testing**: Use `--num-models` to specify how many random XGBoost models to generate and test
- **Multiple Test Arrays**: Use `--num-arrays` to control how many random feature vectors to test per model (uses seeds 1, 2, 3... for reproducibility)
- **Colorized Logging**: Tests feature color-coded output with different colors for INFO (green), WARNING (yellow), ERROR (red), and DEBUG (cyan)
- **Verbose Mode**: Use `--verbose` or `-v` for detailed debug output showing individual test results
- **Comprehensive Reporting**: Final summary shows total pass/fail statistics across all models and test arrays

Tests use random feature vectors and check for numerical equivalence using `np.isclose()` with default tolerances.

#### Comprehensive End-to-End Testing (`tests/test_codegen.py`)

The comprehensive test framework validates the entire pipeline from XGBoost model generation to C++ prediction accuracy:

**Pipeline Validation:**
1. **Model Generation**: Creates random XGBoost models with configurable parameters
2. **Data Generation**: Generates test datasets using `--num-samples` functionality
3. **Code Generation**: Runs `generate_code.py` to create C++ prediction functions
4. **Compilation**: Builds both naive and branchless C++ variants
5. **Execution**: Runs both predictors on the test data
6. **Validation**: Compares all three prediction sets (XGBoost, naive C++, branchless C++)

**Key Features:**
- **Randomized Testing**: Each test uses random parameters for features, trees, depth, and samples
- **Accuracy Validation**: Ensures XGBoost ↔ C++ predictions match within tolerance (~1e-5)
- **Implementation Consistency**: Verifies naive and branchless C++ produce identical results
- **Comprehensive Reporting**: Color-coded logging with detailed pass/fail statistics
- **Configurable Parameters**: Full control over test complexity and volume
- **Error Isolation**: Pinpoints failures to specific pipeline stages (generation, compilation, execution, validation)

**Test Parameters:**
- `--num-tests`: Number of random models to test (default: 5)
- `--min/max-features`: Feature count range (default: 3-10)
- `--min/max-trees`: Tree count range (default: 1-10) 
- `--min/max-depth`: Tree depth range (default: 1-5)
- `--min/max-samples`: Sample count range (default: 50-200)
- `--verbose`: Detailed output including individual test results
- `--seed`: Random seed for reproducible test runs

#### Important Implementation Notes

**Learning Rate (eta) in Saved Models**: XGBoost pre-scales leaf values by the learning rate during training and saves the already-scaled values in JSON models. Therefore, when implementing custom tree prediction from saved XGBoost JSON files:

- ✅ **Use eta = 1.0** - leaf values are already scaled  
- ❌ **Don't use the original learning rate** - this would double-scale the values

This was verified through empirical testing: models trained with different learning rates (0.1, 0.3, 1.0) all require eta=1.0 for correct prediction when reading from JSON files.

**Floating Point Precision**: XGBoost has documented precision issues when loading models from JSON format due to internal single-precision float handling:

- **JSON Precision Loss**: "[XGBoost] handles values as single precision floats internally, however when the model is exported as JSON, the values in the child leaf nodes lose precision" ([GitHub Issue #4097](https://github.com/dmlc/xgboost/issues/4097))
- **Split Threshold Issues**: Conversion to JSON "destroyed the information needed to route down the correct path" for thresholds extremely close to feature values ([GitHub Issue #4060](https://github.com/dmlc/xgboost/issues/4060))
- **Recommended Solution**: "The only safe bet is to convert the input data to 32-bit" before processing ([GitHub Issue #4097](https://github.com/dmlc/xgboost/issues/4097))

For exact XGBoost compatibility in edge cases, convert feature values and split conditions to float32 before comparison: `np.float32(feature_val) < np.float32(split_condition)`.

## TL2cgen Integration

### Overview

TL2cgen (TreeLite 2 C GENerator) is a model compiler that converts decision tree models into optimized C code ([TL2cgen Documentation](https://tl2cgen.readthedocs.io/)). This project includes `src/xgb_to_c_converter.py` which uses TL2cgen to convert XGBoost JSON models to deployable C libraries.

### Key Benefits

- **Performance**: Generated C code provides faster inference than Python-based predictions
- **Deployment**: No Python runtime dependencies required for inference
- **Cross-platform**: Generated code compiles on Linux, macOS, and Windows
- **Parallelization**: Supports multi-threaded prediction out of the box

### Architecture

TL2cgen works in conjunction with Treelite ([Treelite Migration Guide](https://tl2cgen.readthedocs.io/en/latest/treelite-migration.html)):

1. **Treelite**: Loads and serializes XGBoost JSON models into memory
2. **TL2cgen**: Compiles the loaded models into optimized C source code
3. **CMake/Make**: Builds the generated C code into shared libraries

### Dependencies

- `treelite`: Model loading and serialization ([GitHub](https://github.com/dmlc/treelite))
- `tl2cgen`: C code generation ([GitHub](https://github.com/dmlc/tl2cgen))

```bash
pip install treelite tl2cgen
```

### Generated Code Structure

The conversion process creates:

- **C source files**: Optimized prediction logic
- **Header files**: API definitions for integration
- **CMakeLists.txt**: CMake build configuration
- **Makefile**: Alternative build system
- **BUILD_INSTRUCTIONS.md**: Compilation guide

### API Migration Notes

TL2cgen represents a major architectural change from Treelite 3.x:

- **Model Loading**: Still use Treelite (`treelite.Model.load()`)
- **Code Generation**: Use TL2cgen (`tl2cgen.export_srcpkg()`)
- **Prediction**: Use `tl2cgen.Predictor()` instead of `treelite_runtime.Predictor()`
- **Data Matrix**: Use `tl2cgen.DMatrix()` instead of `treelite_runtime.DMatrix()`

### Performance Characteristics

Generated C code optimizations include:

- **Vectorized Operations**: SIMD instructions where applicable
- **Memory Layout**: Cache-friendly data structures
- **Parallel Compilation**: Multi-threaded model compilation
- **Branch Prediction**: Optimized conditional logic