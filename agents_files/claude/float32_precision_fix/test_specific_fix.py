#!/usr/bin/env python3

import numpy as np
import json
import xgboost as xgb
from src.generate_random_xgb import train_random_xgb
from src.xgboost_reader import create_trees_from_json

def test_specific_fix():
    """Test the float32 fix with the exact failing case"""
    print("🧪 TESTING FLOAT32 PRECISION FIX")
    print("=" * 50)
    
    # Reproduce the exact failing scenario
    model_seed = 3
    num_features = 18
    n_estimators = 6
    max_depth = 3
    
    print("Creating model with exact failing parameters:")
    print(f"  seed={model_seed}, features={num_features}, trees={n_estimators}, depth={max_depth}")
    
    model, X, y = train_random_xgb(
        num_features=num_features,
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=model_seed
    )
    
    model_path = "fix_test_model.json"
    model.save_model(model_path)
    
    # Test the specific failing case: test array 3 (seed=3)
    np.random.seed(3)
    test_vector = np.random.rand(num_features)
    
    print(f"\\nTesting with seed=3 test vector (the failing case)")
    
    # XGBoost prediction
    xgb_pred = model.predict(test_vector.reshape(1, -1))[0]
    
    # Our prediction with the float32 fix
    with open(model_path, 'r') as f:
        json_data = json.loads(f.read())
    
    forest = create_trees_from_json(json_data)
    base_score = float(json_data['learner']['learner_model_param']['base_score'])
    
    our_pred = base_score
    for tree in forest:
        our_pred += tree.predict(test_vector)  # Now uses float32 internally
    
    difference = abs(xgb_pred - our_pred)
    
    print(f"\\n📊 RESULTS:")
    print(f"XGBoost prediction:     {xgb_pred:.10f}")
    print(f"Our prediction (fixed): {our_pred:.10f}")
    print(f"Difference:             {difference:.10f}")
    print(f"Relative error:         {100 * difference / xgb_pred:.6f}%")
    
    # Check if it passes with default np.isclose tolerance
    passes_test = np.isclose(xgb_pred, our_pred)
    
    print(f"\\n🎯 TEST RESULT:")
    if passes_test:
        print("✅ PASS: Predictions match within default tolerance")
        print("🎉 Float32 precision fix SUCCESSFUL!")
    else:
        print("❌ FAIL: Still significant difference")
        print("⚠️  Float32 fix may not be sufficient")
    
    # Show the critical Tree 5 comparison
    print(f"\\n🔍 TREE 5 CRITICAL COMPARISON:")
    tree5 = forest[5]
    
    # Get the exact values at the problematic node
    feature_17_val = test_vector[17]
    
    # Find split condition for feature 17 in Tree 5
    tree5_data = json_data['learner']['gradient_booster']['model']['trees'][5]
    node5_split_cond = tree5_data['split_conditions'][5]  # Node 5 uses feature 17
    
    print(f"Feature[17] value:      {feature_17_val:.15f}")
    print(f"Node 5 split condition: {node5_split_cond:.15f}")
    print(f"Difference:             {feature_17_val - node5_split_cond:.15f}")
    
    # Test both float64 and float32 comparisons
    float64_comparison = feature_17_val < node5_split_cond
    float32_comparison = np.float32(feature_17_val) < np.float32(node5_split_cond)
    
    print(f"\\nComparison results:")
    print(f"Float64 (original): {feature_17_val:.15f} < {node5_split_cond:.15f} = {float64_comparison} -> {'LEFT' if float64_comparison else 'RIGHT'}")
    print(f"Float32 (fixed):    {np.float32(feature_17_val):.15f} < {np.float32(node5_split_cond):.15f} = {float32_comparison} -> {'LEFT' if float32_comparison else 'RIGHT'}")
    
    # XGBoost expects RIGHT (leaf 10), let's see what we get now
    booster = xgb.Booster(model_file=model_path)
    leaf_indices = booster.predict(xgb.DMatrix(test_vector.reshape(1, -1)), pred_leaf=True)[0]
    expected_tree5_leaf = int(leaf_indices[5])
    
    print(f"\\nXGBoost expects Tree 5 -> leaf {expected_tree5_leaf}")
    print(f"Our float32 logic -> {'LEFT (leaf 9)' if float32_comparison else 'RIGHT (leaf 10)'}")
    
    if (expected_tree5_leaf == 10 and not float32_comparison) or (expected_tree5_leaf == 9 and float32_comparison):
        print("✅ Tree 5 traversal now matches XGBoost!")
    else:
        print("❌ Tree 5 traversal still differs from XGBoost")
    
    # Clean up
    import os
    os.remove(model_path)

if __name__ == "__main__":
    test_specific_fix()