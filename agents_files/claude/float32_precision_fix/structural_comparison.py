#!/usr/bin/env python3

import numpy as np
import json
import xgboost as xgb
from src.generate_random_xgb import train_random_xgb
from src.xgboost_reader import create_trees_from_json

def structural_comparison():
    """
    Compare ONLY the structural data (weights, splits, leaf values) between:
    1. Raw JSON file
    2. XGBoost Booster loaded from JSON
    3. Our Tree implementation from JSON
    
    NO predictions - just pure structural data comparison.
    """
    print("🏗️ STRUCTURAL DATA COMPARISON")
    print("=" * 60)
    
    # Create and save model
    model_seed = 3
    model, X, y = train_random_xgb(
        num_features=18,
        n_estimators=6,
        max_depth=3,
        random_state=model_seed
    )
    
    model_path = "structural_debug_model.json"
    model.save_model(model_path)
    print(f"✅ Model saved to {model_path}")
    
    # SOURCE 1: Raw JSON file data
    print(f"\n📄 SOURCE 1: RAW JSON FILE")
    print("-" * 30)
    
    with open(model_path, 'r') as f:
        json_data = json.loads(f.read())
    
    base_score_json = float(json_data['learner']['learner_model_param']['base_score'])
    trees_json = json_data['learner']['gradient_booster']['model']['trees']
    
    print(f"Base score: {base_score_json:.15f}")
    print(f"Number of trees: {len(trees_json)}")
    
    # Extract all structural data from JSON
    json_tree_data = []
    for tree_idx, tree_data in enumerate(trees_json):
        tree_info = {
            'tree_id': tree_idx,
            'left_children': tree_data['left_children'],
            'right_children': tree_data['right_children'],
            'split_indices': tree_data['split_indices'],
            'split_conditions': tree_data['split_conditions'],
            'base_weights': tree_data['base_weights'],
            'default_left': tree_data['default_left']
        }
        json_tree_data.append(tree_info)
        print(f"Tree {tree_idx}: {len(tree_data['base_weights'])} nodes")
    
    # SOURCE 2: XGBoost Booster loaded from JSON
    print(f"\n🔥 SOURCE 2: XGBOOST BOOSTER FROM JSON")
    print("-" * 30)
    
    booster = xgb.Booster(model_file=model_path)
    
    # Try to extract structural information from the booster
    try:
        # Get the JSON dump from the loaded booster
        booster_json_dump = booster.get_dump(dump_format='json')
        booster_parsed = [json.loads(tree_str) for tree_str in booster_json_dump]
        print(f"Successfully extracted {len(booster_parsed)} trees from booster")
        
        # Compare with original JSON structure
        xgb_tree_data = []
        for tree_idx, tree_dump in enumerate(booster_parsed):
            # XGBoost dump has a different format - need to parse it
            def extract_xgb_tree_structure(node, node_id=0, structure_data=None):
                if structure_data is None:
                    structure_data = {
                        'left_children': [],
                        'right_children': [],
                        'split_indices': [],
                        'split_conditions': [],
                        'base_weights': [],
                        'default_left': []
                    }
                
                # Ensure we have enough slots
                while len(structure_data['left_children']) <= node_id:
                    structure_data['left_children'].append(-1)
                    structure_data['right_children'].append(-1)
                    structure_data['split_indices'].append(0)
                    structure_data['split_conditions'].append(0.0)
                    structure_data['base_weights'].append(0.0)
                    structure_data['default_left'].append(0)
                
                if 'leaf' in node:
                    # It's a leaf node
                    structure_data['left_children'][node_id] = -1
                    structure_data['right_children'][node_id] = -1
                    structure_data['split_indices'][node_id] = 0
                    structure_data['split_conditions'][node_id] = node['leaf']  # Leaf value
                    structure_data['base_weights'][node_id] = node['leaf']
                    structure_data['default_left'][node_id] = 0
                else:
                    # It's an internal node
                    split_feature = node['split']
                    split_condition = node['split_condition']
                    
                    structure_data['split_indices'][node_id] = split_feature
                    structure_data['split_conditions'][node_id] = split_condition
                    structure_data['base_weights'][node_id] = 0.0  # Internal nodes don't have weights
                    structure_data['default_left'][node_id] = 1 if node.get('missing') == split_feature else 0
                    
                    # Process children
                    if 'children' in node:
                        left_child_id = 2 * node_id + 1
                        right_child_id = 2 * node_id + 2
                        
                        structure_data['left_children'][node_id] = left_child_id
                        structure_data['right_children'][node_id] = right_child_id
                        
                        if len(node['children']) >= 1:
                            extract_xgb_tree_structure(node['children'][0], left_child_id, structure_data)
                        if len(node['children']) >= 2:
                            extract_xgb_tree_structure(node['children'][1], right_child_id, structure_data)
                
                return structure_data
            
            xgb_structure = extract_xgb_tree_structure(tree_dump)
            xgb_tree_data.append(xgb_structure)
            print(f"XGBoost Tree {tree_idx}: {len([x for x in xgb_structure['left_children'] if x != -1 or xgb_structure['base_weights'][xgb_structure['left_children'].index(x)] != 0])} nodes")
            
    except Exception as e:
        print(f"❌ Could not extract structure from XGBoost booster: {e}")
        xgb_tree_data = None
    
    # SOURCE 3: Our Tree implementation from JSON
    print(f"\n🌳 SOURCE 3: OUR TREE IMPLEMENTATION FROM JSON")
    print("-" * 30)
    
    forest = create_trees_from_json(json_data)
    print(f"Successfully parsed {len(forest)} trees")
    
    our_tree_data = []
    for tree_idx, tree in enumerate(forest):
        tree_info = {
            'tree_id': tree_idx,
            'nodes': {},
            'base_score_used': tree_idx == 0  # Only relevant for first tree
        }
        
        # Extract all node information
        for node_id, node in tree.nodes.items():
            node_info = {
                'node_id': node_id,
                'left_child_id': node.left_child_id,
                'right_child_id': node.right_child_id,
                'split_index': node.split_index,
                'split_condition': node.split_condition,
                'base_weight': node.base_weight,
                'default_left': node.default_left,
                'is_leaf': node.left_child_id == -1
            }
            tree_info['nodes'][node_id] = node_info
        
        our_tree_data.append(tree_info)
        print(f"Our Tree {tree_idx}: {len(tree.nodes)} nodes")
    
    # DETAILED COMPARISON
    print(f"\n🔍 DETAILED STRUCTURAL COMPARISON")
    print("=" * 60)
    
    # Focus on Tree 5 (the problematic one)
    tree_idx = 5
    print(f"\n🎯 FOCUSING ON TREE {tree_idx} (THE PROBLEMATIC ONE)")
    print("-" * 50)
    
    json_tree = json_tree_data[tree_idx]
    our_tree = our_tree_data[tree_idx]
    
    print(f"\\n📄 JSON Tree {tree_idx} Raw Data:")
    print(f"left_children:    {json_tree['left_children']}")
    print(f"right_children:   {json_tree['right_children']}")
    print(f"split_indices:    {json_tree['split_indices']}")
    print(f"split_conditions: {[f'{x:.15f}' for x in json_tree['split_conditions'][:6]]}...")
    print(f"base_weights:     {[f'{x:.15f}' for x in json_tree['base_weights'][:6]]}...")
    print(f"default_left:     {json_tree['default_left']}")
    
    print(f"\\n🌳 Our Tree {tree_idx} Parsed Data:")
    sorted_nodes = sorted(our_tree['nodes'].items())
    for node_id, node_info in sorted_nodes[:6]:  # Show first 6 nodes
        if node_info['is_leaf']:
            print(f"Node {node_id}: LEAF, value={node_info['split_condition']:.15f}")
        else:
            print(f"Node {node_id}: SPLIT, feature[{node_info['split_index']}] < {node_info['split_condition']:.15f}, default_left={node_info['default_left']}")
    
    # Node-by-node comparison for Tree 5
    print(f"\\n🔍 NODE-BY-NODE COMPARISON (Tree {tree_idx}):")
    print("-" * 40)
    
    max_nodes = len(json_tree['left_children'])
    all_match = True
    
    for node_id in range(max_nodes):
        json_left = json_tree['left_children'][node_id]
        json_right = json_tree['right_children'][node_id]
        json_split_idx = json_tree['split_indices'][node_id]
        json_split_cond = json_tree['split_conditions'][node_id]
        json_weight = json_tree['base_weights'][node_id]
        json_default_left = json_tree['default_left'][node_id]
        
        is_leaf = (json_left == -1 and json_right == -1)
        
        if node_id in our_tree['nodes']:
            our_node = our_tree['nodes'][node_id]
            
            # Compare values
            mismatches = []
            
            if our_node['left_child_id'] != json_left:
                mismatches.append(f"left_child: ours={our_node['left_child_id']}, json={json_left}")
            
            if our_node['right_child_id'] != json_right:
                mismatches.append(f"right_child: ours={our_node['right_child_id']}, json={json_right}")
            
            if not is_leaf and our_node['split_index'] != json_split_idx:
                mismatches.append(f"split_index: ours={our_node['split_index']}, json={json_split_idx}")
            
            if abs(our_node['split_condition'] - json_split_cond) > 1e-15:
                mismatches.append(f"split_condition: ours={our_node['split_condition']:.15f}, json={json_split_cond:.15f}")
            
            if our_node['base_weight'] is not None and abs(our_node['base_weight'] - json_weight) > 1e-15:
                mismatches.append(f"base_weight: ours={our_node['base_weight']:.15f}, json={json_weight:.15f}")
            
            if our_node['default_left'] != (json_default_left != 0):
                mismatches.append(f"default_left: ours={our_node['default_left']}, json={json_default_left != 0}")
            
            if mismatches:
                print(f"Node {node_id}: ❌ MISMATCHES - {', '.join(mismatches)}")
                all_match = False
            else:
                node_type = "LEAF" if is_leaf else "SPLIT"
                print(f"Node {node_id}: ✅ {node_type} matches perfectly")
        else:
            print(f"Node {node_id}: ❌ MISSING from our tree")
            all_match = False
    
    print(f"\\n🎯 STRUCTURAL COMPARISON RESULT:")
    if all_match:
        print("✅ Our tree structure matches JSON perfectly!")
        print("   The issue must be in prediction logic, not data parsing.")
    else:
        print("❌ Our tree structure has differences from JSON!")
        print("   Data parsing issues found.")
    
    # Clean up
    import os
    os.remove(model_path)

if __name__ == "__main__":
    structural_comparison()