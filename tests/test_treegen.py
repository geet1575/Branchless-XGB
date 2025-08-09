import xgboost as xgb
from src.xgboost_reader import Node, Tree, create_trees_from_json
import numpy as np
import json
import argparse
import logging
from colorama import init, Fore, Style
from src.generate_random_xgb import train_random_xgb

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# Custom colored formatter for logging
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        record.msg = f"{log_color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

# Setup colored logging
def setup_logging(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with colored formatter
    console_handler = logging.StreamHandler()
    formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def test_single_model_prediction(model_path, num_test_arrays, logger):
    """
    Test a single XGBoost model against our custom tree implementation.
    
    Parameters:
    -----------
    model_path : str
        Path to the XGBoost model JSON file
    num_test_arrays : int
        Number of random test arrays to generate and test
    logger : logging.Logger
        Logger instance for colored output
        
    Returns:
    --------
    tuple : (int, int)
        Number of successful tests and total tests
    """
    logger.info(f"Testing model: {model_path}")
    
    try:
        # Load and parse the model
        with open(model_path, 'r') as f:
            xgboost_json_string = f.read()
        
        xgboost_model_data = json.loads(xgboost_json_string)
        forest = create_trees_from_json(xgboost_model_data)
        actual_xgb_model = xgb.Booster(model_file=model_path)
        num_features = actual_xgb_model.num_features()
        
        logger.info(f"Model loaded successfully - Features: {num_features}, Trees: {len(forest)}")
        
        # Extract model parameters
        base_score = float(xgboost_model_data['learner']['learner_model_param']['base_score'])
        eta = 1.0  # Default learning rate
        
        successful_tests = 0
        total_tests = num_test_arrays
        
        # Test multiple random arrays
        for i in range(num_test_arrays):
            # Generate random test vector with seed for reproducibility
            np.random.seed(i + 1)
            random_feature_vector = np.random.rand(num_features)
            
            # Get XGBoost prediction
            model_output = actual_xgb_model.predict(xgb.DMatrix(random_feature_vector.reshape(1, -1)))[0]
            
            # Get our custom forest prediction
            forest_output = base_score
            for tree in forest:
                tree_output = tree.predict(random_feature_vector)
                forest_output += eta * tree_output
            
            # Compare results
            if np.isclose(model_output, forest_output):
                successful_tests += 1
                logger.debug(f"Test {i+1}/{num_test_arrays}: PASS (XGB: {model_output:.6f}, Custom: {forest_output:.6f})")
            else:
                logger.error(f"Test {i+1}/{num_test_arrays}: FAIL (XGB: {model_output:.6f}, Custom: {forest_output:.6f}, Diff: {abs(model_output - forest_output):.6f})")
        
        if successful_tests == total_tests:
            logger.info(f"✓ All {total_tests} tests PASSED for {model_path}")
        else:
            logger.warning(f"⚠ {successful_tests}/{total_tests} tests passed for {model_path}")
            
        return successful_tests, total_tests
        
    except Exception as e:
        logger.error(f"Failed to test model {model_path}: {str(e)}")
        return 0, num_test_arrays


def run_comprehensive_test(num_models, num_arrays, logger):
    """
    Run comprehensive tests across multiple models and test arrays.
    
    Parameters:
    -----------
    num_models : int
        Number of XGBoost models to generate and test
    num_arrays : int
        Number of random test arrays per model
    logger : logging.Logger
        Logger instance for colored output
    """
    logger.info(f"Starting comprehensive test: {num_models} models × {num_arrays} test arrays each")
    
    total_successful = 0
    total_tests = 0
    
    for model_idx in range(num_models):
        logger.info(f"\n{'='*50}")
        logger.info(f"GENERATING MODEL {model_idx + 1}/{num_models}")
        logger.info(f"{'='*50}")
        
        # Generate a random XGBoost model with varying parameters
        model_seed = model_idx + 1
        num_features = np.random.randint(5, 20)  # 5-19 features
        n_estimators = np.random.randint(1, 10)  # 1-9 trees
        max_depth = np.random.randint(2, 6)      # 2-5 depth
        
        logger.info(f"Generating model with: features={num_features}, trees={n_estimators}, depth={max_depth}, seed={model_seed}")
        
        try:
            # Train and save model
            model, X, y = train_random_xgb(
                num_features=num_features,
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=model_seed
            )
            
            model_path = f"test_model_{model_idx + 1}.json"
            model.save_model(model_path)
            logger.info(f"Model saved to {model_path}")
            
            # Test the model
            successful, total = test_single_model_prediction(model_path, num_arrays, logger)
            total_successful += successful
            total_tests += total
            
            # Clean up model file
            import os
            os.remove(model_path)
            logger.debug(f"Cleaned up {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate/test model {model_idx + 1}: {str(e)}")
            total_tests += num_arrays
    
    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info(f"FINAL RESULTS")
    logger.info(f"{'='*60}")
    
    if total_successful == total_tests:
        logger.info(f"🎉 ALL TESTS PASSED! {total_successful}/{total_tests} tests successful")
    else:
        logger.warning(f"⚠ {total_successful}/{total_tests} tests passed ({100*total_successful/total_tests:.1f}%)")
        
    return total_successful == total_tests


def main():
    parser = argparse.ArgumentParser(
        description="Test XGBoost model predictions against custom tree implementation"
    )
    parser.add_argument(
        "--num-models", 
        type=int, 
        default=3,
        help="Number of XGBoost models to generate and test (default: 3)"
    )
    parser.add_argument(
        "--num-arrays", 
        type=int, 
        default=10,
        help="Number of random test arrays per model (default: 10)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose debug logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    logger.info("🚀 Starting BranchLessXGBoost Testing Suite")
    logger.info(f"Configuration: {args.num_models} models, {args.num_arrays} arrays per model")
    
    # Run the comprehensive test
    success = run_comprehensive_test(args.num_models, args.num_arrays, logger)
    
    if success:
        logger.info("\n✅ All tests completed successfully!")
        exit(0)
    else:
        logger.error("\n❌ Some tests failed!")
        exit(1)


if __name__ == "__main__":
    main()