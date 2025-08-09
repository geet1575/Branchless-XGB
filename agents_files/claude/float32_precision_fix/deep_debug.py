#!/usr/bin/env python3

import numpy as np
import json
import xgboost as xgb
from src.generate_random_xgb import train_random_xgb

def deep_model_analysis():
    """Deep dive into the XGBoost model structure and parameters"""
    print("🔍 DEEP MODEL ANALYSIS")
    print("=" * 50)
    
    # Reproduce the exact model
    model_seed = 3
    num_features = 18
    n_estimators = 6
    max_depth = 3
    
    # Generate the model and get the Python object info too
    model, X, y = train_random_xgb(
        num_features=num_features,
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=model_seed
    )
    
    # Check the XGBoost regressor object's parameters
    print("📋 XGBOOST REGRESSOR PARAMETERS:")
    print("-" * 30)
    for param, value in model.get_params().items():
        print(f"  {param}: {value}")
    
    # Save and load the model
    model_path = "deep_debug_model.json"
    model.save_model(model_path)
    
    # Load JSON and inspect structure
    with open(model_path, 'r') as f:
        xgboost_json_string = f.read()
    
    xgboost_model_data = json.loads(xgboost_json_string)
    
    # Print the complete JSON structure (truncated for key sections)
    print("\n📋 JSON MODEL STRUCTURE:")
    print("-" * 30)
    
    def print_dict_structure(d, indent=0, max_depth=3):
        if indent > max_depth:
            return
        for k, v in d.items():
            if isinstance(v, dict):
                print("  " * indent + f"{k}: {{")
                print_dict_structure(v, indent + 1, max_depth)
                print("  " * indent + "}")
            elif isinstance(v, list) and len(v) > 0:
                print("  " * indent + f"{k}: [list of {len(v)} items]")
                if isinstance(v[0], dict):
                    print("  " * indent + f"  First item: {{")
                    print_dict_structure(v[0], indent + 2, max_depth)
                    print("  " * indent + "  }}")
            else:
                print("  " * indent + f"{k}: {v}")
    
    print_dict_structure(xgboost_model_data)
    
    # Focus on gradient booster parameters
    print("\n📋 GRADIENT BOOSTER DETAILS:")
    print("-" * 30)
    gb = xgboost_model_data['learner']['gradient_booster']
    
    if 'gbtree_train_param' in gb:
        train_params = gb['gbtree_train_param']
        print("gbtree_train_param:")
        for k, v in train_params.items():
            print(f"  {k}: {v}")
    
    if 'gbtree_model_param' in gb:
        model_params = gb['gbtree_model_param']
        print("gbtree_model_param:")
        for k, v in model_params.items():
            print(f"  {k}: {v}")
    
    # Try to understand the learning rate issue
    print("\n📋 LEARNING RATE INVESTIGATION:")
    print("-" * 30)
    
    # Check if the model object has learning rate info
    if hasattr(model, 'learning_rate'):
        print(f"model.learning_rate: {model.learning_rate}")
    
    if hasattr(model, 'get_booster'):
        booster = model.get_booster()
        if hasattr(booster, 'attributes'):
            attrs = booster.attributes()
            print(f"Booster attributes: {attrs}")
    
    # Let's also check what happens when we manually test different learning rates
    print("\n🧪 LEARNING RATE TESTING:")
    print("-" * 30)
    
    # Load our trees
    from src.xgboost_reader import create_trees_from_json
    forest = create_trees_from_json(xgboost_model_data)
    actual_xgb_model = xgb.Booster(model_file=model_path)
    
    # Test vector
    np.random.seed(3)
    random_feature_vector = np.random.rand(num_features)
    
    # XGBoost prediction
    xgb_pred = actual_xgb_model.predict(xgb.DMatrix(random_feature_vector.reshape(1, -1)))[0]
    print(f"XGBoost prediction: {xgb_pred:.6f}")
    
    # Test different learning rates
    base_score = float(xgboost_model_data['learner']['learner_model_param']['base_score'])
    tree_outputs = [tree.predict(random_feature_vector) for tree in forest]
    
    print(f"Base score: {base_score:.6f}")
    print(f"Individual tree outputs: {[f'{x:.6f}' for x in tree_outputs]}")
    
    # Test various learning rates
    test_etas = [0.1, 0.3, 1.0]
    for eta in test_etas:
        custom_pred = base_score + eta * sum(tree_outputs)
        diff = abs(xgb_pred - custom_pred)
        print(f"eta={eta}: prediction={custom_pred:.6f}, diff={diff:.6f}")
    
    # Also check the original default learning rate used in generate_random_xgb
    print(f"\n📋 DEFAULT PARAMETERS IN generate_random_xgb.py:")
    print(f"Looking at the function signature...")
    
    # Clean up
    import os
    os.remove(model_path)

if __name__ == "__main__":
    deep_model_analysis()