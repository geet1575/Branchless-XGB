#!/usr/bin/env python3

import numpy as np
import json
import xgboost as xgb
from src.generate_random_xgb import train_random_xgb
from src.xgboost_reader import create_trees_from_json

def compare_tree_structures():
    """Compare our parsed tree structure with the original JSON to find missing info"""
    print("🌳 TREE STRUCTURE COMPARISON")
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
    
    model_path = "tree_compare_model.json"
    model.save_model(model_path)
    
    # Load JSON data
    with open(model_path, 'r') as f:
        json_data = json.loads(f.read())
    
    # Create our parsed trees
    forest = create_trees_from_json(json_data)
    
    # Focus on Tree 5 (the problematic one)
    tree_idx = 5
    print(f"🔍 ANALYZING TREE {tree_idx}")
    print("-" * 30)
    
    # Get JSON tree data
    json_tree = json_data['learner']['gradient_booster']['model']['trees'][tree_idx]
    parsed_tree = forest[tree_idx]
    
    print(f"📊 JSON TREE {tree_idx} STRUCTURE:")
    print(f"left_children:    {json_tree['left_children']}")
    print(f"right_children:   {json_tree['right_children']}")
    print(f"split_indices:    {json_tree['split_indices']}")
    print(f"split_conditions: {[f'{x:.6f}' for x in json_tree['split_conditions']]}")
    print(f"base_weights:     {[f'{x:.6f}' for x in json_tree['base_weights']]}")
    print(f"default_left:     {json_tree['default_left']}")
    
    print(f"\n🌲 OUR PARSED TREE {tree_idx} STRUCTURE:")
    parsed_tree.print_tree()
    
    # Verify node-by-node comparison
    print(f"\n🔍 NODE-BY-NODE VERIFICATION:")
    print("-" * 30)
    
    num_nodes = len(json_tree['left_children'])
    for node_id in range(num_nodes):
        left_child = json_tree['left_children'][node_id]
        right_child = json_tree['right_children'][node_id]
        split_idx = json_tree['split_indices'][node_id]
        split_cond = json_tree['split_conditions'][node_id]
        base_weight = json_tree['base_weights'][node_id]
        default_left = json_tree['default_left'][node_id]
        
        is_leaf = (left_child == -1 and right_child == -1)
        
        print(f"Node {node_id}: ", end="")
        if is_leaf:
            print(f"LEAF (value={base_weight:.6f})")
        else:
            print(f"SPLIT (feature[{split_idx}] < {split_cond:.6f}, default_left={default_left != 0}) -> L:{left_child}, R:{right_child}")
        
        # Check if our parsed tree has this node
        if node_id in parsed_tree.nodes:
            our_node = parsed_tree.nodes[node_id]
            
            # Verify the node properties
            if is_leaf:
                our_value = our_node.split_condition  # Leaf value is stored in split_condition for our implementation
                if abs(our_value - base_weight) > 1e-10:
                    print(f"  ❌ LEAF VALUE MISMATCH: ours={our_value:.6f}, expected={base_weight:.6f}")
                else:
                    print(f"  ✅ Leaf value matches")
            else:
                if our_node.split_index != split_idx:
                    print(f"  ❌ SPLIT INDEX MISMATCH: ours={our_node.split_index}, expected={split_idx}")
                elif abs(our_node.split_condition - split_cond) > 1e-10:
                    print(f"  ❌ SPLIT CONDITION MISMATCH: ours={our_node.split_condition:.6f}, expected={split_cond:.6f}")
                else:
                    print(f"  ✅ Split matches")
                
                # Check default_left handling
                if our_node.default_left != (default_left != 0):
                    print(f"  ❌ DEFAULT_LEFT MISMATCH: ours={our_node.default_left}, expected={default_left != 0}")
                else:
                    print(f"  ✅ default_left matches")
        else:
            print(f"  ❌ NODE MISSING from our parsed tree!")
    
    # Test the specific failing case
    print(f"\n🎯 TESTING SPECIFIC FAILING CASE:")
    print("-" * 30)
    
    np.random.seed(3)
    test_vector = np.random.rand(num_features)
    
    # Manual traversal using JSON data
    print("Manual traversal using JSON:")
    current_node = 0
    path = [0]
    
    while True:
        left = json_tree['left_children'][current_node]
        right = json_tree['right_children'][current_node]
        
        if left == -1 and right == -1:  # Leaf
            leaf_value = json_tree['base_weights'][current_node]
            print(f"  Reached leaf {current_node}: value={leaf_value:.6f}")
            break
        
        split_idx = json_tree['split_indices'][current_node]
        split_cond = json_tree['split_conditions'][current_node]
        default_left = json_tree['default_left'][current_node] != 0
        feature_val = test_vector[split_idx]
        
        print(f"  Node {current_node}: feature[{split_idx}]={feature_val:.10f} vs {split_cond:.10f} (default_left={default_left})")
        
        # XGBoost decision logic
        if feature_val < split_cond:
            current_node = left
            print(f"    -> Go LEFT to {current_node}")
        else:
            current_node = right
            print(f"    -> Go RIGHT to {current_node}")
        
        path.append(current_node)
        
        if len(path) > 10:
            break
    
    # Our traversal
    print("\\nOur tree traversal:")
    our_prediction = parsed_tree.predict(test_vector)
    print(f"  Our prediction: {our_prediction:.6f}")
    
    # Get XGBoost's expected leaf
    booster = xgb.Booster(model_file=model_path)
    leaf_indices = booster.predict(xgb.DMatrix(test_vector.reshape(1, -1)), pred_leaf=True)[0]
    expected_leaf_idx = int(leaf_indices[tree_idx])
    expected_leaf_val = json_tree['base_weights'][expected_leaf_idx]
    
    print(f"  XGBoost expects leaf {expected_leaf_idx}: value={expected_leaf_val:.6f}")
    
    if abs(our_prediction - expected_leaf_val) > 1e-10:
        print(f"  ❌ MISMATCH: diff={abs(our_prediction - expected_leaf_val):.10f}")
    else:
        print(f"  ✅ MATCH!")
    
    # Clean up
    import os
    os.remove(model_path)

if __name__ == "__main__":
    compare_tree_structures()