"""
Feature Engineering Module
===========================
Reusable functions for creating features for personalization use cases.

Author: Home Credit Data Science Team
Date: 2025-11-11
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_customer_demographic_features(party_df: pd.DataFrame,
                                         customer_df: pd.DataFrame,
                                         address_df: pd.DataFrame,
                                         reference_date: str) -> pd.DataFrame:
    """
    Create demographic features for customers.
    
    Args:
        party_df: Party table DataFrame
        customer_df: Customer table DataFrame
        address_df: Address table DataFrame
        reference_date: Reference date for age calculation
        
    Returns:
        DataFrame with demographic features
    """
    logging.info("Creating demographic features...")
    
    # Merge customer with party
    df = customer_df.merge(party_df, on='PARTYID', how='left')
    
    # Merge with address
    df = df.merge(address_df, left_on='PRIMARYADDRESSID', right_on='ADDRESSID', how='left')
    
    # Calculate age
    ref_date = pd.to_datetime(reference_date)
    df['DATEOFBIRTH'] = pd.to_datetime(df['DATEOFBIRTH'])
    df['AGE'] = (ref_date - df['DATEOFBIRTH']).dt.days / 365.25
    
    # Calculate customer tenure (in days)
    df['CUSTOMERESTABLISHEDDATE'] = pd.to_datetime(df['CUSTOMERESTABLISHEDDATE'])
    df['CUSTOMER_TENURE_DAYS'] = (ref_date - df['CUSTOMERESTABLISHEDDATE']).dt.days
    
    # Age group
    df['AGE_GROUP'] = pd.cut(df['AGE'], 
                             bins=[0, 25, 35, 45, 55, 65, 100],
                             labels=['18-25', '26-35', '36-45', '46-55', '56-65', '65+'])
    
    # Tenure group
    df['TENURE_GROUP'] = pd.cut(df['CUSTOMER_TENURE_DAYS'],
                                bins=[-1, 180, 365, 730, 1825, 999999],
                                labels=['0-6M', '6M-1Y', '1-2Y', '2-5Y', '5Y+'])
    
    # Select relevant features
    feature_cols = [
        'CUSTOMERID', 'PARTYID', 'AGE', 'CUSTOMER_TENURE_DAYS',
        'AGE_GROUP', 'TENURE_GROUP', 'CITY', 'STATE', 'POSTALCODE'
    ]
    
    features = df[feature_cols].copy()
    
    logging.info(f"Created {len(feature_cols)} demographic features for {len(features)} customers")
    
    return features


def create_account_features(customer_account_df: pd.DataFrame,
                            product_df: pd.DataFrame,
                            channel_df: pd.DataFrame,
                            reference_date: str) -> pd.DataFrame:
    """
    Create account-level aggregated features.
    
    Args:
        customer_account_df: Customer account table DataFrame
        product_df: Banking product table DataFrame
        channel_df: Channel table DataFrame
        reference_date: Reference date for calculations
        
    Returns:
        DataFrame with account features per customer
    """
    logging.info("Creating account features...")
    
    # Merge with product and channel info
    df = customer_account_df.merge(product_df, on='PRODUCTID', how='left')
    df = df.merge(channel_df, on='CHANNELID', how='left')
    
    # Convert dates
    ref_date = pd.to_datetime(reference_date)
    df['ORIGINATIONDATE'] = pd.to_datetime(df['ORIGINATIONDATE'])
    df['MATURITYDATE'] = pd.to_datetime(df['MATURITYDATE'])
    
    # Calculate account age
    df['ACCOUNT_AGE_DAYS'] = (ref_date - df['ORIGINATIONDATE']).dt.days
    
    # Days until maturity (negative if already matured)
    df['DAYS_TO_MATURITY'] = (df['MATURITYDATE'] - ref_date).dt.days
    
    # Active accounts
    df['IS_ACTIVE'] = (df['ACCOUNTSTATUS'] == 'ACTIVE').astype(int)
    
    # Aggregate by customer
    agg_features = df.groupby('CUSTOMERID').agg({
        'CUSTOMERACCOUNTID': 'count',  # Total number of accounts
        'IS_ACTIVE': 'sum',  # Number of active accounts
        'PRINCIPALAMOUNT': ['sum', 'mean', 'max'],
        'INTERESTRATE': ['mean', 'min', 'max'],
        'ACCOUNT_AGE_DAYS': ['mean', 'min', 'max'],
        'PRODUCTID': 'nunique',  # Number of unique products
        'CHANNELID': 'nunique'  # Number of unique channels
    }).reset_index()
    
    # Flatten column names
    agg_features.columns = ['CUSTOMERID', 
                           'TOTAL_ACCOUNTS',
                           'ACTIVE_ACCOUNTS',
                           'TOTAL_PRINCIPAL',
                           'AVG_PRINCIPAL',
                           'MAX_PRINCIPAL',
                           'AVG_INTEREST_RATE',
                           'MIN_INTEREST_RATE',
                           'MAX_INTEREST_RATE',
                           'AVG_ACCOUNT_AGE_DAYS',
                           'MIN_ACCOUNT_AGE_DAYS',
                           'MAX_ACCOUNT_AGE_DAYS',
                           'NUM_UNIQUE_PRODUCTS',
                           'NUM_UNIQUE_CHANNELS']
    
    # Calculate additional derived features
    agg_features['INACTIVE_ACCOUNTS'] = agg_features['TOTAL_ACCOUNTS'] - agg_features['ACTIVE_ACCOUNTS']
    agg_features['ACTIVE_ACCOUNT_RATIO'] = agg_features['ACTIVE_ACCOUNTS'] / agg_features['TOTAL_ACCOUNTS']
    
    logging.info(f"Created {len(agg_features.columns)-1} account features for {len(agg_features)} customers")
    
    return agg_features


def create_transaction_features(transaction_df: pd.DataFrame,
                                customer_account_df: pd.DataFrame,
                                reference_date: str,
                                lookback_periods: Dict[str, int]) -> pd.DataFrame:
    """
    Create transaction-based behavioral features.
    
    Args:
        transaction_df: Transaction table DataFrame
        customer_account_df: Customer account table DataFrame
        reference_date: Reference date for lookback
        lookback_periods: Dictionary with lookback periods (e.g., {'short': 30, 'medium': 90})
        
    Returns:
        DataFrame with transaction features per customer
    """
    logging.info("Creating transaction features...")
    
    # Merge transactions with customer accounts to get customer ID
    df = transaction_df.merge(
        customer_account_df[['CUSTOMERACCOUNTID', 'CUSTOMERID']],
        on='CUSTOMERACCOUNTID',
        how='left'
    )
    
    # Convert timestamps
    ref_date = pd.to_datetime(reference_date)
    df['TRANSACTIONINITIATEDTIMESTAMP'] = pd.to_datetime(df['TRANSACTIONINITIATEDTIMESTAMP'])
    
    # Calculate days since transaction
    df['DAYS_SINCE_TRANSACTION'] = (ref_date - df['TRANSACTIONINITIATEDTIMESTAMP']).dt.days
    
    # Initialize feature dictionary
    all_features = []
    
    # Create features for each lookback period
    for period_name, days in lookback_periods.items():
        logging.info(f"Processing {period_name} period ({days} days)...")
        
        # Filter transactions within lookback period
        period_df = df[df['DAYS_SINCE_TRANSACTION'] <= days].copy()
        
        # Aggregate by customer
        period_features = period_df.groupby('CUSTOMERID').agg({
            'TRANSACTIONID': 'count',
            'TRANSACTIONAMOUNT': ['sum', 'mean', 'median', 'std', 'min', 'max']
        }).reset_index()
        
        # Flatten columns
        period_features.columns = [
            'CUSTOMERID',
            f'TXN_COUNT_{period_name.upper()}',
            f'TXN_AMOUNT_SUM_{period_name.upper()}',
            f'TXN_AMOUNT_MEAN_{period_name.upper()}',
            f'TXN_AMOUNT_MEDIAN_{period_name.upper()}',
            f'TXN_AMOUNT_STD_{period_name.upper()}',
            f'TXN_AMOUNT_MIN_{period_name.upper()}',
            f'TXN_AMOUNT_MAX_{period_name.upper()}'
        ]
        
        all_features.append(period_features)
    
    # Merge all period features
    features = all_features[0]
    for period_features in all_features[1:]:
        features = features.merge(period_features, on='CUSTOMERID', how='outer')
    
    # Fill missing values with 0 (customers with no transactions)
    features = features.fillna(0)
    
    # Calculate recency (days since last transaction)
    recency = df.groupby('CUSTOMERID')['DAYS_SINCE_TRANSACTION'].min().reset_index()
    recency.columns = ['CUSTOMERID', 'DAYS_SINCE_LAST_TXN']
    
    features = features.merge(recency, on='CUSTOMERID', how='left')
    features['DAYS_SINCE_LAST_TXN'] = features['DAYS_SINCE_LAST_TXN'].fillna(999999)
    
    logging.info(f"Created {len(features.columns)-1} transaction features for {len(features)} customers")
    
    return features


def create_communication_features(communication_df: pd.DataFrame,
                                  party_df: pd.DataFrame,
                                  customer_df: pd.DataFrame,
                                  reference_date: str,
                                  lookback_days: int = 180) -> pd.DataFrame:
    """
    Create communication-based engagement features.
    
    Args:
        communication_df: Communication table DataFrame
        party_df: Party table DataFrame
        customer_df: Customer table DataFrame
        reference_date: Reference date for lookback
        lookback_days: Number of days to look back
        
    Returns:
        DataFrame with communication features per customer
    """
    logging.info("Creating communication features...")
    
    # Merge communication with party and customer
    df = communication_df.merge(party_df[['PARTYID']], on='PARTYID', how='inner')
    df = df.merge(customer_df[['PARTYID', 'CUSTOMERID']], on='PARTYID', how='left')
    
    # Convert timestamps
    ref_date = pd.to_datetime(reference_date)
    df['COMMUNICATIONSTARTTIMESTAMP'] = pd.to_datetime(df['COMMUNICATIONSTARTTIMESTAMP'])
    
    # Calculate days since communication
    df['DAYS_SINCE_COMM'] = (ref_date - df['COMMUNICATIONSTARTTIMESTAMP']).dt.days
    
    # Filter by lookback period
    df = df[df['DAYS_SINCE_COMM'] <= lookback_days].copy()
    
    # Aggregate by customer
    features = df.groupby('CUSTOMERID').agg({
        'COMMUNICATIONID': 'count',
        'COMMUNICATIONMETHODID': 'nunique',
        'INBOUNDOUTBOUNDCOMMUNICATIONINDICATOR': ['sum', 'mean'],
        'DAYS_SINCE_COMM': 'min'
    }).reset_index()
    
    # Flatten columns
    features.columns = [
        'CUSTOMERID',
        'COMM_COUNT',
        'COMM_UNIQUE_METHODS',
        'COMM_INBOUND_COUNT',
        'COMM_INBOUND_RATIO',
        'DAYS_SINCE_LAST_COMM'
    ]
    
    # Calculate outbound count
    features['COMM_OUTBOUND_COUNT'] = features['COMM_COUNT'] - features['COMM_INBOUND_COUNT']
    
    logging.info(f"Created {len(features.columns)-1} communication features for {len(features)} customers")
    
    return features


def create_document_features(document_df: pd.DataFrame,
                             customer_account_df: pd.DataFrame,
                             reference_date: str) -> pd.DataFrame:
    """
    Create document/KYC compliance features.
    
    Args:
        document_df: Document table DataFrame
        customer_account_df: Customer account table DataFrame
        reference_date: Reference date
        
    Returns:
        DataFrame with document features per customer
    """
    logging.info("Creating document features...")
    
    # Get customer ID from account
    df = document_df.merge(
        customer_account_df[['CUSTOMERACCOUNTID', 'CUSTOMERID']],
        on='CUSTOMERACCOUNTID',
        how='left'
    )
    
    # Convert timestamps
    ref_date = pd.to_datetime(reference_date)
    df['DOCUMENTCREATEDTIMESTAMP'] = pd.to_datetime(df['DOCUMENTCREATEDTIMESTAMP'])
    
    # Calculate document age
    df['DOCUMENT_AGE_DAYS'] = (ref_date - df['DOCUMENTCREATEDTIMESTAMP']).dt.days
    
    # Aggregate by customer
    features = df.groupby('CUSTOMERID').agg({
        'DOCUMENTID': 'count',
        'DOCUMENTTYPEID': 'nunique',
        'DOCUMENT_AGE_DAYS': ['mean', 'min', 'max']
    }).reset_index()
    
    # Flatten columns
    features.columns = [
        'CUSTOMERID',
        'DOCUMENT_COUNT',
        'DOCUMENT_UNIQUE_TYPES',
        'DOCUMENT_AVG_AGE_DAYS',
        'DOCUMENT_MIN_AGE_DAYS',
        'DOCUMENT_MAX_AGE_DAYS'
    ]
    
    logging.info(f"Created {len(features.columns)-1} document features for {len(features)} customers")
    
    return features


def merge_all_features(feature_dfs: List[pd.DataFrame],
                      on_column: str = 'CUSTOMERID') -> pd.DataFrame:
    """
    Merge all feature DataFrames on customer ID.
    
    Args:
        feature_dfs: List of feature DataFrames
        on_column: Column name to merge on
        
    Returns:
        Merged DataFrame with all features
    """
    logging.info(f"Merging {len(feature_dfs)} feature sets...")
    
    # Start with first DataFrame
    merged = feature_dfs[0].copy()
    
    # Merge remaining DataFrames
    for i, df in enumerate(feature_dfs[1:], 1):
        merged = merged.merge(df, on=on_column, how='outer')
        logging.info(f"Merged {i+1}/{len(feature_dfs)} feature sets")
    
    logging.info(f"Final feature set: {len(merged)} customers, {len(merged.columns)-1} features")
    
    return merged


def handle_missing_values(df: pd.DataFrame,
                         numeric_strategy: str = 'median',
                         categorical_strategy: str = 'mode') -> pd.DataFrame:
    """
    Handle missing values in feature DataFrame.
    
    Args:
        df: DataFrame with features
        numeric_strategy: Strategy for numeric columns ('mean', 'median', 'zero')
        categorical_strategy: Strategy for categorical columns ('mode', 'unknown')
        
    Returns:
        DataFrame with imputed values
    """
    logging.info("Handling missing values...")
    
    df = df.copy()
    
    # Numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    if numeric_strategy == 'mean':
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    elif numeric_strategy == 'median':
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    elif numeric_strategy == 'zero':
        df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # Categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    if categorical_strategy == 'mode':
        for col in categorical_cols:
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                df[col] = df[col].fillna(mode_val[0])
    elif categorical_strategy == 'unknown':
        df[categorical_cols] = df[categorical_cols].fillna('UNKNOWN')
    
    logging.info(f"Missing values handled. Remaining nulls: {df.isnull().sum().sum()}")
    
    return df


def create_target_variable(customer_account_df: pd.DataFrame,
                          reference_date: str,
                          prediction_window_days: int = 90,
                          training_ratio: float = 0.80) -> pd.DataFrame:
    """
    Create target variable: next product purchased within prediction window.
    Ensures that approximately training_ratio (default 80%) of customers have targets.
    
    Args:
        customer_account_df: Customer account table DataFrame
        reference_date: Reference date to split historical vs future
        prediction_window_days: Days after reference date to look for next purchase
        training_ratio: Target ratio of customers that should have labels (default 0.80 = 80%)
        
    Returns:
        DataFrame with CUSTOMERID and target (NEXT_PRODUCT_ID)
    """
    logging.info("Creating target variable...")
    
    ref_date = pd.to_datetime(reference_date)
    df = customer_account_df.copy()
    df.head()
    df['ORIGINATIONDATE'] = pd.to_datetime(df['ORIGINATIONDATE'])
    
    # Split into historical (before reference) and future (after reference)
    historical = df[df['ORIGINATIONDATE'] < ref_date]
    future = df[(df['ORIGINATIONDATE'] >= ref_date) & 
                (df['ORIGINATIONDATE'] < ref_date + timedelta(days=prediction_window_days))]
    
    # Get next product for each customer
    future_sorted = future.sort_values(['CUSTOMERID', 'ORIGINATIONDATE'])
    next_product = future_sorted.groupby('CUSTOMERID').first()[['PRODUCTID']].reset_index()
    next_product.columns = ['CUSTOMERID', 'NEXT_PRODUCT_ID']
    
    # Get all customers from historical data
    all_customers = historical[['CUSTOMERID']].drop_duplicates()
    
    # Identify customers with and without next purchases
    customers_with_purchase = next_product['CUSTOMERID'].unique()
    customers_without_purchase = all_customers[~all_customers['CUSTOMERID'].isin(customers_with_purchase)]['CUSTOMERID'].unique()
    
    # Calculate current ratio
    total_customers = len(all_customers)
    n_with_purchase = len(customers_with_purchase)
    n_without_purchase = len(customers_without_purchase)
    
    logging.info(f"Natural distribution: {n_with_purchase}/{total_customers} ({n_with_purchase/total_customers*100:.1f}%) with next purchase")
    
    # Adjust to match training_ratio
    target_with_purchase = int(total_customers * training_ratio)
    target_without_purchase = total_customers - target_with_purchase
    
    # Sample customers to match target distribution
    if n_with_purchase < target_with_purchase:
        # Not enough customers with purchases - use all of them
        logging.warning(f"Only {n_with_purchase} customers have next purchases, but target is {target_with_purchase}")
        logging.warning(f"Using all {n_with_purchase} customers with purchases")
        selected_with_purchase = customers_with_purchase
        # Fill remaining from without purchase
        n_to_add_without = total_customers - n_with_purchase
        selected_without_purchase = np.random.choice(customers_without_purchase, size=min(n_to_add_without, n_without_purchase), replace=False)
    else:
        # Sample from customers with purchases
        selected_with_purchase = np.random.choice(customers_with_purchase, size=target_with_purchase, replace=False)
        # Sample from customers without purchases
        selected_without_purchase = np.random.choice(customers_without_purchase, size=min(target_without_purchase, n_without_purchase), replace=False)
    
    # Combine selected customers
    selected_customers = pd.DataFrame({
        'CUSTOMERID': np.concatenate([selected_with_purchase, selected_without_purchase])
    })
    
    # Merge to get target (will be null for customers who didn't buy)
    target_df = selected_customers.merge(next_product, on='CUSTOMERID', how='left')
    
    # Log final statistics
    final_total = len(target_df)
    final_with_purchase = target_df['NEXT_PRODUCT_ID'].notna().sum()
    final_without_purchase = target_df['NEXT_PRODUCT_ID'].isna().sum()
    
    logging.info(f"Target variable created: {final_total} customers")
    logging.info(f"Customers with next purchase (for training): {final_with_purchase} ({final_with_purchase/final_total*100:.1f}%)")
    logging.info(f"Customers without next purchase (for inference): {final_without_purchase} ({final_without_purchase/final_total*100:.1f}%)")
    
    return target_df
