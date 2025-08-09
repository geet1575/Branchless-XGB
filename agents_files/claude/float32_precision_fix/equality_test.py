#!/usr/bin/env python3

import numpy as np

def test_equality():
    """Test the exact equality case"""
    print("🔍 EQUALITY TEST")
    print("=" * 30)
    
    # The exact values from Tree 5
    feature_val = 0.558854
    threshold = 0.558854
    
    print(f"feature_val: {feature_val}")
    print(f"threshold: {threshold}")
    print(f"feature_val == threshold: {feature_val == threshold}")
    print(f"feature_val < threshold: {feature_val < threshold}")
    
    # Test with numpy array (as our code uses)
    np.random.seed(3)
    test_vector = np.random.rand(18)
    feature_val_from_array = test_vector[17]
    
    print(f"\\nFrom numpy array:")
    print(f"test_vector[17]: {feature_val_from_array}")
    print(f"test_vector[17] == threshold: {feature_val_from_array == threshold}")
    print(f"test_vector[17] < threshold: {feature_val_from_array < threshold}")
    
    # Check precision
    print(f"\\nPrecision check:")
    print(f"Difference: {abs(feature_val_from_array - threshold)}")
    print(f"Difference < 1e-15: {abs(feature_val_from_array - threshold) < 1e-15}")
    
    # Test what our prediction logic would do
    if feature_val_from_array < threshold:
        print("\\nOur logic: Go LEFT")
    else:
        print("\\nOur logic: Go RIGHT")

if __name__ == "__main__":
    test_equality()