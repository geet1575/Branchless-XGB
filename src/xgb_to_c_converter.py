#!/usr/bin/env python3
"""
XGBoost JSON to C Code Converter using TL2cgen

This script converts XGBoost JSON model files to optimized C code using tl2cgen.
The generated C code provides fast inference without requiring Python dependencies.

Usage:
    python3 src/xgb_to_c_converter.py [--input INPUT_FILE] [--output OUTPUT_DIR] [--libname LIBRARY_NAME]

Dependencies:
    - treelite: For loading XGBoost JSON models
    - tl2cgen: For compiling tree models to C code
"""

import argparse
import os
import sys
import tempfile
import zipfile
from pathlib import Path

try:
    import treelite
    import tl2cgen
    import numpy as np
except ImportError as e:
    print(f"Error: Missing required dependency - {e}")
    print("Please install dependencies with: pip install treelite tl2cgen")
    sys.exit(1)


def convert_xgb_to_c(json_file_path, output_dir="./c_output", libname="xgb_predictor"):
    """
    Convert XGBoost JSON model to C code using tl2cgen.
    
    Args:
        json_file_path (str): Path to XGBoost JSON model file
        output_dir (str): Directory to save generated C code
        libname (str): Name for the generated library
        
    Returns:
        tuple: (success, message, generated_files)
    """
    try:
        # Check if input file exists
        if not os.path.exists(json_file_path):
            return False, f"Input file not found: {json_file_path}", []
        
        print(f"Loading XGBoost model from: {json_file_path}")
        
        # Load the XGBoost JSON model using treelite
        # Use new frontend API to avoid deprecation warning
        try:
            from treelite import frontend
            model = frontend.load_xgboost_model(json_file_path)
        except ImportError:
            # Fallback for older treelite versions
            model = treelite.Model.load(json_file_path, model_format="xgboost_json")
        
        print(f"Model loaded successfully:")
        print(f"  - Number of trees: {model.num_tree}")
        print(f"  - Number of features: {model.num_feature}")
        
        # Get number of classes if available (newer treelite versions may not have this)
        try:
            num_classes = model.num_class
            print(f"  - Number of classes: {num_classes}")
        except AttributeError:
            print(f"  - Model type: Regression (no num_class attribute)")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate C source package
        pkg_path = output_path / f"{libname}_src.zip"
        print(f"Generating C source package: {pkg_path}")
        
        tl2cgen.export_srcpkg(
            model=model,
            toolchain="cmake",
            pkgpath=str(pkg_path),
            libname=libname,
            params={"parallel_comp": model.num_tree}  # Enable parallel compilation
        )
        
        # Extract the generated source package
        extract_dir = output_path / f"{libname}_src"
        with zipfile.ZipFile(pkg_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # List generated files
        generated_files = []
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, extract_dir)
                generated_files.append(rel_path)
        
        print(f"\nC source package generated successfully in: {extract_dir}")
        print("Generated files:")
        for file in sorted(generated_files):
            print(f"  - {file}")
        
        # Generate compilation instructions
        instructions_file = output_path / "BUILD_INSTRUCTIONS.md"
        with open(instructions_file, 'w') as f:
            f.write(f"""# Build Instructions for {libname}

## Prerequisites
- CMake (version 3.12 or higher)
- C/C++ compiler (GCC, Clang, or MSVC)

## Build Steps

### Option 1: Using CMake (Recommended)
```bash
cd {libname}_src
mkdir build
cd build
cmake ..
make -j$(nproc)
```

### Option 2: Using provided Makefile
```bash
cd {libname}_src
make
```

## Generated Library
The build process will create:
- `lib{libname}.so` (Linux/macOS) or `{libname}.dll` (Windows)
- Header files for C/C++ integration

## Usage Example (C++)
```cpp
#include "predictor.h"

// Load the library and make predictions
// See header files for complete API documentation
```

## Performance Notes
- The generated C code is optimized for fast inference
- Supports parallel prediction on multiple threads
- No Python dependencies required for inference
""")
        
        return True, f"Conversion completed successfully", generated_files
        
    except Exception as e:
        return False, f"Conversion failed: {str(e)}", []


def demonstrate_usage(json_file_path, output_dir, libname):
    """
    Demonstrate how to use the generated C library for predictions.
    """
    try:
        # Load original model for comparison
        try:
            from treelite import frontend
            model = frontend.load_xgboost_model(json_file_path)
        except ImportError:
            model = treelite.Model.load(json_file_path, model_format="xgboost_json")
        
        # Try to compile the generated library
        lib_path = Path(output_dir) / f"{libname}_src" / f"lib{libname}.so"
        
        if lib_path.exists():
            print(f"\nTesting generated library: {lib_path}")
            
            # Load the compiled predictor
            predictor = tl2cgen.Predictor(str(lib_path))
            
            # Create test data
            test_data = np.random.rand(5, model.num_feature).astype(np.float32)
            dmat = tl2cgen.DMatrix(test_data)
            
            # Make predictions
            predictions = predictor.predict(dmat)
            
            print(f"Test predictions shape: {predictions.shape}")
            print(f"Sample predictions: {predictions[:3]}")
            
            return True, "Library test successful"
        else:
            return False, f"Generated library not found at {lib_path}. Please build the C code first."
            
    except Exception as e:
        return False, f"Library test failed: {str(e)}"


def main():
    parser = argparse.ArgumentParser(
        description="Convert XGBoost JSON models to optimized C code using tl2cgen"
    )
    parser.add_argument(
        "--input", "-i",
        default="src/random_xgb_regressor.json",
        help="Path to input XGBoost JSON file (default: src/random_xgb_regressor.json)"
    )
    parser.add_argument(
        "--output", "-o",
        default="./c_output",
        help="Output directory for generated C code (default: ./c_output)"
    )
    parser.add_argument(
        "--libname", "-l",
        default="xgb_predictor",
        help="Name for generated library (default: xgb_predictor)"
    )
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Test the generated library after conversion"
    )
    
    args = parser.parse_args()
    
    # Convert the model
    success, message, files = convert_xgb_to_c(args.input, args.output, args.libname)
    
    if success:
        print(f"\n✅ {message}")
        
        if args.test:
            test_success, test_message = demonstrate_usage(args.input, args.output, args.libname)
            if test_success:
                print(f"✅ {test_message}")
            else:
                print(f"⚠️  {test_message}")
    else:
        print(f"❌ {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()