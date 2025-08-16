#!/bin/bash

# Generate XGBoost model with 1M samples and create C++ prediction code
echo "Generating XGBoost model with 10,000 samples..."
python3 src/generate_random_xgb.py --num-samples 10000 --random-state 12345 --max-depth 2 --n-estimators 10

echo "Generating C++ prediction code..."
cd src && python3 generate_code.py

echo "Done! Ready for benchmarking."