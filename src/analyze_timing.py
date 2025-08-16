#!/usr/bin/env python3
"""
Timing Analysis Script for BranchLessXGBoost Benchmarks

Reads timing data from naive_times.txt and branchless_times.txt,
generates distribution graphs and statistical summaries.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path

def read_timing_file(filepath):
    """Read timing data from a text file."""
    try:
        with open(filepath, 'r') as f:
            times = [float(line.strip()) for line in f if line.strip()]
        return np.array(times)
    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
        return None
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def calculate_statistics(times):
    """Calculate statistical measures for timing data."""
    stats = {
        'mean': np.mean(times),
        'std': np.std(times),
        'p50': np.percentile(times, 50),
        'p90': np.percentile(times, 90),
        'p99_9': np.percentile(times, 99.9),
        'min': np.min(times),
        'max': np.max(times),
        'count': len(times)
    }
    return stats

def plot_percentile_distribution(times, title, output_path, unit="cycles"):
    """Plot percentile vs timing distribution."""
    # Calculate percentiles from 0 to 100
    percentiles = np.linspace(0, 100, 1000)
    timing_values = np.percentile(times, percentiles)
    
    plt.figure(figsize=(12, 8))
    plt.plot(percentiles, timing_values, linewidth=2, color='blue')
    plt.xlabel('Percentile (%)', fontsize=12)
    plt.ylabel(f'Timing ({unit})', fontsize=12)
    plt.title(f'{title} - Percentile Distribution', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Add vertical lines for key percentiles
    key_percentiles = [50, 90, 99.9]
    colors = ['green', 'orange', 'red']
    for p, color in zip(key_percentiles, colors):
        value = np.percentile(times, p)
        plt.axvline(x=p, color=color, linestyle='--', alpha=0.7, linewidth=1)
        plt.axhline(y=value, color=color, linestyle='--', alpha=0.7, linewidth=1)
        plt.text(p + 1, value, f'P{p}: {value:.1f}{unit}', 
                verticalalignment='bottom', fontsize=10, color=color)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved distribution plot: {output_path}")

def plot_histogram(times, title, output_path, unit="cycles"):
    """Plot histogram of timing data."""
    plt.figure(figsize=(12, 8))
    plt.hist(times, bins=100, alpha=0.7, color='skyblue', edgecolor='black')
    plt.xlabel(f'Timing ({unit})', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title(f'{title} - Timing Distribution Histogram', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Add vertical lines for mean and key percentiles
    mean_val = np.mean(times)
    p50_val = np.percentile(times, 50)
    p90_val = np.percentile(times, 90)
    p99_9_val = np.percentile(times, 99.9)
    
    plt.axvline(x=mean_val, color='red', linestyle='-', linewidth=2, label=f'Mean: {mean_val:.1f}{unit}')
    plt.axvline(x=p50_val, color='green', linestyle='--', linewidth=2, label=f'P50: {p50_val:.1f}{unit}')
    plt.axvline(x=p90_val, color='orange', linestyle='--', linewidth=2, label=f'P90: {p90_val:.1f}{unit}')
    plt.axvline(x=p99_9_val, color='purple', linestyle='--', linewidth=2, label=f'P99.9: {p99_9_val:.1f}{unit}')
    
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved histogram plot: {output_path}")

def print_statistics(stats, name, unit="cycles"):
    """Print statistical summary."""
    print(f"\n=== {name} Statistics ===")
    print(f"Count:      {stats['count']:,} samples")
    print(f"Mean:       {stats['mean']:.2f} {unit}")
    print(f"Std Dev:    {stats['std']:.2f} {unit}")
    print(f"Min:        {stats['min']:.2f} {unit}")
    print(f"Max:        {stats['max']:.2f} {unit}")
    print(f"P50:        {stats['p50']:.2f} {unit}")
    print(f"P90:        {stats['p90']:.2f} {unit}")
    print(f"P99.9:      {stats['p99_9']:.2f} {unit}")

def plot_comparison(naive_times, branchless_times, output_path, unit="cycles"):
    """Plot comparison of both implementations."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Percentile comparison
    percentiles = np.linspace(0, 100, 1000)
    naive_values = np.percentile(naive_times, percentiles)
    branchless_values = np.percentile(branchless_times, percentiles)
    
    ax1.plot(percentiles, naive_values, linewidth=2, color='red', label='Naive', alpha=0.8)
    ax1.plot(percentiles, branchless_values, linewidth=2, color='blue', label='Branchless', alpha=0.8)
    ax1.set_xlabel('Percentile (%)', fontsize=12)
    ax1.set_ylabel(f'Timing ({unit})', fontsize=12)
    ax1.set_title('Percentile Distribution Comparison', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Box plot comparison
    ax2.boxplot([naive_times, branchless_times], labels=['Naive', 'Branchless'])
    ax2.set_ylabel(f'Timing ({unit})', fontsize=12)
    ax2.set_title('Box Plot Comparison', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved comparison plot: {output_path}")

def main():
    # Get script directory and set up paths
    script_dir = Path(__file__).parent
    cpp_code_dir = script_dir / "cpp_code"
    images_dir = script_dir.parent / "images"
    
    # Create images directory if it doesn't exist
    images_dir.mkdir(exist_ok=True)
    
    # File paths
    naive_file = cpp_code_dir / "naive_times.txt"
    branchless_file = cpp_code_dir / "branchless_times.txt"
    
    print("BranchLessXGBoost Timing Analysis")
    print("=" * 40)
    
    # Read timing data
    print(f"Reading timing data from {naive_file} and {branchless_file}")
    naive_times = read_timing_file(naive_file)
    branchless_times = read_timing_file(branchless_file)
    
    if naive_times is None or branchless_times is None:
        print("Error: Could not read timing files. Please run the benchmarks first.")
        sys.exit(1)
    
    print(f"Loaded {len(naive_times)} naive samples and {len(branchless_times)} branchless samples")
    
    # Using cycles as the measurement unit
    unit = "cycles"
    
    # Calculate statistics
    naive_stats = calculate_statistics(naive_times)
    branchless_stats = calculate_statistics(branchless_times)
    
    # Print statistics
    print_statistics(naive_stats, "Naive Implementation", unit)
    print_statistics(branchless_stats, "Branchless Implementation", unit)
    
    # Performance comparison
    print(f"\n=== Performance Comparison ===")
    speedup_mean = naive_stats['mean'] / branchless_stats['mean']
    speedup_p50 = naive_stats['p50'] / branchless_stats['p50']
    speedup_p90 = naive_stats['p90'] / branchless_stats['p90']
    speedup_p99_9 = naive_stats['p99_9'] / branchless_stats['p99_9']
    
    print(f"Speedup (Naive/Branchless):")
    print(f"  Mean:   {speedup_mean:.2f}x")
    print(f"  P50:    {speedup_p50:.2f}x")
    print(f"  P90:    {speedup_p90:.2f}x")
    print(f"  P99.9:  {speedup_p99_9:.2f}x")
    
    # Generate plots
    print(f"\n=== Generating Plots ===")
    
    # Individual distribution plots
    plot_percentile_distribution(naive_times, "Naive Implementation", 
                               images_dir / "naive_percentile_distribution.png", unit)
    plot_percentile_distribution(branchless_times, "Branchless Implementation", 
                               images_dir / "branchless_percentile_distribution.png", unit)
    
    # Individual histograms
    plot_histogram(naive_times, "Naive Implementation", 
                  images_dir / "naive_histogram.png", unit)
    plot_histogram(branchless_times, "Branchless Implementation", 
                  images_dir / "branchless_histogram.png", unit)
    
    # Comparison plot
    plot_comparison(naive_times, branchless_times, 
                   images_dir / "comparison.png", unit)
    
    print(f"\nAll plots saved to: {images_dir}")
    print("Analysis complete!")

if __name__ == "__main__":
    main()