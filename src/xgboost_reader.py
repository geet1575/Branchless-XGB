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
        current_node = self.root
        while current_node.left_child_id != -1:  # While it's not a leaf node
            # Check if the feature value is less than the split condition
            if feature_values[current_node.split_index] < current_node.split_condition:
                current_node = current_node.left_child
            else:
                current_node = current_node.right_child
        # When the loop finishes, the current_node is a leaf node
        return current_node.split_condition

def create_trees_from_json(json_data):
    """
    Parses the XGBoost model JSON and returns a list of Tree objects.
    """
    tree_model_data_list = json_data['learner']['gradient_booster']['model']['trees']
    forest = []
    for tree_data in tree_model_data_list:
        forest.append(Tree(tree_data))
    return forest