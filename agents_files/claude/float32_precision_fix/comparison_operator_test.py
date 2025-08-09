#!/usr/bin/env python3

import numpy as np
import json
import xgboost as xgb
from src.generate_random_xgb import train_random_xgb

def test_comparison_operators():
    """
    Test if XGBoost uses different comparison logic than standard Python '<'
    Focus on the exact values from the failing case.
    """
    print("🔍 COMPARISON OPERATOR PRECISION TEST")
    print("=" * 50)
    
    # The exact values from our failing case
    feature_val = 0.558854087990882
    split_cond = 0.558854100000000
    
    print(f"Feature value:    {feature_val:.15f}")
    print(f"Split condition:  {split_cond:.15f}")
    print(f"Difference:       {feature_val - split_cond:.20f}")
    
    # Test all comparison operators
    print(f"\\n🧮 PYTHON COMPARISON RESULTS:")
    print(f"feature_val < split_cond:  {feature_val < split_cond}")
    print(f"feature_val <= split_cond: {feature_val <= split_cond}")
    print(f"feature_val == split_cond: {feature_val == split_cond}")
    print(f"feature_val >= split_cond: {feature_val >= split_cond}")
    print(f"feature_val > split_cond:  {feature_val > split_cond}")
    
    # Test with numpy values (as our implementation uses)
    np.random.seed(3)
    test_vector = np.random.rand(18)
    numpy_feature_val = test_vector[17]
    
    print(f"\\n🔢 NUMPY COMPARISON RESULTS:")
    print(f"numpy feature_val:         {numpy_feature_val:.15f}")
    print(f"numpy_val < split_cond:    {numpy_feature_val < split_cond}")
    print(f"numpy_val <= split_cond:   {numpy_feature_val <= split_cond}")
    
    # Test single vs double precision
    feature_float32 = np.float32(feature_val)
    split_float32 = np.float32(split_cond)
    
    print(f"\\n💾 SINGLE PRECISION (FLOAT32) TEST:")
    print(f"feature as float32:        {feature_float32:.15f}")
    print(f"split as float32:          {split_float32:.15f}")
    print(f"float32 comparison <:      {feature_float32 < split_float32}")
    print(f"float32 comparison <=:     {feature_float32 <= split_float32}")
    
    # Test if we can reproduce XGBoost's behavior by changing comparison
    print(f"\\n🔄 ALTERNATIVE COMPARISON TESTS:")
    
    # Maybe XGBoost uses <= instead of <?
    our_logic_lt = numpy_feature_val < split_cond  # What we use
    alt_logic_lte = numpy_feature_val <= split_cond  # Alternative
    alt_logic_gte = numpy_feature_val >= split_cond  # Another alternative
    
    print(f"Our logic (<):             {our_logic_lt}  -> {'LEFT' if our_logic_lt else 'RIGHT'}")
    print(f"Alternative (<=):          {alt_logic_lte} -> {'LEFT' if alt_logic_lte else 'RIGHT'}")
    print(f"Alternative (>=):          {alt_logic_gte} -> {'LEFT' if alt_logic_gte else 'RIGHT'}")
    
    # XGBoost expects RIGHT (leaf 10), our logic gives LEFT (leaf 9)
    xgb_expected = "RIGHT"
    our_result = "LEFT" if our_logic_lt else "RIGHT"
    
    print(f"\\n🎯 COMPARISON SUMMARY:")
    print(f"XGBoost expects:           {xgb_expected}")
    print(f"Our result (<):            {our_result}")
    print(f"Match:                     {xgb_expected == our_result}")
    
    if alt_logic_lte:
        alt_result_lte = "LEFT"
    else:
        alt_result_lte = "RIGHT"
        
    print(f"Alternative result (<=):   {alt_result_lte}")
    print(f"Alt matches XGBoost:       {xgb_expected == alt_result_lte}")
    
    # Test with epsilon tolerance
    epsilon_values = [1e-15, 1e-12, 1e-10, 1e-8, 1e-6]
    print(f"\\n🔬 EPSILON TOLERANCE TESTS:")
    
    for eps in epsilon_values:
        # If difference is smaller than epsilon, maybe XGBoost treats as equal
        diff = abs(numpy_feature_val - split_cond)
        if diff < eps:
            print(f"eps={eps:.0e}: diff < eps, could cause tie-breaking behavior")
        else:
            print(f"eps={eps:.0e}: diff >= eps, normal comparison")
    
    # Create the actual model and test with a tiny modification
    print(f"\\n🧪 EDGE CASE BEHAVIOR TEST:")
    
    # Test values that are clearly on one side vs the other
    clearly_left = split_cond - 0.001   # Clearly less than
    clearly_right = split_cond + 0.001  # Clearly greater than
    
    print(f"Clearly left ({clearly_left:.15f} < {split_cond:.15f}): {clearly_left < split_cond}")
    print(f"Clearly right ({clearly_right:.15f} < {split_cond:.15f}): {clearly_right < split_cond}")
    
    print(f"\\n📋 HYPOTHESIS:")
    print(f"XGBoost likely has internal precision handling that differs from")
    print(f"standard Python float comparisons, possibly:")
    print(f"1. Using different floating-point precision (float32 vs float64)")
    print(f"2. Having tie-breaking rules for extremely close values")
    print(f"3. Using slightly different comparison logic in edge cases")
    print(f"4. Internal representation differences between training and JSON export")

if __name__ == "__main__":
    test_comparison_operators()