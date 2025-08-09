#!/usr/bin/env python3

import numpy as np
import json
import xgboost as xgb
from src.generate_random_xgb import train_random_xgb

def detailed_prediction_analysis():
    """Compare step-by-step how XGBoost vs our implementation computes predictions"""
    print("🔍 DETAILED PREDICTION ANALYSIS")
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
    
    model_path = "pred_debug_model.json"
    model.save_model(model_path)
    
    # Create the failing test case
    np.random.seed(3)
    test_vector = np.random.rand(num_features)
    print(f"Test vector shape: {test_vector.shape}")
    print(f"Test vector: {test_vector}")
    
    # Method 1: XGBoost Regressor prediction
    print(f"\n📊 METHOD 1: XGBoost Regressor")
    regressor_pred = model.predict(test_vector.reshape(1, -1))[0]
    print(f"Regressor prediction: {regressor_pred:.6f}")
    
    # Method 2: XGBoost Booster prediction  
    print(f"\n📊 METHOD 2: XGBoost Booster")
    booster = xgb.Booster(model_file=model_path)
    booster_pred = booster.predict(xgb.DMatrix(test_vector.reshape(1, -1)))[0]
    print(f"Booster prediction: {booster_pred:.6f}")
    
    # Method 3: Manual calculation using booster.predict_leaf
    print(f"\n📊 METHOD 3: Manual calculation with predict_leaf")
    dmatrix = xgb.DMatrix(test_vector.reshape(1, -1))
    leaf_indices = booster.predict(dmatrix, pred_leaf=True)[0]  # Get leaf indices
    print(f"Leaf indices for each tree: {leaf_indices}")
    
    # Method 4: Manual calculation using our tree implementation
    print(f"\n📊 METHOD 4: Our custom tree implementation")
    
    with open(model_path, 'r') as f:
        json_data = json.loads(f.read())
    
    from src.xgboost_reader import create_trees_from_json
    forest = create_trees_from_json(json_data)
    
    base_score = float(json_data['learner']['learner_model_param']['base_score'])
    print(f"Base score: {base_score:.6f}")
    
    # Check what learning rate we should use
    # Option A: From regressor object
    eta_from_regressor = model.learning_rate
    print(f"Learning rate from regressor: {eta_from_regressor}")
    
    # Option B: Try to extract from JSON (if available)
    gb_data = json_data['learner']['gradient_booster']
    if 'gbtree_train_param' in gb_data:
        train_params = gb_data['gbtree_train_param']
        eta_from_json = train_params.get('learning_rate', eta_from_regressor)
        print(f"Learning rate from JSON: {eta_from_json}")
    else:
        print("No gbtree_train_param found in JSON")
        eta_from_json = eta_from_regressor
    
    # Calculate using correct learning rate
    custom_pred = base_score
    print(f"Starting with base_score: {custom_pred:.6f}")
    
    tree_outputs = []
    for i, tree in enumerate(forest):
        tree_out = tree.predict(test_vector)
        tree_outputs.append(tree_out)
        custom_pred += eta_from_regressor * tree_out
        print(f"Tree {i}: raw_output={tree_out:.6f}, eta*output={eta_from_regressor * tree_out:.6f}, cumulative={custom_pred:.6f}")
    
    print(f"\nFinal custom prediction: {custom_pred:.6f}")
    print(f"Difference from XGBoost: {abs(booster_pred - custom_pred):.6f}")
    
    # Let's also manually check if our tree parsing is correct
    # by comparing tree structure
    print(f"\n🔍 TREE STRUCTURE VERIFICATION")
    print("-" * 30)
    
    if 'trees' in gb_data['model']:
        json_trees = gb_data['model']['trees']
        print(f"Number of trees in JSON: {len(json_trees)}")
        print(f"Number of parsed trees: {len(forest)}")
        
        # Check first tree structure
        if len(json_trees) > 0:
            first_json_tree = json_trees[0]
            first_parsed_tree = forest[0]
            
            print(f"\nFirst tree in JSON has keys: {list(first_json_tree.keys())}")
            
            # Try to manually traverse first tree for the test vector
            if 'left_children' in first_json_tree:
                print("Manual tree traversal for first tree:")
                print(f"Root node (id 0)")
                
                # Simple manual traversal
                current_node = 0
                left_children = first_json_tree['left_children'] 
                right_children = first_json_tree['right_children']
                split_indices = first_json_tree['split_indices'] if 'split_indices' in first_json_tree else []
                split_conditions = first_json_tree['split_conditions'] if 'split_conditions' in first_json_tree else []
                base_weights = first_json_tree['base_weights'] if 'base_weights' in first_json_tree else []
                
                steps = 0
                while steps < 10:  # Safety limit
                    if current_node >= len(left_children):
                        break
                        
                    left = left_children[current_node] 
                    right = right_children[current_node]
                    
                    # If it's a leaf node
                    if left == right and left == -1:
                        leaf_value = base_weights[current_node] if current_node < len(base_weights) else 0
                        print(f"  Reached leaf {current_node}: value={leaf_value:.6f}")
                        break
                    
                    # If it's an internal node
                    if current_node < len(split_indices) and current_node < len(split_conditions):
                        feature_idx = split_indices[current_node]
                        threshold = split_conditions[current_node]
                        feature_val = test_vector[feature_idx] if feature_idx < len(test_vector) else 0
                        
                        print(f"  Node {current_node}: feature[{feature_idx}]={feature_val:.6f} vs threshold={threshold:.6f}")
                        
                        if feature_val < threshold:
                            current_node = left
                            print(f"    -> Go left to node {current_node}")
                        else:
                            current_node = right
                            print(f"    -> Go right to node {current_node}")
                    else:
                        print(f"  Missing split data for node {current_node}")
                        break
                    
                    steps += 1
                    
                print(f"Our parsed tree prediction: {first_parsed_tree.predict(test_vector):.6f}")
    
    # Clean up
    import os
    os.remove(model_path)

if __name__ == "__main__":
    detailed_prediction_analysis()