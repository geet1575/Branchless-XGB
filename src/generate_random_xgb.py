import argparse
import numpy as np
from xgboost import XGBRegressor

def train_random_xgb(
    num_features=10,
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
):
    """
    Train an XGBoost regressor on a synthetic random dataset.

    Parameters
    ----------
    num_features : int
        Number of input features (columns) to generate.
    n_estimators : int
        Number of trees (boosting rounds).
    max_depth : int
        Maximum tree depth for base learners.
    learning_rate : float
        Step size shrinkage used in update to prevent overfitting.
    subsample : float
        Subsample ratio of the training instances.
    colsample_bytree : float
        Subsample ratio of columns when constructing each tree.
    random_state : int
        Seed for reproducibility.

    Returns
    -------
    model : XGBRegressor
        Trained XGBoost model.
    X : ndarray
        The synthetic features used for training.
    y : ndarray
        The synthetic targets used for training.
    """
    # 1) Generate synthetic data
    np.random.seed(random_state)
    X = np.random.rand(200, num_features)       # 200 samples × num_features
    y = np.random.rand(200)                     # continuous targets for regression

    # 2) Instantiate the model for regression w/ RMSE
    model = XGBRegressor(
        objective='reg:squarederror',
        eval_metric='rmse',
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        random_state=random_state
    )

    # 3) Train
    model.fit(X, y)

    return model, X, y

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train a random XGBoost regressor on synthetic data"
    )
    parser.add_argument(
        "--num-features", type=int, default=10,
        help="Number of features in the synthetic dataset"
    )
    parser.add_argument(
        "--n_estimators", type=int, default=100,
        help="Number of trees (boosting rounds)"
    )
    parser.add_argument(
        "--max_depth", type=int, default=3,
        help="Maximum tree depth"
    )
    parser.add_argument(
        "--learning_rate", type=float, default=0.1,
        help="Learning rate (eta)"
    )
    parser.add_argument(
        "--random_state", type=int, default=42,
        help="Random seed for reproducibility"
    )
    args = parser.parse_args()

    model, X, y = train_random_xgb(
        num_features=args.num_features,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        learning_rate=args.learning_rate,
        random_state=args.random_state
    )

    print("Trained XGBoost regressor with parameters:")
    for k, v in vars(args).items():
        print(f"  - {k}: {v}")

    # Save to JSON
    output_path = "random_xgb_regressor.json"
    model.save_model(output_path)
    print(f"Model saved to {output_path}")
