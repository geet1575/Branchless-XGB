#!/usr/bin/env python3

import numpy as np
import json
import xgboost as xgb
from src.generate_random_xgb import train_random_xgb

def debug_tree5():
    """Debug Tree 5 specifically to find the parsing bug"""
    print("🌳 TREE 5 DEBUGGING")
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
    
    model_path = "tree5_debug_model.json"
    model.save_model(model_path)
    
    # Create the failing test case
    np.random.seed(3)
    test_vector = np.random.rand(num_features)
    
    # Get leaf index for tree 5
    booster = xgb.Booster(model_file=model_path)
    dmatrix = xgb.DMatrix(test_vector.reshape(1, -1))
    leaf_indices = booster.predict(dmatrix, pred_leaf=True)[0]
    tree5_leaf_idx = int(leaf_indices[5])
    
    print(f"Tree 5 should reach leaf: {tree5_leaf_idx}")
    
    # Load JSON and examine Tree 5 structure
    with open(model_path, 'r') as f:
        json_data = json.loads(f.read())
    
    tree5_data = json_data['learner']['gradient_booster']['model']['trees'][5]
    
    print(f"\\n📊 TREE 5 JSON STRUCTURE:")
    print("-" * 30)
    for key in ['left_children', 'right_children', 'split_indices', 'split_conditions', 'base_weights']:
        if key in tree5_data:
            values = tree5_data[key]
            print(f"{key}: {values}")
    
    expected_leaf_value = tree5_data['base_weights'][tree5_leaf_idx]
    print(f"\\nExpected leaf value at index {tree5_leaf_idx}: {expected_leaf_value:.6f}")
    
    # Manual traversal of Tree 5
    print(f"\\n🔍 MANUAL TREE 5 TRAVERSAL:")
    print("-" * 30)
    
    left_children = tree5_data['left_children']
    right_children = tree5_data['right_children']
    split_indices = tree5_data['split_indices']
    split_conditions = tree5_data['split_conditions']
    base_weights = tree5_data['base_weights']
    
    current_node = 0
    path = []
    
    while True:
        path.append(current_node)
        left = left_children[current_node]
        right = right_children[current_node]
        
        # Check if leaf
        if left == -1 and right == -1:
            leaf_value = base_weights[current_node]
            print(f"Reached leaf {current_node}: value={leaf_value:.6f}")
            print(f"Path taken: {' -> '.join(map(str, path))}")
            break
        
        # Internal node
        feature_idx = split_indices[current_node]
        threshold = split_conditions[current_node]
        feature_val = test_vector[feature_idx]
        
        print(f"Node {current_node}: feature[{feature_idx}]={feature_val:.6f} vs threshold={threshold:.6f}")
        
        if feature_val < threshold:
            current_node = left
            print(f"  -> Go LEFT to node {current_node}")
        else:
            current_node = right
            print(f"  -> Go RIGHT to node {current_node}")
        
        if len(path) > 10:  # Safety break
            print("Safety break - too many steps")
            break
    
    # Now test our parsed Tree 5
    print(f"\\n🌲 OUR PARSED TREE 5:")
    print("-" * 30)
    
    from src.xgboost_reader import create_trees_from_json
    forest = create_trees_from_json(json_data)
    tree5_parsed = forest[5]
    
    our_tree5_output = tree5_parsed.predict(test_vector)
    print(f"Our Tree 5 prediction: {our_tree5_output:.6f}")
    
    # Let's inspect our parsed tree structure
    print(f"\\n🔧 PARSED TREE 5 INSPECTION:")
    print("-" * 30)
    print(f"Tree 5 root node: {tree5_parsed.root}")
    
    def print_node_structure(node, indent=0, max_depth=5):
        if indent > max_depth or node is None:
            return
        
        prefix = "  " * indent
        if hasattr(node, 'is_leaf') and node.is_leaf:
            print(f"{prefix}Leaf(value={getattr(node, 'leaf_value', 'unknown'):.6f})")
        else:
            feature_idx = getattr(node, 'split_feature', 'unknown')
            threshold = getattr(node, 'split_value', 'unknown')
            print(f"{prefix}Internal(feature={feature_idx}, threshold={threshold})")
            
            if hasattr(node, 'yes_child') and node.yes_child:
                print(f"{prefix}├─ YES:")
                print_node_structure(node.yes_child, indent + 1, max_depth)
            
            if hasattr(node, 'no_child') and node.no_child:
                print(f"{prefix}└─ NO:")
                print_node_structure(node.no_child, indent + 1, max_depth)
    
    if tree5_parsed.root:
        print_node_structure(tree5_parsed.root)
    
    # Clean up
    import os
    os.remove(model_path)

if __name__ == "__main__":
    debug_tree5()