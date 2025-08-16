import json
import os
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

# Test C++ code generation for first few trees (limit output)
print("="*80)
print("C++ CODE GENERATION TEST")
print("="*80)

# Test with first 3 trees to keep output manageable
test_trees = forest[:3]

for i, tree in enumerate(test_trees):
    print(f"\n{'='*60}")
    print(f"TREE {i+1} (ID: {tree.tree_id})")
    print(f"{'='*60}")
    
    # Print tree structure
    print("Tree Structure:")
    tree.print_tree()
    print()
    
    # Generate naive C++ code
    print("NAIVE C++ CODE (if/else):")
    print("-" * 30)
    naive_code = tree.generate_naive_cpp(f"predict_tree_{i+1}")
    print(naive_code)
    print()
    
    # Generate branchless C++ code
    print("BRANCHLESS C++ CODE (mathematical):")
    print("-" * 40)
    branchless_code = tree.generate_branchless_cpp(f"predict_tree_{i+1}_branchless")
    print(branchless_code)
    print()

# Function to print to both terminal and file
def dual_print(text, file_handle=None):
    print(text)
    if file_handle:
        file_handle.write(text + '\n')

# Generate complete forest prediction functions
print("\n" + "="*80)
print("COMPLETE FOREST PREDICTION FUNCTIONS")
print("="*80)

base_score = float(xgboost_model_data['learner']['learner_model_param']['base_score'])
num_features = int(xgboost_model_data['learner']['learner_model_param']['num_feature'])

# Create the cpp_code directory if it doesn't exist
os.makedirs("cpp_code", exist_ok=True)

# Open the output file for writing
with open("cpp_code/predict.cpp", 'w') as cpp_file:
    # Write C++ header comments
    dual_print(f"// Generated XGBoost prediction code", cpp_file)
    dual_print(f"// Forest with {len(forest)} trees, {num_features} features", cpp_file)
    dual_print(f"// Base score: {base_score}", cpp_file)
    dual_print("", cpp_file)
    
    # Also print these to terminal with formatting
    print(f"\n// Forest with {len(forest)} trees, {num_features} features")
    print(f"// Base score: {base_score}")

    # Naive forest prediction with inlined tree code
    print("\n//NAIVE FOREST PREDICTION (INLINED):")
    print("//" + "-" * 40)
    
    dual_print("//NAIVE FOREST PREDICTION (INLINED):", cpp_file)
    dual_print("//" + "-" * 40, cpp_file)
    dual_print("float predict_forest_naive(const float* features) {", cpp_file)
    dual_print("    float result = 0.0f;", cpp_file)
    dual_print("    float tree_result;", cpp_file)
    dual_print("", cpp_file)
    
    for i, tree in enumerate(forest):
        dual_print(f"    // Tree {i+1}", cpp_file)
        # Get the tree code and extract the body (remove function signature and braces)
        tree_code = tree.generate_naive_cpp(f"temp_tree_{i+1}")
        lines = tree_code.split('\n')
        # Skip first line (function signature) and last line (closing brace)
        tree_body = lines[1:-1]
        for line in tree_body:
            if line.strip().startswith('return'):
                # Replace return with assignment to tree_result
                value = line.strip().replace('return ', '').replace(';', '')
                dual_print(f"    tree_result = {value};", cpp_file)
            else:
                dual_print(f"    {line}", cpp_file)
        dual_print("    result += tree_result;", cpp_file)
        dual_print("", cpp_file)

    dual_print(f"    return result + {base_score}f;  // Add base score", cpp_file)
    dual_print("}", cpp_file)

    # Branchless forest prediction with inlined tree code
    print("\n//BRANCHLESS FOREST PREDICTION (INLINED):")
    print("//" + "-" * 40)
    
    dual_print("", cpp_file)
    dual_print("//BRANCHLESS FOREST PREDICTION (INLINED):", cpp_file)
    dual_print("//" + "-" * 40, cpp_file)
    dual_print("float predict_forest_branchless(const float* features) {", cpp_file)
    dual_print("    float result = 0.0f;", cpp_file)
    dual_print("", cpp_file)
    
    for i, tree in enumerate(forest):
        dual_print(f"    // Tree {i+1}", cpp_file)
        # Get the tree code and extract the body
        tree_code = tree.generate_branchless_cpp(f"temp_tree_{i+1}")
        lines = tree_code.split('\n')
        # Skip first line (function signature), second line (float result = 0.0f;), and last two lines
        tree_body = lines[2:-2]  # Skip signature, result declaration, return statement, and closing brace
        for line in tree_body:
            if line.strip() and not line.strip().startswith('//'):
                # Modify the line to add directly to the main result instead of tree's local result
                modified_line = line.replace('result +=', 'result +=')
                dual_print(f"    {modified_line}", cpp_file)
        dual_print("", cpp_file)

    dual_print(f"    return result + {base_score}f;  // Add base score", cpp_file)
    dual_print("}", cpp_file)

print(f"\nC++ code has been written to cpp_code/predict.cpp")