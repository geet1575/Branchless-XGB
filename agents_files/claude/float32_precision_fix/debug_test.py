#!/usr/bin/env python3

import numpy as np
import json
import xgboost as xgb
from src.generate_random_xgb import train_random_xgb
from src.xgboost_reader import create_trees_from_json

def reproduce_failure():
    """Reproduce the exact failing scenario for RCA"""
    print("🔍 REPRODUCING FAILURE SCENARIO")
    print("=" * 50)
    
    # Reproduce the exact model parameters from the log
    model_seed = 3
    num_features = 18
    n_estimators = 6
    max_depth = 3
    
    print(f"Generating model with: features={num_features}, trees={n_estimators}, depth={max_depth}, seed={model_seed}")
    
    # Generate the same model
    model, X, y = train_random_xgb(
        num_features=num_features,
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=model_seed
    )
    
    # Save model
    model_path = "debug_model.json"
    model.save_model(model_path)
    print(f"Model saved to {model_path}")
    
    # Load and parse the model
    with open(model_path, 'r') as f:
        xgboost_json_string = f.read()
    
    xgboost_model_data = json.loads(xgboost_json_string)
    forest = create_trees_from_json(xgboost_model_data)
    actual_xgb_model = xgb.Booster(model_file=model_path)
    
    print(f"Model loaded successfully - Features: {actual_xgb_model.num_features()}, Trees: {len(forest)}")
    
    # Extract model parameters
    base_score = float(xgboost_model_data['learner']['learner_model_param']['base_score'])
    print(f"Base score: {base_score}")
    
    # Check if learning rate is available in JSON
    try:
        eta = float(xgboost_model_data['learner']['gradient_booster']['gbtree_train_param'].get('learning_rate', 1.0))
        print(f"Learning rate found in JSON: {eta}")
    except:
        eta = 1.0
        print(f"Learning rate not found in JSON, using default: {eta}")
    
    # Test the specific failing case: test array 3 (seed=3)
    print("\n🔍 TESTING FAILING CASE (Test 3 with seed=3)")
    print("-" * 50)
    
    np.random.seed(3)  # This is the failing test case
    random_feature_vector = np.random.rand(num_features)
    print(f"Test vector (first 5 values): {random_feature_vector[:5]}")
    
    # Get XGBoost prediction
    model_output = actual_xgb_model.predict(xgb.DMatrix(random_feature_vector.reshape(1, -1)))[0]
    print(f"XGBoost prediction: {model_output:.6f}")
    
    # Get our custom forest prediction with detailed breakdown
    forest_output = base_score
    print(f"Starting with base_score: {base_score:.6f}")
    
    for i, tree in enumerate(forest):
        tree_output = tree.predict(random_feature_vector)
        forest_output += eta * tree_output
        print(f"Tree {i}: output={tree_output:.6f}, eta*output={eta * tree_output:.6f}, cumulative={forest_output:.6f}")
    
    print(f"\nFinal custom prediction: {forest_output:.6f}")
    print(f"Difference: {abs(model_output - forest_output):.6f}")
    print(f"Relative error: {100 * abs(model_output - forest_output) / model_output:.3f}%")
    
    if np.isclose(model_output, forest_output):
        print("✅ PASS: Predictions match within tolerance")
    else:
        print("❌ FAIL: Significant difference detected")
        
        # Let's inspect the model structure more deeply
        print(f"\n🔍 DETAILED MODEL ANALYSIS")
        print("-" * 50)
        print(f"XGBoost model info:")
        print(f"  - objective: {xgboost_model_data['learner']['objective']['name']}")
        print(f"  - base_score: {base_score}")
        
        # Check gradient booster parameters
        gb_params = xgboost_model_data['learner']['gradient_booster']
        print(f"  - booster: {gb_params['name']}")
        if 'gbtree_train_param' in gb_params:
            train_params = gb_params['gbtree_train_param']
            print(f"  - train_param keys: {list(train_params.keys())}")
            for k, v in train_params.items():
                print(f"    - {k}: {v}")
        
        # Inspect tree structure
        if 'trees' in gb_params:
            trees_data = gb_params['trees']
            print(f"  - Number of trees in JSON: {len(trees_data)}")
            
            # Print first tree structure for inspection
            if trees_data:
                first_tree = trees_data[0]
                print(f"  - First tree keys: {list(first_tree.keys())}")
                if 'tree_param' in first_tree:
                    print(f"    - tree_param: {first_tree['tree_param']}")
    
    # Clean up
    import os
    os.remove(model_path)
    print(f"\nCleaned up {model_path}")

if __name__ == "__main__":
    reproduce_failure()