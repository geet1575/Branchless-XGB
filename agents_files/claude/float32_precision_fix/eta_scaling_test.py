#!/usr/bin/env python3

import numpy as np
import json
import xgboost as xgb
from xgboost import XGBRegressor

def test_eta_scaling():
    """Test whether XGBoost leaf values in JSON are pre-scaled by learning rate"""
    print("🔬 TESTING ETA SCALING IN XGBOOST MODELS")
    print("=" * 60)
    
    # Create a simple dataset
    np.random.seed(42)
    X = np.random.rand(100, 5)
    y = np.random.rand(100)
    
    # Test with different learning rates
    learning_rates = [0.1, 0.3, 1.0]
    
    for eta in learning_rates:
        print(f"\n📊 TESTING WITH LEARNING RATE = {eta}")
        print("-" * 40)
        
        # Train model with specific learning rate
        model = XGBRegressor(
            n_estimators=3,  # Just 3 trees to make analysis easier
            max_depth=2,     # Shallow trees
            learning_rate=eta,
            random_state=42
        )
        
        model.fit(X, y)
        
        # Save model to JSON
        model_path = f"eta_test_{eta}.json"
        model.save_model(model_path)
        
        # Load JSON and examine leaf values
        with open(model_path, 'r') as f:
            json_data = json.loads(f.read())
        
        trees_data = json_data['learner']['gradient_booster']['model']['trees']
        base_score = float(json_data['learner']['learner_model_param']['base_score'])
        
        print(f"Base score: {base_score:.6f}")
        print(f"Number of trees: {len(trees_data)}")
        
        # Get leaf values from first tree
        first_tree = trees_data[0]
        leaf_values = first_tree['base_weights']
        print(f"First tree leaf values: {[f'{x:.6f}' for x in leaf_values[:4]]}...")  # Show first 4
        
        # Test prediction on a simple case
        test_x = np.array([[0.5, 0.5, 0.5, 0.5, 0.5]])
        
        # Method 1: XGBoost prediction
        xgb_pred = model.predict(test_x)[0]
        
        # Method 2: Manual prediction assuming eta=1.0 (raw leaf values)
        booster = xgb.Booster(model_file=model_path)
        leaf_indices = booster.predict(xgb.DMatrix(test_x), pred_leaf=True)[0]
        
        manual_pred_eta_1 = base_score
        for i, leaf_idx in enumerate(leaf_indices):
            tree_leaf_values = trees_data[i]['base_weights']
            manual_pred_eta_1 += tree_leaf_values[int(leaf_idx)]
        
        # Method 3: Manual prediction assuming eta needs to be applied
        manual_pred_with_eta = base_score
        for i, leaf_idx in enumerate(leaf_indices):
            tree_leaf_values = trees_data[i]['base_weights']
            manual_pred_with_eta += eta * tree_leaf_values[int(leaf_idx)]
        
        print(f"XGBoost prediction: {xgb_pred:.6f}")
        print(f"Manual (eta=1.0): {manual_pred_eta_1:.6f}")
        print(f"Manual (eta={eta}): {manual_pred_with_eta:.6f}")
        
        diff_eta_1 = abs(xgb_pred - manual_pred_eta_1)
        diff_with_eta = abs(xgb_pred - manual_pred_with_eta)
        
        print(f"Difference (eta=1.0): {diff_eta_1:.8f}")
        print(f"Difference (eta={eta}): {diff_with_eta:.8f}")
        
        if diff_eta_1 < 1e-10:
            print("✅ LEAF VALUES ARE PRE-SCALED (eta=1.0 works)")
        elif diff_with_eta < 1e-10:
            print("❌ LEAF VALUES ARE NOT PRE-SCALED (need to apply eta)")
        else:
            print("❓ Neither method matches exactly")
        
        # Clean up
        import os
        os.remove(model_path)
    
    print(f"\n🧠 CONCLUSION:")
    print("-" * 40)
    print("If leaf values are pre-scaled by learning rate during training,")
    print("then eta=1.0 should work for prediction from saved JSON models.")
    print("If leaf values are raw, then we need to apply eta during prediction.")

if __name__ == "__main__":
    test_eta_scaling()