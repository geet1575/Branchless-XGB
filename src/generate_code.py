import json
from xgboost_reader import Node, Tree, create_trees_from_json

file_name = "random_xgb_regressor.json"

xgboost_json_string =""

with open(file_name, 'r') as f:
    xgboost_json_string = f.read()

# Parse the JSON string
xgboost_model_data = json.loads(xgboost_json_string)

# Create a list of Tree objects
forest = create_trees_from_json(xgboost_model_data)

# You can now access the list of trees (a 'forest')
print(f"Successfully parsed {len(forest)} trees from the model.\n")

# Iterate through the forest and print each tree
for tree in forest:
    print(f"==================== Tree ID: {tree.tree_id} ====================")
    
    # Print a visual representation of the entire tree
    print(f"Tree {tree.tree_id} Structure:")
    tree.print_tree()
    print("\n")