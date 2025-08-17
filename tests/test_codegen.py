# Standard library imports
import argparse
import json
import logging
import os
import subprocess
import sys
import random

# Third-party imports
import numpy as np
import pandas as pd
import xgboost as xgb
from colorama import init, Fore, Style

# Local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from xgboost_reader import Node, Tree, create_trees_from_json
from generate_random_xgb import train_random_xgb

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

def run_command(cmd, cwd=None, verbose=False):
    """Run a shell command and return success status and output"""
    try:
        if verbose:
            logging.info(f"Running: {cmd}")
        
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            check=True
        )
        
        if verbose and result.stdout:
            logging.debug(f"stdout: {result.stdout}")
        
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {cmd}")
        logging.error(f"Return code: {e.returncode}")
        logging.error(f"stderr: {e.stderr}")
        if e.stdout:
            logging.error(f"stdout: {e.stdout}")
        return False, e.stderr

def compare_csv_predictions(xgb_file, naive_file, branchless_file, tolerance=1e-5):
    """Compare predictions from three CSV files and check if they're within tolerance"""
    try:
        # Read the CSV files
        xgb_df = pd.read_csv(xgb_file)
        naive_df = pd.read_csv(naive_file)
        branchless_df = pd.read_csv(branchless_file)
        
        # Extract prediction columns
        xgb_preds = xgb_df['prediction'].values
        naive_preds = naive_df['prediction'].values
        branchless_preds = branchless_df['prediction'].values
        
        # Check lengths match
        if not (len(xgb_preds) == len(naive_preds) == len(branchless_preds)):
            logging.error(f"Length mismatch: XGB={len(xgb_preds)}, Naive={len(naive_preds)}, Branchless={len(branchless_preds)}")
            return False, "Length mismatch"
        
        # Compare XGBoost vs Naive
        xgb_naive_diff = np.abs(xgb_preds - naive_preds)
        xgb_naive_max_diff = np.max(xgb_naive_diff)
        xgb_naive_close = np.allclose(xgb_preds, naive_preds, atol=tolerance, rtol=tolerance)
        
        # Compare XGBoost vs Branchless
        xgb_branchless_diff = np.abs(xgb_preds - branchless_preds)
        xgb_branchless_max_diff = np.max(xgb_branchless_diff)
        xgb_branchless_close = np.allclose(xgb_preds, branchless_preds, atol=tolerance, rtol=tolerance)
        
        # Compare Naive vs Branchless (should be identical)
        naive_branchless_diff = np.abs(naive_preds - branchless_preds)
        naive_branchless_max_diff = np.max(naive_branchless_diff)
        naive_branchless_close = np.allclose(naive_preds, branchless_preds, atol=tolerance, rtol=tolerance)
        
        # Create comparison report
        report = {
            'num_samples': len(xgb_preds),
            'xgb_vs_naive': {
                'max_diff': xgb_naive_max_diff,
                'close': xgb_naive_close
            },
            'xgb_vs_branchless': {
                'max_diff': xgb_branchless_max_diff,
                'close': xgb_branchless_close
            },
            'naive_vs_branchless': {
                'max_diff': naive_branchless_max_diff,
                'close': naive_branchless_close
            }
        }
        
        # All comparisons should pass
        all_close = xgb_naive_close and xgb_branchless_close and naive_branchless_close
        
        return all_close, report
        
    except Exception as e:
        logging.error(f"Error comparing CSV files: {e}")
        return False, str(e)

def test_single_model(num_features, n_estimators, max_depth, num_samples, verbose=False):
    """Test a single randomly generated XGBoost model through the complete pipeline"""
    
    logging.info(f"Testing model: {num_features} features, {n_estimators} trees, depth {max_depth}, {num_samples} samples")
    
    # Step 1: Generate random XGBoost model with test data
    cmd = f"python3 src/generate_random_xgb.py --num-features {num_features} --n-estimators {n_estimators} --max-depth {max_depth} --num-samples {num_samples}"
    success, output = run_command(cmd, verbose=verbose)
    if not success:
        return False, "Failed to generate XGBoost model"
    
    # Step 2: Generate C++ code from the model (run from src directory)
    cmd = "python3 generate_code.py"
    success, output = run_command(cmd, cwd="src", verbose=verbose)
    if not success:
        return False, "Failed to generate C++ code"
    
    # Step 3: Build C++ predictors
    cmd = "make clean && make all"
    success, output = run_command(cmd, cwd="src/cpp_code", verbose=verbose)
    if not success:
        return False, "Failed to build C++ predictors"
    
    # Step 4: Run both predictors
    cmd = "./predictor_naive"
    success, output = run_command(cmd, cwd="src/cpp_code", verbose=verbose)
    if not success:
        return False, "Failed to run naive predictor"
    
    cmd = "./predictor_branchless"
    success, output = run_command(cmd, cwd="src/cpp_code", verbose=verbose)
    if not success:
        return False, "Failed to run branchless predictor"
    
    # Step 5: Compare outputs
    xgb_file = "data/xgboost_outputs.csv"
    naive_file = "data/naive_outputs.csv"
    branchless_file = "data/branchless_outputs.csv"
    
    # Check that all files exist
    for file_path in [xgb_file, naive_file, branchless_file]:
        if not os.path.exists(file_path):
            return False, f"Missing output file: {file_path}"
    
    # Compare predictions
    all_close, report = compare_csv_predictions(xgb_file, naive_file, branchless_file)
    
    if all_close:
        logging.info(f"✅ All predictions match within tolerance")
        if verbose:
            logging.debug(f"Comparison report: {report}")
        return True, report
    else:
        logging.error(f"❌ Predictions don't match")
        logging.error(f"Comparison report: {report}")
        return False, report

def main():
    parser = argparse.ArgumentParser(
        description="Test C++ code generation and prediction accuracy for random XGBoost models"
    )
    parser.add_argument(
        "--num-tests", type=int, default=100,
        help="Number of random models to test"
    )
    parser.add_argument(
        "--min-features", type=int, default=3,
        help="Minimum number of features"
    )
    parser.add_argument(
        "--max-features", type=int, default=50,
        help="Maximum number of features"
    )
    parser.add_argument(
        "--min-trees", type=int, default=30,
        help="Minimum number of trees"
    )
    parser.add_argument(
        "--max-trees", type=int, default=100,
        help="Maximum number of trees"
    )
    parser.add_argument(
        "--min-depth", type=int, default=1,
        help="Minimum tree depth"
    )
    parser.add_argument(
        "--max-depth", type=int, default=5,
        help="Maximum tree depth"
    )
    parser.add_argument(
        "--min-samples", type=int, default=100,
        help="Minimum number of test samples"
    )
    parser.add_argument(
        "--max-samples", type=int, default=200,
        help="Maximum number of test samples"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose output and debug logging"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducible tests"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    # Set random seed for reproducible tests
    random.seed(args.seed)
    np.random.seed(args.seed)
    
    logging.info(f"🚀 Starting C++ code generation tests")
    logging.info(f"📊 Testing {args.num_tests} random models")
    logging.info(f"🔧 Features: {args.min_features}-{args.max_features}, Trees: {args.min_trees}-{args.max_trees}, Depth: {args.min_depth}-{args.max_depth}")
    logging.info(f"📝 Samples: {args.min_samples}-{args.max_samples}")
    
    # Test results tracking
    passed_tests = 0
    failed_tests = 0
    test_reports = []
    
    for test_num in range(1, args.num_tests + 1):
        logging.info(f"\n{'='*60}")
        logging.info(f"🧪 TEST {test_num}/{args.num_tests}")
        logging.info(f"{'='*60}")
        
        # Generate random test parameters
        num_features = random.randint(args.min_features, args.max_features)
        n_estimators = random.randint(args.min_trees, args.max_trees)
        max_depth = random.randint(args.min_depth, args.max_depth)
        num_samples = random.randint(args.min_samples, args.max_samples)
        
        # Run the test
        success, report = test_single_model(
            num_features, n_estimators, max_depth, num_samples, args.verbose
        )
        
        test_config = {
            'test_num': test_num,
            'num_features': num_features,
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'num_samples': num_samples,
            'success': success,
            'report': report
        }
        test_reports.append(test_config)
        
        if success:
            passed_tests += 1
            logging.info(f"✅ Test {test_num} PASSED")
        else:
            failed_tests += 1
            logging.error(f"❌ Test {test_num} FAILED: {report}")
    
    # Final summary
    logging.info(f"\n{'='*60}")
    logging.info(f"📊 FINAL RESULTS")
    logging.info(f"{'='*60}")
    logging.info(f"✅ Passed: {passed_tests}/{args.num_tests}")
    logging.info(f"❌ Failed: {failed_tests}/{args.num_tests}")
    
    if failed_tests == 0:
        logging.info(f"🎉 All tests passed!")
        return 0
    else:
        logging.error(f"💥 {failed_tests} tests failed")
        
        # Show failed test details
        logging.error(f"\n📋 Failed test details:")
        for test_config in test_reports:
            if not test_config['success']:
                logging.error(f"Test {test_config['test_num']}: {test_config['num_features']}f, {test_config['n_estimators']}t, {test_config['max_depth']}d, {test_config['num_samples']}s")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())