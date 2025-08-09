#!/usr/bin/env python3

import numpy as np
import json
import xgboost as xgb
from src.generate_random_xgb import train_random_xgb

def leaf_value_verification():
    """Verify that we're getting the correct leaf values from our tree parsing"""
    print("🍃 LEAF VALUE VERIFICATION")
    print("=" * 50)
    
    # Create the failing model
    model_seed = 3
    num_features = 18
    n_estimators = 6
    max_depth = 3
    
    model, X, y = train_random_xgb(
        num_features=num_features,
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=model_seed
    )
    
    model_path = "leaf_debug_model.json"
    model.save_model(model_path)
    
    # Create the failing test case
    np.random.seed(3)
    test_vector = np.random.rand(num_features)
    
    # Get leaf indices from XGBoost
    booster = xgb.Booster(model_file=model_path)
    dmatrix = xgb.DMatrix(test_vector.reshape(1, -1))
    leaf_indices = booster.predict(dmatrix, pred_leaf=True)[0]
    print(f"XGBoost leaf indices: {leaf_indices}")
    
    # Load JSON and extract leaf values manually
    with open(model_path, 'r') as f:
        json_data = json.loads(f.read())
    
    trees_data = json_data['learner']['gradient_booster']['model']['trees']
    
    # Extract actual leaf values from JSON for each tree
    print(f"\n🍃 MANUAL LEAF VALUE EXTRACTION:")
    print("-" * 30)
    
    manual_tree_outputs = []
    for i, (tree_data, leaf_idx) in enumerate(zip(trees_data, leaf_indices)):
        leaf_idx = int(leaf_idx)
        base_weights = tree_data['base_weights']
        
        if leaf_idx < len(base_weights):
            leaf_value = base_weights[leaf_idx]
            manual_tree_outputs.append(leaf_value)
            print(f"Tree {i}: leaf_idx={leaf_idx}, leaf_value={leaf_value:.6f}")
        else:
            print(f"Tree {i}: ERROR - leaf_idx={leaf_idx} >= len(base_weights)={len(base_weights)}")
            manual_tree_outputs.append(0.0)
    
    # Compare with our parsed tree outputs
    print(f"\n🌳 OUR PARSED TREE OUTPUTS:")
    print("-" * 30)
    
    from src.xgboost_reader import create_trees_from_json
    forest = create_trees_from_json(json_data)
    
    our_tree_outputs = []
    for i, tree in enumerate(forest):
        tree_out = tree.predict(test_vector)
        our_tree_outputs.append(tree_out)
        print(f"Tree {i}: our_output={tree_out:.6f}")
    
    # Compare the two methods
    print(f"\n📊 COMPARISON:")
    print("-" * 30)
    total_diff = 0
    for i in range(len(manual_tree_outputs)):
        diff = abs(manual_tree_outputs[i] - our_tree_outputs[i])
        total_diff += diff
        match_status = "✅" if diff < 1e-10 else "❌"
        print(f"Tree {i}: manual={manual_tree_outputs[i]:.6f}, ours={our_tree_outputs[i]:.6f}, diff={diff:.10f} {match_status}")
    
    print(f"\nTotal difference in tree outputs: {total_diff:.10f}")
    
    # Now let's compute final predictions using both methods
    base_score = float(json_data['learner']['learner_model_param']['base_score'])
    learning_rate = model.learning_rate
    
    print(f"\n🎯 FINAL PREDICTION COMPARISON:")
    print("-" * 30)
    print(f"Base score: {base_score:.6f}")
    print(f"Learning rate: {learning_rate}")
    
    # Method 1: Using manual leaf values
    manual_pred = base_score + learning_rate * sum(manual_tree_outputs)
    print(f"Manual prediction: {base_score:.6f} + {learning_rate} * {sum(manual_tree_outputs):.6f} = {manual_pred:.6f}")
    
    # Method 2: Using our tree outputs 
    our_pred = base_score + learning_rate * sum(our_tree_outputs)
    print(f"Our prediction: {base_score:.6f} + {learning_rate} * {sum(our_tree_outputs):.6f} = {our_pred:.6f}")
    
    # XGBoost prediction
    xgb_pred = booster.predict(dmatrix)[0]
    print(f"XGBoost prediction: {xgb_pred:.6f}")
    
    print(f"\nDifferences:")
    print(f"XGBoost vs Manual: {abs(xgb_pred - manual_pred):.6f}")
    print(f"XGBoost vs Ours: {abs(xgb_pred - our_pred):.6f}")
    print(f"Manual vs Ours: {abs(manual_pred - our_pred):.6f}")
    
    # If there's still a difference, let's check if there are any other parameters we're missing
    if abs(xgb_pred - manual_pred) > 1e-10:
        print(f"\n🔍 ADDITIONAL PARAMETER INVESTIGATION:")
        print("-" * 30)
        
        # Check learner model parameters
        learner_params = json_data['learner']['learner_model_param']
        print(f"Learner model params: {learner_params}")
        
        # Check if there are any other scaling factors
        print(f"Boost from average: {learner_params.get('boost_from_average', 'not found')}")
        
        # Check objective parameters
        objective = json_data['learner']['objective']
        print(f"Objective: {objective}")
    
    # Clean up
    import os
    os.remove(model_path)

if __name__ == "__main__":
    leaf_value_verification()