"""
Exploratory Data Analysis (EDA) Module
=======================================
Reusable functions for data exploration and visualization.

Author: Home Credit Data Science Team
Date: 2025-11-11
"""

import logging
from typing import Dict, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os


def set_plot_style():
    """Set consistent plot styling."""
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['font.size'] = 10


def create_data_summary_report(tables: Dict[str, pd.DataFrame],
                               output_path: str) -> pd.DataFrame:
    """
    Create summary report for all tables.
    
    Args:
        tables: Dictionary of table DataFrames
        output_path: Path to save the report
        
    Returns:
        Summary DataFrame
    """
    logging.info("Creating data summary report...")
    
    summary_data = []
    
    for table_name, df in tables.items():
        if df is not None:
            summary_data.append({
                'table_name': table_name,
                'num_rows': len(df),
                'num_columns': len(df.columns),
                'memory_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
                'missing_cells': df.isnull().sum().sum(),
                'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
            })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Save report
    os.makedirs(output_path, exist_ok=True)
    report_path = os.path.join(output_path, 'data_summary.csv')
    summary_df.to_csv(report_path, index=False)
    
    logging.info(f"Data summary report saved to {report_path}")
    
    return summary_df


def analyze_missing_values(df: pd.DataFrame, 
                          table_name: str,
                          output_path: str) -> pd.DataFrame:
    """
    Analyze missing values in a DataFrame.
    
    Args:
        df: DataFrame to analyze
        table_name: Name of the table
        output_path: Path to save results
        
    Returns:
        DataFrame with missing value statistics
    """
    logging.info(f"Analyzing missing values for {table_name}...")
    
    missing_stats = pd.DataFrame({
        'column': df.columns,
        'missing_count': df.isnull().sum().values,
        'missing_percentage': (df.isnull().sum() / len(df) * 100).values,
        'dtype': df.dtypes.values
    }).sort_values('missing_percentage', ascending=False)
    
    # Save statistics
    os.makedirs(output_path, exist_ok=True)
    stats_path = os.path.join(output_path, f'{table_name}_missing_values.csv')
    missing_stats.to_csv(stats_path, index=False)
    
    # Create visualization
    set_plot_style()
    fig, ax = plt.subplots(figsize=(10, max(6, len(df.columns) * 0.3)))
    
    missing_pct = missing_stats[missing_stats['missing_percentage'] > 0]
    if len(missing_pct) > 0:
        ax.barh(missing_pct['column'], missing_pct['missing_percentage'])
        ax.set_xlabel('Missing Percentage (%)')
        ax.set_ylabel('Column')
        ax.set_title(f'Missing Values Analysis - {table_name}')
        plt.tight_layout()
        
        plot_path = os.path.join(output_path, f'{table_name}_missing_values.png')
        plt.savefig(plot_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        logging.info(f"Missing values plot saved to {plot_path}")
    else:
        plt.close()
        logging.info(f"No missing values found in {table_name}")
    
    return missing_stats


def analyze_numeric_columns(df: pd.DataFrame,
                           table_name: str,
                           output_path: str) -> pd.DataFrame:
    """
    Analyze numeric columns with descriptive statistics.
    
    Args:
        df: DataFrame to analyze
        table_name: Name of the table
        output_path: Path to save results
        
    Returns:
        DataFrame with statistics
    """
    logging.info(f"Analyzing numeric columns for {table_name}...")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) == 0:
        logging.info(f"No numeric columns found in {table_name}")
        return pd.DataFrame()
    
    # Get descriptive statistics
    stats_df = df[numeric_cols].describe().T
    stats_df['skewness'] = df[numeric_cols].skew()
    stats_df['kurtosis'] = df[numeric_cols].kurtosis()
    stats_df['missing_count'] = df[numeric_cols].isnull().sum()
    
    # Save statistics
    os.makedirs(output_path, exist_ok=True)
    stats_path = os.path.join(output_path, f'{table_name}_numeric_stats.csv')
    stats_df.to_csv(stats_path)
    
    logging.info(f"Numeric statistics saved to {stats_path}")
    
    return stats_df


def plot_numeric_distributions(df: pd.DataFrame,
                               table_name: str,
                               output_path: str,
                               max_plots: int = 20) -> None:
    """
    Create distribution plots for numeric columns.
    
    Args:
        df: DataFrame to plot
        table_name: Name of the table
        output_path: Path to save plots
        max_plots: Maximum number of plots to create
    """
    logging.info(f"Creating distribution plots for {table_name}...")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns[:max_plots]
    
    if len(numeric_cols) == 0:
        logging.info(f"No numeric columns to plot in {table_name}")
        return
    
    set_plot_style()
    n_cols = min(3, len(numeric_cols))
    n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 5, n_rows * 4))
    axes = axes.flatten() if n_rows > 1 or n_cols > 1 else [axes]
    
    for idx, col in enumerate(numeric_cols):
        ax = axes[idx]
        df[col].dropna().hist(bins=30, ax=ax, edgecolor='black', alpha=0.7)
        ax.set_title(f'{col}')
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
    
    # Hide empty subplots
    for idx in range(len(numeric_cols), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    
    # Save plot
    os.makedirs(output_path, exist_ok=True)
    plot_path = os.path.join(output_path, f'{table_name}_distributions.png')
    plt.savefig(plot_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    logging.info(f"Distribution plots saved to {plot_path}")


def analyze_categorical_columns(df: pd.DataFrame,
                                table_name: str,
                                output_path: str) -> pd.DataFrame:
    """
    Analyze categorical columns.
    
    Args:
        df: DataFrame to analyze
        table_name: Name of the table
        output_path: Path to save results
        
    Returns:
        DataFrame with categorical statistics
    """
    logging.info(f"Analyzing categorical columns for {table_name}...")
    
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    if len(categorical_cols) == 0:
        logging.info(f"No categorical columns found in {table_name}")
        return pd.DataFrame()
    
    stats_data = []
    
    for col in categorical_cols:
        unique_count = df[col].nunique()
        most_common = df[col].mode()[0] if len(df[col].mode()) > 0 else None
        most_common_freq = df[col].value_counts().iloc[0] if len(df[col]) > 0 else 0
        
        stats_data.append({
            'column': col,
            'unique_values': unique_count,
            'most_common': most_common,
            'most_common_frequency': most_common_freq,
            'missing_count': df[col].isnull().sum()
        })
    
    stats_df = pd.DataFrame(stats_data)
    
    # Save statistics
    os.makedirs(output_path, exist_ok=True)
    stats_path = os.path.join(output_path, f'{table_name}_categorical_stats.csv')
    stats_df.to_csv(stats_path, index=False)
    
    logging.info(f"Categorical statistics saved to {stats_path}")
    
    return stats_df


def plot_correlation_matrix(df: pd.DataFrame,
                           table_name: str,
                           output_path: str,
                           top_n: int = 30) -> None:
    """
    Create correlation matrix heatmap for numeric columns.
    
    Args:
        df: DataFrame to analyze
        table_name: Name of the table
        output_path: Path to save plot
        top_n: Maximum number of columns to include
    """
    logging.info(f"Creating correlation matrix for {table_name}...")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns[:top_n]
    
    if len(numeric_cols) < 2:
        logging.info(f"Not enough numeric columns for correlation matrix in {table_name}")
        return
    
    # Calculate correlation
    corr_matrix = df[numeric_cols].corr()
    
    # Create heatmap
    set_plot_style()
    fig, ax = plt.subplots(figsize=(min(15, len(numeric_cols)), min(12, len(numeric_cols) * 0.8)))
    
    sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
    
    ax.set_title(f'Correlation Matrix - {table_name}')
    plt.tight_layout()
    
    # Save plot
    os.makedirs(output_path, exist_ok=True)
    plot_path = os.path.join(output_path, f'{table_name}_correlation.png')
    plt.savefig(plot_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    logging.info(f"Correlation matrix saved to {plot_path}")


def analyze_target_variable(target_df: pd.DataFrame,
                           target_col: str,
                           output_path: str) -> pd.DataFrame:
    """
    Analyze target variable distribution.
    
    Args:
        target_df: DataFrame with target variable
        target_col: Name of target column
        output_path: Path to save results
        
    Returns:
        DataFrame with target distribution
    """
    logging.info("Analyzing target variable...")
    
    # Distribution
    distribution = target_df[target_col].value_counts().reset_index()
    distribution.columns = ['product_id', 'count']
    distribution['percentage'] = (distribution['count'] / distribution['count'].sum() * 100)
    
    # Save distribution
    os.makedirs(output_path, exist_ok=True)
    dist_path = os.path.join(output_path, 'target_distribution.csv')
    distribution.to_csv(dist_path, index=False)
    
    # Create plot
    set_plot_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.bar(distribution['product_id'].astype(str), distribution['count'])
    ax.set_xlabel('Product ID')
    ax.set_ylabel('Count')
    ax.set_title('Target Variable Distribution (Next Product Purchased)')
    ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    plot_path = os.path.join(output_path, 'target_distribution.png')
    plt.savefig(plot_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    logging.info(f"Target analysis saved to {output_path}")
    
    return distribution


def create_eda_summary(output_path: str) -> str:
    """
    Create a summary text file of all EDA findings.
    
    Args:
        output_path: Path to save summary
        
    Returns:
        Path to summary file
    """
    summary_path = os.path.join(output_path, 'eda_summary.txt')
    
    with open(summary_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("Exploratory Data Analysis Summary\n")
        f.write("Next Best Product Recommendation - Home Credit\n")
        f.write("="*80 + "\n\n")
        
        f.write("This directory contains the following EDA outputs:\n\n")
        f.write("1. data_summary.csv - Overview of all tables\n")
        f.write("2. *_missing_values.csv/png - Missing value analysis per table\n")
        f.write("3. *_numeric_stats.csv - Descriptive statistics for numeric columns\n")
        f.write("4. *_distributions.png - Distribution plots for numeric variables\n")
        f.write("5. *_categorical_stats.csv - Statistics for categorical columns\n")
        f.write("6. *_correlation.png - Correlation matrices\n")
        f.write("7. target_distribution.csv/png - Target variable analysis\n\n")
        
        f.write("Key Findings:\n")
        f.write("-" * 80 + "\n")
        f.write("(Populate this section after reviewing the analysis)\n\n")
    
    logging.info(f"EDA summary created at {summary_path}")
    
    return summary_path
