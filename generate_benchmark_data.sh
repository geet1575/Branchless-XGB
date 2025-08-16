#!/bin/bash

# Generate XGBoost model with 1M samples and create C++ prediction code
echo "Generating XGBoost model with 1,000,000 samples..."
python3 src/generate_random_xgb.py --num-samples 1000000 --random-state 12 --max-depth 5 --n-estimators 100 --num-features 40

echo "Generating C++ prediction code..."
cd src && python3 generate_code.py

echo "Done! Ready for benchmarking."