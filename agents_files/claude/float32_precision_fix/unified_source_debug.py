#!/usr/bin/env python3

import numpy as np
import json
import xgboost as xgb
from src.generate_random_xgb import train_random_xgb
from src.xgboost_reader import create_trees_from_json

def unified_source_debug():
    """
    Use JSON dump as single source of truth and compare:
    1. XGBoost model loaded from JSON
    2. Our tree implementation from JSON  
    3. Raw JSON data manual traversal
    """
    print("📄 UNIFIED SOURCE DEBUG - JSON AS SINGLE SOURCE OF TRUTH")
    print("=" * 70)
    
    # Create and save model
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
    
    model_path = "unified_debug_model.json"
    model.save_model(model_path)
    print(f"✅ Model saved to {model_path} (SINGLE SOURCE OF TRUTH)")
    
    # Test case
    np.random.seed(3)
    test_vector = np.random.rand(num_features)
    print(f"Test vector created with seed=3")
    
    # Load JSON data (our single source of truth)
    with open(model_path, 'r') as f:
        json_data = json.loads(f.read())
    
    base_score = float(json_data['learner']['learner_model_param']['base_score'])
    trees_data = json_data['learner']['gradient_booster']['model']['trees']
    
    print(f"\\n📊 SINGLE SOURCE OF TRUTH ANALYSIS:")
    print(f"Base score: {base_score:.10f}")
    print(f"Number of trees: {len(trees_data)}")
    
    # METHOD 1: XGBoost Booster loaded from JSON
    print(f"\\n🔥 METHOD 1: XGBOOST BOOSTER FROM JSON")
    print("-" * 40)
    
    booster = xgb.Booster(model_file=model_path)
    dmatrix = xgb.DMatrix(test_vector.reshape(1, -1))
    
    # Get prediction
    xgb_prediction = booster.predict(dmatrix)[0]
    print(f"XGBoost prediction: {xgb_prediction:.10f}")
    
    # Get leaf indices  
    leaf_indices = booster.predict(dmatrix, pred_leaf=True)[0]
    print(f"Leaf indices: {[int(x) for x in leaf_indices]}")
    
    # Get contributions (if supported)
    try:
        contributions = booster.predict(dmatrix, pred_contribs=True)[0]
        print(f"Feature contributions: {contributions[:5]}... (showing first 5)")
    except:
        print("Feature contributions not available")
    
    # METHOD 2: Manual prediction from JSON (our ground truth calculation)
    print(f"\\n📋 METHOD 2: MANUAL PREDICTION FROM JSON")
    print("-" * 40)
    
    manual_prediction = base_score
    manual_tree_outputs = []
    
    for tree_idx, tree_data in enumerate(trees_data):
        expected_leaf_idx = int(leaf_indices[tree_idx])
        leaf_value = tree_data['base_weights'][expected_leaf_idx]
        manual_tree_outputs.append(leaf_value)
        manual_prediction += leaf_value  # eta=1.0 as established
        print(f"Tree {tree_idx}: leaf_idx={expected_leaf_idx}, leaf_value={leaf_value:.10f}")
    
    print(f"Manual prediction: {base_score:.10f} + {sum(manual_tree_outputs):.10f} = {manual_prediction:.10f}")
    
    # METHOD 3: Our tree implementation from JSON
    print(f"\\n🌳 METHOD 3: OUR TREE IMPLEMENTATION FROM JSON")
    print("-" * 40)
    
    forest = create_trees_from_json(json_data)
    our_prediction = base_score
    our_tree_outputs = []
    
    for tree_idx, tree in enumerate(forest):
        tree_output = tree.predict(test_vector)
        our_tree_outputs.append(tree_output)
        our_prediction += tree_output
        print(f"Tree {tree_idx}: our_output={tree_output:.10f}")
    
    print(f"Our prediction: {base_score:.10f} + {sum(our_tree_outputs):.10f} = {our_prediction:.10f}")
    
    # METHOD 4: Raw JSON manual traversal for problematic tree
    print(f"\\n📐 METHOD 4: RAW JSON MANUAL TRAVERSAL (Tree 5)")
    print("-" * 40)
    
    tree5_data = trees_data[5]
    print(f"Tree 5 structure from JSON:")
    print(f"  left_children:    {tree5_data['left_children']}")
    print(f"  right_children:   {tree5_data['right_children']}")
    print(f"  split_indices:    {tree5_data['split_indices']}")
    print(f"  split_conditions: {[f'{x:.15f}' for x in tree5_data['split_conditions'][:6]]}...")
    print(f"  base_weights:     {[f'{x:.15f}' for x in tree5_data['base_weights'][:6]]}...")
    
    # Manual traversal of Tree 5
    current_node = 0
    traversal_log = []
    
    while True:
        left = tree5_data['left_children'][current_node]
        right = tree5_data['right_children'][current_node]
        
        if left == -1 and right == -1:  # Leaf
            leaf_value = tree5_data['base_weights'][current_node]
            traversal_log.append(f"REACHED LEAF {current_node}: value={leaf_value:.15f}")
            print(f"  Final: {traversal_log[-1]}")
            break
        
        split_idx = tree5_data['split_indices'][current_node]
        split_cond = tree5_data['split_conditions'][current_node]
        feature_val = test_vector[split_idx]
        
        # The critical comparison
        goes_left = feature_val < split_cond
        next_node = left if goes_left else right
        direction = "LEFT" if goes_left else "RIGHT"
        
        log_entry = f"Node {current_node}: feature[{split_idx}]={feature_val:.15f} vs {split_cond:.15f} -> {direction} to {next_node}"
        traversal_log.append(log_entry)
        print(f"  {log_entry}")
        
        # Show the exact bit representations for the critical comparison
        if current_node == 5:  # The problematic node
            print(f"    🔍 CRITICAL COMPARISON ANALYSIS:")
            print(f"    Feature value hex: {feature_val.hex()}")
            print(f"    Split condition hex: {split_cond.hex()}")
            print(f"    Difference: {feature_val - split_cond:.20f}")
            print(f"    feature_val < split_cond: {feature_val < split_cond}")
            print(f"    feature_val <= split_cond: {feature_val <= split_cond}")
            print(f"    feature_val == split_cond: {feature_val == split_cond}")
        
        current_node = next_node
        
        if len(traversal_log) > 10:  # Safety
            break
    
    # COMPARISON ANALYSIS
    print(f"\\n📊 PREDICTION COMPARISON:")
    print("-" * 40)
    print(f"XGBoost:     {xgb_prediction:.15f}")
    print(f"Manual:      {manual_prediction:.15f}")
    print(f"Our trees:   {our_prediction:.15f}")
    
    xgb_vs_manual = abs(xgb_prediction - manual_prediction)
    xgb_vs_ours = abs(xgb_prediction - our_prediction)
    manual_vs_ours = abs(manual_prediction - our_prediction)
    
    print(f"\\nDifferences:")
    print(f"XGBoost vs Manual:    {xgb_vs_manual:.15f}")
    print(f"XGBoost vs Our trees: {xgb_vs_ours:.15f}")
    print(f"Manual vs Our trees:  {manual_vs_ours:.15f}")
    
    # Tree-by-tree comparison
    print(f"\\n🌲 TREE-BY-TREE OUTPUT COMPARISON:")
    print("-" * 40)
    total_tree_diff = 0
    for i in range(len(manual_tree_outputs)):
        diff = abs(manual_tree_outputs[i] - our_tree_outputs[i])
        total_tree_diff += diff
        status = "✅" if diff < 1e-15 else "❌" 
        print(f"Tree {i}: manual={manual_tree_outputs[i]:.15f}, ours={our_tree_outputs[i]:.15f}, diff={diff:.15f} {status}")
    
    print(f"\\nTotal tree output difference: {total_tree_diff:.15f}")
    
    # ANALYSIS RESULTS
    print(f"\\n🎯 ANALYSIS RESULTS:")
    print("-" * 40)
    
    if xgb_vs_manual < 1e-15:
        print("✅ XGBoost and Manual match perfectly - JSON is consistent")
    else:
        print("❌ XGBoost and Manual differ - JSON consistency issue")
    
    if manual_vs_ours < 1e-15:
        print("✅ Our tree implementation matches manual JSON traversal perfectly")
    else:
        print("❌ Our tree implementation has a bug")
        
    if xgb_vs_ours > 1e-10:
        print("❌ Significant difference between XGBoost and our implementation")
        print(f"   This suggests either:")
        print(f"   1. XGBoost uses different comparison logic than standard '<'")
        print(f"   2. There are precision/rounding differences")
        print(f"   3. XGBoost has different tie-breaking rules")
    
    # Clean up
    import os
    os.remove(model_path)

if __name__ == "__main__":
    unified_source_debug()