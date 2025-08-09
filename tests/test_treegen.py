import xgboost as xgb
from src.xgboost_reader import Node, Tree, create_trees_from_json
import numpy as np
import json

file_name = "src/random_xgb_regressor.json"

xgboost_json_string =""

with open(file_name, 'r') as f:
    xgboost_json_string = f.read()

# Parse the JSON string
xgboost_model_data = json.loads(xgboost_json_string)

# Create a list of Tree objects
forest = create_trees_from_json(xgboost_model_data)

actual_xgb_model = xgb.Booster(model_file=file_name)    

num_features = actual_xgb_model.num_features()

random_feature_vector = np.random.rand(num_features)

model_output = actual_xgb_model.predict(xgb.DMatrix(random_feature_vector.reshape(1, -1)))


# pull params from the JSON you already loaded
base_score = float(xgboost_model_data['learner']['learner_model_param']['base_score'])
# learning rate sometimes lives here in modern JSON dumps:
# eta = float(
    # xgboost_model_data['learner']['gradient_booster']['gbtree_train_param'].get('learning_rate', 1.0)
# )
eta = 1.0
forest_output = base_score

for tree in forest:
    tree_output = tree.predict(random_feature_vector)
    forest_output += eta * tree_output

if np.isclose(model_output, forest_output):
    print("The XGBoost model output matches the forest output.")
else:
    print("The XGBoost model output does NOT match the forest output.")
    print(f"XGBoost model output: {model_output}")
    print(f"Forest output: {forest_output}")