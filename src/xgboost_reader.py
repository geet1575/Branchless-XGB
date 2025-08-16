# xgboost_reader.py

class Node:
    """
    Represents a single node within an XGBoost tree.
    """
    def __init__(self, node_id, left_child_id, right_child_id, parent_id, 
                 split_index, split_condition, default_left, loss_change, 
                 sum_hessian, base_weight):
        self.node_id = node_id
        self.left_child_id = left_child_id
        self.right_child_id = right_child_id
        self.parent_id = parent_id
        self.split_index = split_index
        self.split_condition = split_condition
        self.default_left = default_left
        self.loss_change = loss_change
        self.sum_hessian = sum_hessian
        self.base_weight = base_weight
        self.left_child = None
        self.right_child = None
        
        # ========== NEW ATTRIBUTE ==========
        # This will be set to 'yes', 'no', or 'root' during tree construction.
        self.path_from_parent = None 
        self.true_or_false = None 
        # =================================

    def __repr__(self):
        # Leaf nodes have a leaf_value, internal nodes have a split condition.
        if self.left_child_id == -1: # It's a leaf node
            return f"""Node(id={self.node_id}, y/n={self.path_from_parent}, true/false={self.true_or_false if self.true_or_false is not None else 
            'root'} leaf_value={self.split_condition})"""
        else: # It's a split node
            return (f"""Node(id={self.node_id}, y/n={self.path_from_parent}, true/false={self.true_or_false if self.true_or_false else 'root'}, feature_{self.split_index} < {self.split_condition})""")

class Tree:
    """
    Represents a single decision tree from an XGBoost model.
    """
    def __init__(self, tree_data):
        self.tree_id = tree_data.get('id', 'N/A')
        self.nodes = {}
        self._build_tree(tree_data)
        self.root = self.nodes.get(0)

    # ========== MODIFIED FUNCTION START ==========
    def _build_tree(self, tree_data):
        """
        Constructs the tree from the provided tree data.
        """
        num_nodes = len(tree_data['left_children'])
        
        # First, create all node objects
        for i in range(num_nodes):
            is_leaf = tree_data['left_children'][i] == -1
            node = Node(
                node_id=i,
                left_child_id=tree_data['left_children'][i],
                right_child_id=tree_data['right_children'][i],
                parent_id=tree_data['parents'][i],
                split_index=tree_data['split_indices'][i] if not is_leaf else None,
                split_condition=tree_data['split_conditions'][i],
                default_left=tree_data['default_left'][i] != 0,
                loss_change=tree_data['loss_changes'][i],
                sum_hessian=tree_data['sum_hessian'][i],
                base_weight=tree_data['base_weights'][i] if i < len(tree_data['base_weights']) else None
            )
            self.nodes[i] = node

        # Second, link nodes and set the new 'path_from_parent' attribute
        for i in range(num_nodes):
            node = self.nodes[i]
            if not node.left_child_id == -1:
                left_child_node = self.nodes[node.left_child_id]
                node.left_child = left_child_node
                left_child_node.path_from_parent = "yes"  # Left child is the 'yes' path
                left_child_node.true_or_false = True  # True for left child

            if not node.right_child_id == -1:
                right_child_node = self.nodes[node.right_child_id]
                node.right_child = right_child_node
                right_child_node.path_from_parent = "no" # Right child is the 'no' path
                right_child_node.true_or_false = False  # False for right child

        # Set the path for the root node
        if self.nodes.get(0):
            self.nodes.get(0).path_from_parent = "root"
    # ========== MODIFIED FUNCTION END ==========

    def print_tree(self, node=None, prefix="", is_left=None):
        """
        Prints a visual representation of the tree structure with explicit
        'yes' and 'no' paths.
        """
        if not node:
            node = self.root
        if node is None:
            print("Tree is empty.")
            return
        if node.right_child:
            self.print_tree(node.right_child, prefix + ("│      " if is_left else "       "), False)
        if is_left is True:
            connector = f"└── [{node.path_from_parent}] "
        elif is_left is False:
            connector = f"┌── [{node.path_from_parent}] "
        else:
            connector = f"[{node.path_from_parent}] "
        print(prefix + connector + str(node))
        if node.left_child:
            self.print_tree(node.left_child, prefix + ("       " if is_left else "│      "), True)

    def predict(self, feature_values):
        """
        Calculates the output of the tree for a given array of feature values.

        Args:
            feature_values: A list or array of values for the input features.

        Returns:
            The prediction value from the leaf node.
        """
        import numpy as np
        
        current_node = self.root
        while current_node.left_child_id != -1:  # While it's not a leaf node
            # XGBoost uses single-precision (float32) for split comparisons internally
            # This avoids precision issues when loading models from JSON format
            # Sources: https://github.com/dmlc/xgboost/issues/4097
            #          https://github.com/dmlc/xgboost/issues/4060
            feature_val = np.float32(feature_values[current_node.split_index])
            split_cond = np.float32(current_node.split_condition)
            
            # Check if the feature value is less than the split condition
            if feature_val < split_cond:
                current_node = current_node.left_child
            else:
                current_node = current_node.right_child
        # When the loop finishes, the current_node is a leaf node
        return current_node.split_condition

    def generate_naive_cpp(self, function_name="predict_tree"):
        """
        Generates naive C++ code with if/else conditionals for tree prediction.
        
        Args:
            function_name: Name of the generated C++ function
            
        Returns:
            String containing the C++ function code
        """
        code_lines = []
        code_lines.append(f"float {function_name}(const float* features) {{")
        
        def generate_node_code(node, indent_level=1):
            """Recursively generate code for each node"""
            indent = "    " * indent_level
            
            if node.left_child_id == -1:  # Leaf node
                code_lines.append(f"{indent}return {node.split_condition}f;")
            else:  # Split node
                code_lines.append(f"{indent}if (features[{node.split_index}] < {node.split_condition}f) {{")
                generate_node_code(node.left_child, indent_level + 1)
                code_lines.append(f"{indent}}} else {{")
                generate_node_code(node.right_child, indent_level + 1)
                code_lines.append(f"{indent}}}")
        
        if self.root:
            generate_node_code(self.root)
        else:
            code_lines.append("    return 0.0f;  // Empty tree")
            
        code_lines.append("}")
        return "\n".join(code_lines)

    def generate_branchless_cpp(self, function_name="predict_tree_branchless"):
        """
        Generates branchless C++ code using mathematical expressions for tree prediction.
        
        Args:
            function_name: Name of the generated C++ function
            
        Returns:
            String containing the branchless C++ function code
        """
        code_lines = []
        code_lines.append(f"float {function_name}(const float* features) {{")
        code_lines.append("    float result = 0.0f;")
        
        # Collect all paths from root to leaves
        leaf_paths = []
        
        def collect_paths(node, current_path=[]):
            """Collect all paths from root to leaves with their conditions"""
            if node.left_child_id == -1:  # Leaf node
                leaf_paths.append({
                    'conditions': current_path.copy(),
                    'value': node.split_condition
                })
            else:  # Split node
                # Left path (condition is true: feature < split_condition)
                left_condition = {
                    'feature': node.split_index,
                    'threshold': node.split_condition,
                    'is_less_than': True
                }
                collect_paths(node.left_child, current_path + [left_condition])
                
                # Right path (condition is false: feature >= split_condition)
                right_condition = {
                    'feature': node.split_index,
                    'threshold': node.split_condition,
                    'is_less_than': False
                }
                collect_paths(node.right_child, current_path + [right_condition])
        
        if self.root:
            collect_paths(self.root)
            
            # Generate branchless code for each path
            for i, path in enumerate(leaf_paths):
                if not path['conditions']:  # Root is leaf
                    code_lines.append(f"    result += {path['value']}f;")
                else:
                    # Build the condition expression
                    condition_parts = []
                    for condition in path['conditions']:
                        if condition['is_less_than']:
                            condition_parts.append(f"(features[{condition['feature']}] < {condition['threshold']}f)")
                        else:
                            condition_parts.append(f"(features[{condition['feature']}] >= {condition['threshold']}f)")
                    
                    # Combine all conditions with AND
                    full_condition = " && ".join(condition_parts)
                    code_lines.append(f"    result += ({full_condition}) * {path['value']}f;")
        else:
            code_lines.append("    // Empty tree")
            
        code_lines.append("    return result;")
        code_lines.append("}")
        return "\n".join(code_lines)

def create_trees_from_json(json_data):
    """
    Parses the XGBoost model JSON and returns a list of Tree objects.
    """
    tree_model_data_list = json_data['learner']['gradient_booster']['model']['trees']
    forest = []
    for tree_data in tree_model_data_list:
        forest.append(Tree(tree_data))
    return forest