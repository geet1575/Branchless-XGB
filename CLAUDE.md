# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BranchLessXGBoost is a Python project that provides tools for reading, parsing, and analyzing XGBoost model trees without using branching logic. The project focuses on converting XGBoost models to a custom tree representation that can be analyzed and visualized.

## Common Commands

### Setup
```bash
bash setup.sh  # Install dependencies (xgboost, numpy, scikit-learn)
```

### Testing
```bash
bash test_treegen.sh  # Run the main test suite
python3 -m tests.test_treegen  # Alternative way to run tests
```

### Model Generation and Analysis
```bash
# Generate a random XGBoost model with custom parameters
python3 src/generate_random_xgb.py --num-features 10 --n_estimators 1 --max_depth 3

# Parse and analyze the generated model
python3 src/generate_code.py

# Compare custom implementation with XGBoost's native predictions
python3 tests/test_treegen.py
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

### Key Features

- **Branch-less Design**: The core focus is on representing tree logic without traditional if/else branching
- **Path Tracking**: Each node maintains explicit "yes"/"no" path information from its parent
- **JSON Integration**: Direct parsing of XGBoost's native JSON model format
- **Prediction Validation**: Tests compare custom tree predictions against XGBoost's native predictions

### File Structure
- `src/xgboost_reader.py`: Core tree and node classes
- `src/generate_random_xgb.py`: XGBoost model generation utilities
- `src/generate_code.py`: Example usage and model parsing
- `tests/test_treegen.py`: Validation tests comparing predictions
- `src/random_xgb_regressor.json`: Generated XGBoost model in JSON format

### Testing Strategy

The project validates correctness by comparing predictions between:
1. XGBoost's native `predict()` method
2. Custom tree traversal implementation

Tests use random feature vectors and check for numerical equivalence using `np.isclose()`.